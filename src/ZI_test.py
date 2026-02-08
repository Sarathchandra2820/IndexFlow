import dataclasses
import random
import numpy as np
import matplotlib.pyplot as plt
from order_book import OrderBook
from agent_logic import Agent, Order, LPLT_agent
from exchange import Exchange


from visualize_book import plot_order_book, plot_interactive_order_book

def initialise_agents(type : str, num : int):
    agents = []
    for i in range(num):
        agent_id = f"agent_{i+1}"
        inventory = random.uniform(100,200)
        #cash = random.uniform(8000,11000)
        cash = inventory*100

        if type == "LPLT":
            agent_obj = LPLT_agent(id=agent_id, inventory=inventory, cash=cash)
            agent_obj.b = random.gauss(0,1)
            agent_obj.spread_bias = random.gauss(0,1)
            agent_obj.imbalance_bias = random.gauss(0,1)
        elif type == "Random":
            agent_obj = Agent(id=agent_id, inventory=inventory, cash=cash)
        agents.append(agent_obj)
    return agents

def random_orders(agent_list : list, exchange : Exchange, num_orders : int):

    mid_price_history = [] 
    spread_history = []
    book_history = [] # For visualization
    sides = ['bid','ask']

    shape_alpha = 1.8 
    tick_size = 0.50
    init_spread = 0.50

    # for _ in range(100):
    for k in range(num_orders):
        agent = random.choice(agent_list)
        side = random.choice(sides)
        # Use last known valid values or defaults to prevent resetting on empty book
        last_mid = 100
        for p in reversed(mid_price_history):
            if p is not None:
                last_mid = p
                break
        
        last_spread = init_spread
        for s in reversed(spread_history):
            if s is not None:
                last_spread = s
                break

        raw_sample = np.random.pareto(shape_alpha)

        if side == "bid":
            price = round((last_mid - last_spread/2) - raw_sample*tick_size, 6)
            price = max(0.01, price)
        elif side == "ask":
            price = round((last_mid + last_spread/2) + raw_sample*tick_size, 6)
            price = max(0.01, price)

        size = random.randint(1,5)

        p = random.uniform(0,1)
        if p < 0.50:
            exchange.process_limit_order(agent, side, price, size)
        elif (0.50 < p < 0.75) and (k > num_orders*0.1):
            q = random.choice(['buy','sell'])
            if q=='buy':
                exchange.process_market_buy(agent, size)
            else:
                exchange.process_market_sell(agent, size)
        elif p > 0.75 and (k > num_orders*0.2):
            if agent.active_orders:
                order_id = random.choice(list(agent.active_orders.keys()))
                exchange.process_cancel_order(agent, order_id)
        # Calculate new metrics after order processing

        # Update History

        spread = exchange.order_book.calculate_spread()
        mid_price = exchange.order_book.calculate_mid_price()
        
        spread_history.append(spread)
        mid_price_history.append(mid_price)

        # Snapshot for visualization (every 10 steps to save memory/speed)
        if k % 10 == 0:
            book_history.append(exchange.order_book.get_snapshot())
    
    # Capture final state
    book_history.append(exchange.order_book.get_snapshot())

    return mid_price_history, spread_history, book_history

    
if __name__ == "__main__":
    num_agents = 10
    agent_list = initialise_agents(num_agents)
    ex = Exchange()
    for agent in agent_list:
        ex.register_agent(agent)
    
    for agent in ex.agents.values():
        print(agent)

    mid_price, spread, book_history = random_orders(agent_list, ex, 1000)
    # print("\nOrder Book after random orders:")
    # print(ex.order_book)

    print("Visualizing Final Order Book...")
    plot_interactive_order_book(book_history)

    plt.plot(mid_price)
    plt.title("Mid Price Evolution")
    plt.xlabel("Number of Orders")
    plt.ylabel("Mid Price")
    plt.show()

    plt.plot(spread[20:])
    plt.title("Spread Evolution")
    plt.xlabel("Number of Orders")
    plt.ylabel("Spread")
    plt.show()

    # Visualize Order Book
    print("\nVisualizing Final Order Book...")
    from visualize_book import plot_order_book
    plot_order_book(ex.order_book)

