import matplotlib.pyplot as plt
import numpy as np

def plot_order_book(order_book):
    """
    Plots the Limit Order Book as a Depth Chart.
    """
    bids, asks = order_book.get_snapshot()
    
    if not bids and not asks:
        print("Order Book is Empty!")
        return

    # Process Bids
    bid_prices = []
    bid_cum_vol = []
    cumulative = 0
    # Bids are sorted descending (Best bid first).
    # For depth chart, we usually plot from highest bid downwards.
    for price, size in bids:
        bid_prices.append(price)
        cumulative += size
        bid_cum_vol.append(cumulative)
        
    # Process Asks
    ask_prices = []
    ask_cum_vol = []
    cumulative = 0
    # Asks are sorted ascending (Best ask first).
    # For depth chart, we usually plot from lowest ask upwards.
    for price, size in asks:
        ask_prices.append(price)
        cumulative += size
        ask_cum_vol.append(cumulative)

    plt.figure(figsize=(10, 6))
    
    # Plot Bids (Green)
    if bid_prices:
        plt.step(bid_prices, bid_cum_vol, color='green', label='Bids', where='pre')
        plt.fill_between(bid_prices, bid_cum_vol, step="pre", color='green', alpha=0.3)
        
    # Plot Asks (Red)
    if ask_prices:
        plt.step(ask_prices, ask_cum_vol, color='red', label='Asks', where='post')
        plt.fill_between(ask_prices, ask_cum_vol, step="post", color='red', alpha=0.3)

    plt.xlabel("Price")
    plt.ylabel("Cumulative Volume")
    plt.title("Order Book Depth Chart")
    plt.legend()
    plt.grid(True, linestyle='--', alpha=0.6)
    plt.show()

def plot_interactive_order_book(history):
    """
    Plots the Order Book evolution with a slider.
    history: list of (bids, asks) tuples
    """
    from matplotlib.widgets import Slider

    if not history:
        print("No history to plot.")
        return

    fig, ax = plt.subplots(figsize=(10, 7))
    plt.subplots_adjust(bottom=0.25)
    
    # Initial Plot (Start at last step to show final state initially, or first)
    # Let's start at 0
    bids, asks = history[0]
    
    # We need to initialize the plot lines. 
    # Use step plot.
    bid_line, = ax.step([], [], color='green', label='Bids', where='pre')
    ask_line, = ax.step([], [], color='red', label='Asks', where='post')
    
    # Areas for fill_between (need to be cleared and redrawn)
    # To handle fills efficiently, we can remove and re-add them
    bid_fill = None
    ask_fill = None

    ax.set_xlabel("Price")
    ax.set_ylabel("Cumulative Volume")
    ax.legend()
    ax.grid(True, linestyle='--', alpha=0.6)
    
    # Calculate global limits for stable axes so the graph doesn't jump
    all_prices = []
    all_vols = []
    
    # Subsample history for limit calc to save time if history is huge
    sample_rate = 1 if len(history) < 100 else len(history)//100
    
    for b, a in history[::sample_rate]:
        if b:
            all_prices.extend([p for p,s in b])
            vol = sum(s for p,s in b)
            all_vols.append(vol)
        if a:
            all_prices.extend([p for p,s in a])
            vol = sum(s for p,s in a)
            all_vols.append(vol)
            
    if all_prices and all_vols:
        # Padded limits
        ax.set_xlim(min(all_prices)*0.95, max(all_prices)*1.05)
        ax.set_ylim(0, max(all_vols)*1.1)

    def update(val):
        nonlocal bid_fill, ask_fill
        step = int(val)
        if step >= len(history): step = len(history) - 1
            
        bids, asks = history[step]
        
        # Process Bids
        bid_prices = []
        bid_cum_vol = []
        cumulative = 0
        # bids are sorted desc (highest first)
        # for depth chart usually we want to see them accumulating away from mid
        # But standard depth chart: X axis is price.
        # So we plot (price, cum_vol). 
        # For Bids: we usually accumulate from BEST (highest) to WORST (lowest).
        # But plotting on X axis (Price): Lowest Price is on Left. 
        # So curve goes from Right (Best) to Left (Worst) going UP.
        
        # Re-sort for plotting order if needed, but snapshots are already sorted
        # bids: [(100, 10), (99, 5)] -> best is 100.
        # We want to show: at 100, vol is 10. At 99, vol is 10+5=15.
        
        for price, size in bids:
            bid_prices.append(price)
            cumulative += size
            bid_cum_vol.append(cumulative)
            
        # Process Asks
        # asks: [(101, 5), (102, 10)] -> best is 101.
        # At 101, vol 5. At 102, vol 5+10=15.
        ask_prices = []
        ask_cum_vol = []
        cumulative = 0
        for price, size in asks:
            ask_prices.append(price)
            cumulative += size
            ask_cum_vol.append(cumulative)
            
        # Update Data
        bid_line.set_data(bid_prices, bid_cum_vol)
        ask_line.set_data(ask_prices, ask_cum_vol)
        
        ax.set_title(f"Order Book Evolution (Step {step})")
        
        # Clear old fills
        if bid_fill: 
            bid_fill.remove()
            bid_fill = None
        if ask_fill: 
            ask_fill.remove()
            ask_fill = None
            
        # Add new fills
        if bid_prices:
            bid_fill = ax.fill_between(bid_prices, bid_cum_vol, step="pre", color='green', alpha=0.3)
        if ask_prices:
            ask_fill = ax.fill_between(ask_prices, ask_cum_vol, step="post", color='red', alpha=0.3)
            
        fig.canvas.draw_idle()

    # Slider
    ax_slider = plt.axes([0.2, 0.1, 0.65, 0.03])
    slider = Slider(ax_slider, 'Step', 0, len(history)-1, valinit=0, valstep=1)
    
    slider.on_changed(update)
    
    # Trigger initial update
    update(0)
    
    plt.show()
