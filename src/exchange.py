import dataclasses
from order_book import OrderBook
from agent_logic import Agent, Order




@dataclasses.dataclass
class Exchange:
    

    def __init__(self):
        self.order_book = OrderBook()
        self.agents = {}  # The Phonebook: {agent_id: Agent_Object}

    def register_agent(self, agent: Agent):
        """Add an agent to the exchange so we can pay them later."""
        self.agents[agent.id] = agent
        print(f"Agent {agent.id} registered.")

    def process_limit_order(self, agent: Agent, side: str, price: float, size: int):
        # 1. Validation Checks & Initial Deduction
        # We deduct the FULL worst-case cost/inventory upfront. 
        # We will refund any savings if we match at a better price.
        if side == "bid":
            if agent.cash < price * size:
                print(f'Insufficient cash for bid order. Needed {price*size}, has {agent.cash}')
                return
            agent.cash -= price * size
            
        elif side == "ask":
            if agent.inventory < size:
                print('Insufficient inventory for ask order.')
                return
            agent.inventory -= size
        
        # 2. Match against Order Book
        trades, remaining_size = self.order_book.match_limit_order(side, price, size)
        
        # 3. Process Trades (Settlement)
        total_quantity_traded = size - remaining_size
        total_cost_or_revenue = 0.0
        
        for trade in trades:
            maker_id, trade_price, qty, _ = trade
            trade_value = trade_price * qty
            total_cost_or_revenue += trade_value
            
            # Settle with the Maker (The Passive Party)
            if maker_id in self.agents:
                maker = self.agents[maker_id]
                if side == "bid":
                    # We are Buying, Maker was Selling (Ask).
                    # Maker delivered 'qty' (already locked in book).
                    # Maker receives Cash.
                    maker.cash += trade_value
                    # We also need to remove this from Maker's active_orders if completely filled?
                    # The OrderBook handles removal from book, but Agent logic needs to know.
                    # Currently Agent.active_orders tracks [side, price, size]. WIll address this if needed.
                elif side == "ask":
                    # We are Selling, Maker was Buying (Bid).
                    # Maker paid cash (already locked).
                    # Maker receives Inventory.
                    maker.inventory += qty
            else:
                print(f"CRITICAL: Maker {maker_id} not found.")

        # 4. Settle with Taker (The Active Party - 'agent')
        if side == "bid":
            # We bought 'total_quantity_traded'
            agent.inventory += total_quantity_traded
            
            # Refund difference: We paid 'price * total_quantity_traded' upfront for this portion.
            # Actual cost was 'total_cost_or_revenue'.
            # refund = (price * traded) - actual_cost
            cost_for_traded_portion = price * total_quantity_traded
            refund = cost_for_traded_portion - total_cost_or_revenue
            agent.cash += refund
            
            if total_quantity_traded > 0:
                print(f"Trade: {agent.id} bought {total_quantity_traded} @ avg {total_cost_or_revenue/total_quantity_traded:.2f}")

        elif side == "ask":
            # We sold 'total_quantity_traded'
            # We gain Cash = total_cost_or_revenue
            agent.cash += total_cost_or_revenue
            
            if total_quantity_traded > 0:
                print(f"Trade: {agent.id} sold {total_quantity_traded} @ avg {total_cost_or_revenue/total_quantity_traded:.2f}")

        # 5. Add Remainder to Book (if any)
        if remaining_size > 0:
            order_obj = Order(agent_id=agent.id, size=remaining_size)
            self.order_book.add_order(side, price, order_obj)
            
            # 6. Update Agent Record (for the passive remainder)
            # Only track the portion that sits in the book
            agent.active_orders[order_obj.order_id] = [side, price, remaining_size]

    def process_cancel_order(self, agent: Agent, order_id: str):
        if order_id not in agent.active_orders:
            print(f"Order ID {order_id} not found in agent {agent.id}'s active orders.")
            return
        
        side, price, size = agent.active_orders[order_id]
        
        # Cancel from Order Book
        self.order_book.cancel_order(side, price, order_id)
        
        # Refund Agent
        if side == "bid":
            agent.cash += price * size
        elif side == "ask":
            agent.inventory += size
        
        # Remove from Agent's Active Orders
        del agent.active_orders[order_id]

    def process_market_buy(self, buyer: Agent, size: int):

        #check if the buyer has enough cash to buy the maximum possible at the worst price
        best_ask = self.order_book.get_best_ask()
        if best_ask is None:
            print("No asks in the book to buy from.")
            return
        worst_case_cost = 1.5*best_ask * size
        if buyer.cash < worst_case_cost:
            print(f"Buyer {buyer.id} has insufficient cash ({buyer.cash}) for market buy of size {size} (worst case cost: {worst_case_cost}).")
            return
        # 1. EXECUTE
        trade_log = self.order_book.market_buy(size)
        
        total_cost = 0.0
        total_quantity_received = 0.0

        # 2. SETTLE
        for trade in trade_log:
            seller_id, price, qty_traded, _  = trade
            
            trade_value = price * qty_traded
            
            # Pay the Seller
            if seller_id in self.agents:
                seller_obj = self.agents[seller_id]
                seller_obj.cash += trade_value
            else:
                print(f"CRITICAL ERROR: Seller {seller_id} not found in registry! Money lost.")
            
            total_cost += trade_value
            total_quantity_received += qty_traded

        # 3. CHARGE THE BUYER
        if buyer.cash >= total_cost:
            buyer.cash -= total_cost
            buyer.inventory += total_quantity_received
            print(f"Trade: {buyer.id} bought {total_quantity_received} @ avg ${total_cost/total_quantity_received if total_quantity_received else 0:.2f}")
        else:
            print(f"WARNING: Buyer {buyer.id} went into debt by ${total_cost - buyer.cash}")
            
            buyer.cash -= total_cost
            buyer.inventory += total_quantity_received

        return trade_log
    
    def process_market_sell(self, seller: Agent, size: int):

        #check if the seller has enough inventory to sell
        best_bid = self.order_book.get_best_bid()
        if best_bid is None:
            print("No bids in the book to sell to.")
            return

        if seller.inventory < 1.5*size: # simplistic check
            print(f"Seller {seller.id} has insufficient inventory ({seller.inventory}) for market sell of size {size}.")
            return
        # 1. EXECUTE
        trade_log = self.order_book.market_sell(size)
        
        total_revenue = 0.0
        total_quantity_sold = 0.0

        # 2. SETTLE
        for trade in trade_log:
            buyer_id, price, qty_traded, _  = trade
            
            trade_value = price * qty_traded
            
            # Pay the seller
            if buyer_id in self.agents:
                buyer_obj = self.agents[buyer_id]
                buyer_obj.inventory += qty_traded
            else:
                print(f"CRITICAL ERROR: Buyer {buyer_id} not found in registry! Inventory lost.")
            
            total_revenue += trade_value
            total_quantity_sold += qty_traded

        # 3. CREDIT THE SELLER
        seller.cash += total_revenue
        seller.inventory -= total_quantity_sold
        print(f"Trade: {seller.id} sold {total_quantity_sold} @ avg ${total_revenue/total_quantity_sold if total_quantity_sold else 0:.2f}")

        return trade_log


# def initialise_agents(num_agents : int):
    


# --- SIMULATION SCRIPT ---
if __name__ == "__main__":
    print("--- STARTING SIMULATION ---\n")
    
    # 1. Setup Exchange
    ex = Exchange()
    
    # 2. Create Agents
    alice = Agent(id="Alice", cash=1000, inventory=10)
    bob = Agent(id="Bob", cash=500, inventory=20)
    charlie = Agent(id="Charlie", cash=2000, inventory=0) # The Buyer
    
    # 3. Register Agents
    ex.register_agent(alice)
    ex.register_agent(bob)
    ex.register_agent(charlie)
    print("")

    # 4. Alice and Bob place orders (Liquidity)
    ex.process_limit_order(alice, "ask", 100.0, 5)   # Alice sells 5 @ $100
    ex.process_limit_order(bob, "bid", 98.0, 5)      # Bob bids 5 @ $98
    print("")

    # 5. Charlie executes a MARKET BUY (Takes Liquidity)
    # He wants 7 units. He should get 5 from Alice ($100) and 2 from Bob ($102)
    ex.process_market_buy(charlie, 7)
    
    print("\n--- FINAL BALANCES ---")
    print(alice)
    print(bob)
    print(charlie)