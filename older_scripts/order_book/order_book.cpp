#include <iostream>       // For input/output
#include <string>         // For string manipulation
#include <vector>         // For storing a list of orders
#include <map>            // For the order book structure
#include <deque>          // For managing queues of orders
#include <ctime>          // For timestamps
#include <cstdlib>        // For random numbers
#include <ctime>   // For std::time


// Define a struct for the Orderbook

struct Order {
    int id;        // Unique id to identify the buyer or seller
    double price;   // Price at which they wanna buy 
    int quantity;  // Quantity at they wanna buy {Number of shares for example}
    bool buyorsell; // True for buy and false for sell 
    long timestamp; // Time at which the order is placed 
    // Constructor
    Order(int orderId, double orderPrice, int orderQuantity, bool buy)
        : id(orderId), price(orderPrice), quantity(orderQuantity), buyorsell(buy) {
        timestamp = std::time(nullptr); // Current time
    }

};

std::map<double, std::deque<Order>> bids;
std::map<double, std::deque<Order>> asks;

void addorder(std::map<double, std::deque<Order>> &bids,
                std::map<double, std::deque<Order>> &asks, const Order &order) {
                    if (order.buyorsell) {
                        bids[order.price].push_back(order);
                    } // If its a buy order, then map the order object to the price 
                    else {
                        asks[order.price].push_back(order);
                    }
                    
                }

// generating synthetic data 

Order generateOrder(int id, double midpointPrice) {
    bool buyorsell = std::rand() % 2; // Randomly decide buy or sell
    double price = midpointPrice + (std::rand() % 5 - 2); // +/-2 price variation
    int quantity = std::rand() % 100 + 1; // Random quantity between 1 and 100

    return Order(id, price, quantity, buyorsell);
}

void printOrderBook(const std::map<double, std::deque<Order>> &bids,
                    const std::map<double, std::deque<Order>> &asks) {
    std::cout << "ORDER BOOK:" << std::endl;

    // Print Bids
    std::cout << "Bids (Buy Orders):" << std::endl;
    for (auto it = bids.rbegin(); it != bids.rend(); ++it) { // Reverse iterate for descending order
        double price = it->first;
        int totalQuantity = 0;

        // Sum up the quantities for all orders at this price
        for (const auto &order : it->second) {
            totalQuantity += order.quantity;
        }

        std::cout << "Price: $" << price << " | Total Quantity: " << totalQuantity << std::endl;
    }



    // Print Asks
    std::cout << "Asks (Sell Orders):" << std::endl;
    for (auto it = asks.begin(); it != asks.end(); ++it) { // Ascending order
        double price = it->first;
        int totalQuantity = 0;

        // Sum up the quantities for all orders at this price
        for (const auto &order : it->second) {
            totalQuantity += order.quantity;
        }

        std::cout << "Price: $" << price << " | Total Quantity: " << totalQuantity << std::endl;
    }
}


int main() {
   // std::srand(std::time(0)); // Seed random number generator

    std::map<double, std::deque<Order>> bids;
    std::map<double, std::deque<Order>> asks;

    double midpointPrice = 100.0; // Base price

    // Generate and add synthetic orders
    for (int i = 1; i <= 100; ++i) {
        Order order = generateOrder(i, midpointPrice);
        addorder(bids, asks, order);
    }

    // Print the order book
    printOrderBook(bids, asks);

    return 0;
}
