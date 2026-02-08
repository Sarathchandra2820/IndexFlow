import dataclasses
import time
import numpy as np
import math
from order_book import OrderBook
from ZI_test import initialise_agents


def sigmoid(x):
    return 1 / (1 + math.exp(-x))

@dataclasses.dataclass

class Agent:
    id: str = None
    inventory: float = 0.0
    cash: float = 0.0
    active_orders: dict = dataclasses.field(default_factory=dict)

    def __str__(self):
        return f"Agent(id={self.id}, inventory={self.inventory}, cash={self.cash}, active_orders={self.active_orders})"


class LPLT_agent(Agent):
    aggression : float = 0.0
    b : float = 0.0
    spread_bias : float = 0.0
    imbalance_bias : float = 0.0


    def choose_action(self, spread: float):
        w = sigmoid(self.b + self.spread_bias * spread)
        p = np.random.uniform(0,1)

        #Missing is an inventory constraint
        if p < w:
            return 'LP'
        else:
            return 'LT'

    def choose_side(self,imbalance: float):
        #we choose the buy or sell side based on the imbalance
        w = sigmoid(self.imbalance_bias * imbalance)

        p = np.random.uniform(0,1)
        if p < w:
            return 'buy'
        else:
            return 'sell'

    def set_price(self, mid_price: float, spread: float):
        if self.choose_action(spread) == 'LP':
            sample = np.random.pareto(1.8)
            if self.choose_side(spread) == 'buy':
                price = np.round(mid_price + spread/2 + sample*0.5, 6)
                if price > self.cash*self.aggression:
                    return self.set_price(mid_price, spread)
                else:
                    return price
            else:
                price = np.round(mid_price - spread/2 - sample*0.5, 6)
                if price < 0:
                    return self.set_price(mid_price, spread)
                else:
                    return price
        else:
            return None

    def set_size(self):

        

        



    
        








@dataclasses.dataclass
class Order:
    agent_id : str = None
    order_id : str = None
    #agent_active_orders : Agent.active_orders = None
    size : int = 0
    time_stamp : float = dataclasses.field(default_factory=time.time)


    def __str__(self):
        return f"Order(agent_id={self.agent_id}, order_id={self.order_id} size={self.size}, time_stamp={self.time_stamp})"
    







if __name__ == "__main__":

    agents = initialise_agents(type="LPLT", num=10)


 

    

    

    print(order1)

