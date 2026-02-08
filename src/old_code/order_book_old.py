import dataclasses


@dataclasses.dataclass

class OrderBook1:

    bid_dic : dict = None
    ask_dic : dict = None




    def add_limit_order(self, side: str, price: float, size: int):
        if side == "bid":
            if price in self.bid_dic:
                self.bid_dic[price] += size
            else:
                self.bid_dic[price] = size
        elif side == "ask":
            if price in self.ask_dic:
                self.ask_dic[price] += size
            else:
                self.ask_dic[price] = size
        else:
            raise ValueError("Side must be either 'bid' or 'ask'")
    
    def cancel_order(self, side: str, price: float, size: int):
        if side == "bid":
            if price in self.bid_dic:
                self.bid_dic[price] -= size

                if self.bid_dic[price] == 0:
                    self.bid_dic.pop(price,None)
                elif self.bid_dic[price] < 0:
                    raise ValueError("cannot cancel more orders than present")

        if side == "ask":        
            if price in self.ask_dic:
                self.ask_dic[price] -= size
        
                if self.ask_dic[price] == 0:
                    self.ask_dic.pop(price,None)
                elif self.ask_dic[price]< 0:
                    raise ValueError("cannot cancel more orders than present")


    def get_best_bid(self):
        if not self.bid_dic:
            return None, None
        best_bid_price = max(self.bid_dic.keys())
        best_bid_size = self.bid_dic[best_bid_price]
        return best_bid_price, best_bid_size
    
    def get_best_ask(self):
        if not self.ask_dic:
            return None, None
        best_ask_price = min(self.ask_dic.keys())
        best_ask_size = self.ask_dic[best_ask_price]
        return best_ask_price, best_ask_size

    def best_price(self):
        best_bid_price, _ = self.get_best_bid()
        best_ask_price, _ = self.get_best_ask()
        return best_bid_price, best_ask_price
    
    def best_bid_price(self):
        best_bid_price, _ = self.get_best_bid()
        return best_bid_price
    

    def market_buy(self,size : int):

        best_ask_price, best_ask_size = self.get_best_ask()

        if best_ask_size is None:
            return None
        else:

            if best_ask_size == size:
                self.ask_dic.pop(best_ask_price,None)

            elif best_ask_size > size:
                    #modify the size of the best_ask 
                self.ask_dic[best_ask_price] -= size  #we are at the first price level

            elif best_ask_size < size:
                self.ask_dic.pop(best_ask_price,None)
                new_size = size - best_ask_size

                self.market_buy(new_size)
            else:
                raise ValueError("Unexpected error in market buy")
     
    
    def market_sell(self,size : int):
        best_bid_price, best_bid_size = self.get_best_bid()
        
        if best_bid_size is None:
            return None
        else:

            if best_bid_size == size:
                self.bid_dic.pop(best_bid_price,None)

            elif best_bid_size > size:
                    #modify the size of the best_bid 
                self.bid_dic[best_bid_price] -= size  #we are at the first price level

            elif best_bid_size < size:
                self.bid_dic.pop(best_bid_price,None)
                new_size = size - best_bid_size

                self.market_sell(new_size)
            else:
                raise ValueError("Unexpected error in market sell")
            
    def market_order(self, side: str, size: int):
        if side == "buy":
            self.market_buy(size)
        elif side == "sell":
            self.market_sell(size)
        else:
            raise ValueError("Side must be either 'bid' or 'ask'")
            
    def update_mid_price(self):
        best_bid_price, _ = self.get_best_bid()
        best_ask_price, _ = self.get_best_ask()

        if best_bid_price is None or best_ask_price is None:
            return None
        else:
            mid_price = (best_bid_price + best_ask_price) / 2
            return mid_price
    
    def update_spread(self):

        best_bid_price, best_ask_price = self.best_price()
        spread = best_ask_price - best_bid_price 

        return spread
    
    def calculate_imbalance(self):
        total_bid_size = sum(self.bid_dic.values())
        total_ask_size = sum(self.ask_dic.values())

        if (total_bid_size + total_ask_size) == 0:
            return 0.0
        else:
            imbalance = (total_bid_size - total_ask_size) / (total_bid_size + total_ask_size)
            return imbalance



    def __str__(self):
        for price in sorted(self.bid_dic.keys(), reverse=True):
            print(f"Bid - Price: {price}, Size: {self.bid_dic[price]}")
        for price in sorted(self.ask_dic.keys()):
            print(f"Ask - Price: {price}, Size: {self.ask_dic[price]}")

        print(f"best bid: {self.get_best_bid()}")
        print(f"best ask: {self.get_best_ask()}")
        print(f"mid price: {self.update_mid_price()}")
        return ""



if __name__ == "__main__":
    ob = OrderBook1()

    ob.add_limit_order("bid", 100.0, 5.0)
    ob.add_limit_order("bid", 101.0, 3.0)
    ob.add_limit_order("ask", 102.0, 4.0)
    ob.add_limit_order("ask", 103.0, 2.0)
    ob.add_limit_order("bid", 100.0, 2.0)
    ob.add_limit_order("ask", 102.0, 1.0)
    print(ob)
    

    # ob.cancel_order("bid", 100.0, 2.0)
    # ob.cancel_order("ask", 103.0, 1.0)
    ob.market_buy(4.0)
    ob.market_sell(5.0)

    print(ob)
    

    

