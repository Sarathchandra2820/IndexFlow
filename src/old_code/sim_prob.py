import dataclasses
import numpy as np
import matplotlib.pyplot as plt
import random
from data_coll.order_book_old import OrderBook1



def market_initialisation(order_book: OrderBook1, initial_price: float, spread: float, length : int):
    # Initialize the order book with limit orders around the initial price
    

    # 1. Define the shape parameter (alpha).
    # Crypto is volatile, so tails are heavy. Try 1.5 to 2.0.
    shape_alpha = 1.8 
    tick_size = 0.50

    # 2. Sample from Pareto distribution (numpy returns x such that x >= 0)
    # 'size' is the number of orders you are simulating
    raw_sample = np.random.pareto(shape_alpha,size=length)

    for samples in raw_sample:

        un_r_bid_price = (initial_price-spread/2) - samples*tick_size
        bid_price = np.round(un_r_bid_price,decimals=4)
        bid_size  = random.randint(1,10)
        order_book.add_limit_order("bid", bid_price, bid_size)
        
        
        un_r_ask_price = (initial_price+spread/2) + samples*tick_size
        ask_price = np.round(un_r_ask_price,decimals=4)
        ask_size  = random.randint(1,10)
        order_book.add_limit_order("ask", ask_price, ask_size)

    



def limit_order_prob(side: str, mid_price : float, spread : float) -> list[2]:
    
    if side not in ["bid","ask"]:
        raise ValueError("Side must be either 'bid' or 'ask'")
    
    # 1. Define the shape parameter (alpha).
    # Crypto is volatile, so tails are heavy. Try 1.5 to 2.0.
    shape_alpha = 1.8 
    tick_size = 0.50

    # 2. Sample from Pareto distribution (numpy returns x such that x >= 0)
    # 'size' is the number of orders you are simulating
    raw_sample = np.round(np.random.pareto(shape_alpha), decimals=4)

    
    if side == "bid":
        un_r_bid_price = (mid_price-spread/2) - raw_sample*tick_size
        bid_price = np.round(un_r_bid_price,decimals=4)
        bid_size  = random.randint(1,10)
        return [bid_price, bid_size]
        
    elif side == "ask":
        un_r_ask_price = (mid_price+spread/2) + raw_sample*tick_size
        ask_price = np.round(un_r_ask_price,decimals=4)
        ask_size  = random.randint(1,10)
        return [ask_price, ask_size]
    
def cancel_order_prob(side: str, order_book: OrderBook1) -> list[2]:  #We randomely cancel the orders 
    
    if side not in ["bid","ask"]:
        raise ValueError("Side must be either 'bid' or 'ask'")
    
    if side == "bid":
        if not order_book.bid_dic:
            return None
        price = random.choice(list(order_book.bid_dic.keys()))
        qty = int(order_book.bid_dic[price])
        size = random.randint(1, qty)

        #order_book.cancel_order("bid", price, size)

        return [price, size]
        
    elif side == "ask":
        if not order_book.ask_dic:
            return None
        price = random.choice(list(order_book.ask_dic.keys()))
        qty = int(order_book.ask_dic[price])
        size = random.randint(1, order_book.ask_dic[price])

        #order_book.cancel_order("ask", price, size)

        return [price, size]
    
def random_market_order_size(max_size: float) -> float:
    qnt =  random.randint(1, max_size)
    # if side == "bid":
    #     order_book.market_buy(qnt)
    # elif side == "ask":
    #     order_book.market_sell(qnt)
    return qnt


    
    
@dataclasses.dataclass 
        
class Simtrades:
    
    order_book : OrderBook1 = None
    history : dict = None
    mid_price_history : list = dataclasses.field(default_factory=list)
    spread_history : list = dataclasses.field(default_factory=list)
    imbalance_history : list = dataclasses.field(default_factory=list)

    def __post_init__(self):
        self.order_book = OrderBook1()
        self.history = {}
        self.mid_price_history = []

    def start_process(self, num_time_steps: int, initial_price: float, init_spread : float, p_limit: float, p_cancel: float, p_market: float, store_history: bool = True):

        if abs((p_limit + p_cancel + p_market)- 1.0) > 1e-2:
    
            raise ValueError("Probabilities must sum to 1")
        

        for i in range(num_time_steps):

            if i == 0: 
                mid_price = initial_price
                spread = init_spread
                market_initialisation(self.order_book, initial_price, spread, length=100)
                mid_price = self.order_book.update_mid_price()
                print(f"Initial mid price: {mid_price}")
                print(f"Initial spread: {spread}")
                spread = self.order_book.update_spread()
                print(f"Initial spread: {spread}")
                self.mid_price_history.append(mid_price)
                self.spread_history.append(spread)
                if store_history:
                    self.history[i] = {
                        "order_book": {
                            "bids": self.order_book.bid_dic.copy(),
                            "asks": self.order_book.ask_dic.copy()
                        },
                        "mid_price": mid_price
                    }
                

            #number of orders in the orderbook 


            
            p = random.uniform(0,1)

            if p < p_limit:
                # Add limit order
                side = random.choice(["bid","ask"])

                # print(f"Before cancel {mid_price}")
                # print(f"best_price {self.order_book.best_price()}")

                
                #logic for the price and size to be drawn out of some distribution

                price, size = limit_order_prob(side, mid_price, spread= spread)
                self.order_book.add_limit_order(side, price, size)
            

            elif p < p_limit + p_cancel:
                # Cancel order
                side = random.choice(["bid","ask"])

                # print(f"Before cancel {mid_price}")
                # print(f"best_price {self.order_book.best_price()}")
                
                #logic for the price and size to be drawn out of some distribution

                price, size = cancel_order_prob(side, self.order_book)
                if price==None:
                    continue
                self.order_book.cancel_order(side, price, size)

            else:
                # Market order
                side = random.choice(["buy","sell"])

                #logic for the price and size to be drawn out of some distribution

                max_size = 10.0
                size = random_market_order_size(max_size)
                self.order_book.market_order(side, size)
            
            # Update mid price and spread

            mid_price = self.order_book.update_mid_price()
            spread = self.order_book.update_spread()
            self.mid_price_history.append(mid_price)
            self.spread_history.append(spread)
            self.imbalance_history.append(self.order_book.calculate_imbalance())
           
            if store_history:
                self.history[i] = {
                    "order_book": {
                        "bids": self.order_book.bid_dic.copy(),
                        "asks": self.order_book.ask_dic.copy()
                    },
                    "mid_price": mid_price
                }
        return self.history, self.mid_price_history,self.spread_history
    

if __name__ == "__main__":

    sim = Simtrades()
    history, mid_price_history, spread_histroy = sim.start_process(num_time_steps=1000, initial_price=100.0, init_spread=2.0, p_limit=0.4, p_cancel=0.2, p_market=0.4, store_history=True)

    #plot mid price history
    plt.plot(mid_price_history)
    plt.xlabel("Time step")
    plt.ylabel("Mid Price")
    plt.title("Mid Price History")
    plt.show()

    plt.plot(spread_histroy)
    plt.xlabel("Time step")
    plt.ylabel("spread")
    plt.title("Mid Price History")
    plt.show()

    plt.plot(sim.imbalance_history)
    plt.xlabel("Time step")
    plt.ylabel("Imbalance")
    plt.title("Imbalance History")
    plt.show()

    # # 1. Define the shape parameter (alpha).
    # # Crypto is volatile, so tails are heavy. Try 1.5 to 2.0.
    # shape_alpha = 1.8 
    # price_mid = 100.0  # Center around this mid-price
    # spread = 2.0 #a static quantity for now
    # tick_size = 0.50

    # # 2. Sample from Pareto distribution (numpy returns x such that x >= 0)
    # # 'size' is the number of orders you are simulating
    # raw_samples = np.random.pareto(shape_alpha, size=1000)

    # bid_prices = (price_mid-spread/2) - raw_samples*tick_size
    # ask_prices = (price_mid+spread/2) + raw_samples*tick_size



    # #plot the histogram
    # plt.hist(bid_prices, bins=50, density=True, alpha=0.6) 
    # plt.hist(ask_prices, bins=50, density=True, alpha=0.6)
    # plt.show()
                


            

                