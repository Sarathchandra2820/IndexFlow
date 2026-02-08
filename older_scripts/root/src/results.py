import matplotlib.pyplot as plt

# File name
file_name = "synthetic_prices.txt"

prices=[]

with open(file_name,"r") as file:
    for line in file:
        prices.append(float(line))

plt.plot(prices)
print(prices)