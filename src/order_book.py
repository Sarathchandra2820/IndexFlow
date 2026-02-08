import dataclasses
import time
from collections import deque
from agent_logic import Order


@dataclasses.dataclass
class OrderBook:

    bid_dic : dict = dataclasses.field(default_factory=dict)
    ask_dic : dict = dataclasses.field(default_factory=dict)
    counter : int = 0


        

    def add_order(self, side: str, price: float, order : Order):
         
        self.counter += 1
        order.order_id = f"order_number_{self.counter}"

        if side == "bid":
            if price in self.bid_dic:
                
                self.bid_dic[price].append(order)
            else:
                q = deque()
                q.append(order)
                self.bid_dic[price] = q

        elif side == "ask":
            if price in self.ask_dic:
                self.ask_dic[price].append(order)
            else:
                q = deque()
                q.append(order)
                self.ask_dic[price] = q
    

    def cancel_order(self, side: str, price: float, order_id: str):
        found = False
        if side == "bid":
            if price in self.bid_dic:
                orders_queue = self.bid_dic[price]
                # Rebuild deque without the matching order
                new_queue = deque()
                for ords in orders_queue:
                    if ords.order_id != order_id:
                        new_queue.append(ords)
                    else:
                        found = True
                self.bid_dic[price] = new_queue
                if not new_queue:
                    del self.bid_dic[price]
                if not found:
                    pass # Order might have been executed already
            else:
                pass # Price level cleared

        elif side == "ask":
            if price in self.ask_dic:
                orders_queue = self.ask_dic[price]
                # Rebuild deque without the matching order
                new_queue = deque()
                for ords in orders_queue:
                    if ords.order_id != order_id:
                        new_queue.append(ords)
                    else:
                        found = True
                self.ask_dic[price] = new_queue
                if not new_queue:
                    del self.ask_dic[price]

                if not found:
                    pass # Order executed
            else:
                pass # Price level cleared
            
    def get_best_bid(self):

        if not self.bid_dic:
            return None 
        best_bid_price = max(self.bid_dic.keys())

        return best_bid_price
    
    def get_best_ask(self):
        if not self.ask_dic:
            return None
        best_ask_price = min(self.ask_dic.keys())
        return best_ask_price
    


            
    def market_buy(self, size : int, trade_log = None):

        if trade_log is None:
            trade_log = []
        best_ask_price = self.get_best_ask()

        if best_ask_price is None:
            raise ValueError("No asks in the order book")
        
        elif best_ask_price in self.ask_dic:
            order_at_best = self.ask_dic[best_ask_price][0]
            ord_size = order_at_best.size
            seller_id = order_at_best.agent_id
            if ord_size > size:
                order_at_best.size -= size
                trade_log.append((seller_id, best_ask_price, size, time.time()))


            elif ord_size == size:
                self.ask_dic[best_ask_price].remove(order_at_best)
                trade_log.append((seller_id, best_ask_price, size, time.time()))

                # CLEANUP: If that was the last order, delete the price level
                if not self.ask_dic[best_ask_price]:
                    del self.ask_dic[best_ask_price]

            elif ord_size < size:
                self.ask_dic[best_ask_price].remove(order_at_best)
                trade_log.append((seller_id, best_ask_price, ord_size, time.time()))

                # CLEANUP: If that was the last order, delete the price level
                if not self.ask_dic[best_ask_price]:
                    del self.ask_dic[best_ask_price]

                new_size = size - ord_size
                self.market_buy(new_size,trade_log=trade_log)
                          
                
            else:
                raise ValueError("Not enough size at best ask to fulfill market order")
            
        return trade_log
        
    def market_sell(self,size : int, trade_log = None):

        if trade_log is None:
            trade_log = []
        best_bid_price = self.get_best_bid()
        
        if best_bid_price is None:
            raise ValueError("No bids in the order book")
        
        elif best_bid_price in self.bid_dic:
            order_at_best = self.bid_dic[best_bid_price][0]
            ord_size = order_at_best.size
            buyer_id = order_at_best.agent_id
            if ord_size > size:
                order_at_best.size -= size
                trade_log.append((buyer_id, best_bid_price, size, time.time()))
            elif ord_size == size:
                self.bid_dic[best_bid_price].remove(order_at_best)
                trade_log.append((buyer_id, best_bid_price, size, time.time()))

                if not self.bid_dic[best_bid_price]:
                    del self.bid_dic[best_bid_price]
            elif ord_size < size:
                self.bid_dic[best_bid_price].remove(order_at_best)
                trade_log.append((buyer_id, best_bid_price, ord_size, time.time()))

                if not self.bid_dic[best_bid_price]:
                    del self.bid_dic[best_bid_price]


                new_size = size - ord_size
                self.market_sell(new_size,trade_log=trade_log)
                          
            else:
                raise ValueError("Not enough size at best bid to fulfill market order")
        return trade_log

    def match_limit_order(self, side: str, limit_price: float, size: int):
        """
        Matches a limit order against the book. 
        Returns (trade_log, remaining_size)
        """
        trade_log = []
        remaining_size = size
        
        if side == "bid":
            # Buying: Match against Asks (lowest first)
            while remaining_size > 0:
                best_ask = self.get_best_ask()
                
                # Stop if no asks or best ask is too expensive
                if best_ask is None or best_ask > limit_price:
                    break
                
                # We can match!
                orders_at_price = self.ask_dic[best_ask]
                
                while orders_at_price and remaining_size > 0:
                    order_match = orders_at_price[0] # FIFO
                    match_qty = min(remaining_size, order_match.size)
                    
                    # Record Trade
                    # (Maker_ID, Price, Qty, Time)
                    trade_log.append((order_match.agent_id, best_ask, match_qty, time.time()))
                    
                    # Update sizes
                    remaining_size -= match_qty
                    order_match.size -= match_qty
                    
                    if order_match.size == 0:
                        orders_at_price.popleft() # Remove full filled order
                        
                # Cleanup price level if empty
                if not orders_at_price:
                    del self.ask_dic[best_ask]

        elif side == "ask":
            # Selling: Match against Bids (highest first)
            while remaining_size > 0:
                best_bid = self.get_best_bid()
                
                # Stop if no bids or best bid is too low
                if best_bid is None or best_bid < limit_price:
                    break
                
                # We can match!
                orders_at_price = self.bid_dic[best_bid]
                
                while orders_at_price and remaining_size > 0:
                    order_match = orders_at_price[0] # FIFO
                    match_qty = min(remaining_size, order_match.size)
                    
                    # Record Trade
                    # (Maker_ID, Price, Qty, Time)
                    trade_log.append((order_match.agent_id, best_bid, match_qty, time.time()))
                    
                    # Update sizes
                    remaining_size -= match_qty
                    order_match.size -= match_qty
                    
                    if order_match.size == 0:
                        orders_at_price.popleft() # Remove full filled order
                        
                # Cleanup price level if empty
                if not orders_at_price:
                    del self.bid_dic[best_bid]
                    
        return trade_log, remaining_size
    
    def calculate_imbalance(self):
        total_bid_size = sum([sum([order.size for order in orders]) for orders in self.bid_dic.values()])
        total_ask_size = sum([sum([order.size for order in orders]) for orders in self.ask_dic.values()])

        if total_bid_size + total_ask_size == 0:
            return 0.0  # Avoid division by zero

        imbalance = (total_bid_size - total_ask_size) / (total_bid_size + total_ask_size)
        return imbalance
    
    def calculate_spread(self):
        best_bid = self.get_best_bid()
        best_ask = self.get_best_ask()

        if best_bid is None or best_ask is None:
            return None  # Spread is undefined if either side is empty

        spread = best_ask - best_bid
        return spread
    
    def calculate_mid_price(self):
        best_bid = self.get_best_bid()
        best_ask = self.get_best_ask()

        if best_bid is None or best_ask is None:
            return None # Mid-price is undefined if either side is empty

        mid_price = (best_bid + best_ask) / 2
        return mid_price
    
    
    def get_book_stats(self):
        mid_price = self.calculate_mid_price()
        spread = self.calculate_spread()
        imbalance = self.calculate_imbalance()
        return mid_price, spread, imbalance

    
    def get_snapshot(self):
        """
        Returns a snapshot of the book for visualization.
        bids: [(price, size), ...] sorted highest price first
        asks: [(price, size), ...] sorted lowest price first
        """
        bids = []
        for price in sorted(self.bid_dic.keys(), reverse=True):
            total_size = sum(order.size for order in self.bid_dic[price])
            bids.append((price, total_size))
            
        asks = []
        for price in sorted(self.ask_dic.keys()):
            total_size = sum(order.size for order in self.ask_dic[price])
            asks.append((price, total_size))
            
        return bids, asks

#     #test market_buy 

#     ob = OrderBook()
#     agent_id = "agent_1"
#     order1 = Order(agent_id=agent_id, size=10)
#     order2 = Order(agent_id=agent_id, size=15)
#     order3 = Order(agent_id=agent_id, size=5)   

#     ob.add_order("ask", 101.0, order1)
#     ob.add_order("ask", 102.0, order2)
#     ob.add_order("ask", 101.0, order3)

#     trade_log = ob.market_buy(20, trade_log=[])

#     print(trade_log)