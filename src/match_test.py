import unittest
from exchange import Exchange
from agent_logic import Agent
from order_book import OrderBook

class TestMatchingEngine(unittest.TestCase):
    def setUp(self):
        self.ex = Exchange()
        self.alice = Agent(id="Alice", cash=10000, inventory=100) # Seller
        self.bob = Agent(id="Bob", cash=10000, inventory=100)     # Buyer
        
        self.ex.register_agent(self.alice)
        self.ex.register_agent(self.bob)

    def test_passive_order(self):
        print("\n--- Test Passive Order ---")
        # Alice places Ask @ 100
        self.ex.process_limit_order(self.alice, "ask", 100.0, 10)
        
        # Bob places Bid @ 99 (No Match)
        self.ex.process_limit_order(self.bob, "bid", 99.0, 5)
        
        self.assertEqual(len(self.ex.order_book.bid_dic[99.0]), 1)
        self.assertEqual(len(self.ex.order_book.ask_dic[100.0]), 1)
        print("Passive order verified.")

    def test_aggressive_full_fill(self):
        print("\n--- Test Aggressive Full Fill ---")
        # Alice places Ask @ 100 (Size 10)
        self.ex.process_limit_order(self.alice, "ask", 100.0, 10)
        
        # Bob places Bid @ 101 (Size 2) -> Should match at 100
        initial_cash_bob = self.bob.cash
        initial_inv_bob = self.bob.inventory
        initial_cash_alice = self.alice.cash
        initial_inv_alice = self.alice.inventory
        
        self.ex.process_limit_order(self.bob, "bid", 101.0, 2)
        
        # Checks
        # Alice sold 2
        # Inventory was already deducted when she placed the order (100 - 10 = 90). 
        # It should NOT drop further upon trade.
        self.assertEqual(self.alice.inventory, initial_inv_alice) 
        self.assertEqual(self.alice.cash, initial_cash_alice + 200.0) # 2 * 100
        
        # Bob bought 2
        self.assertEqual(self.bob.inventory, initial_inv_bob + 2)
        self.assertEqual(self.bob.cash, initial_cash_bob - 200.0) # Paid 100 each (improved from 101)
        
        # Book: Ask size should be 8
        self.assertEqual(self.ex.order_book.ask_dic[100.0][0].size, 8)
        print("Aggressive full fill verified.")

    def test_aggressive_partial_fill(self):
        print("\n--- Test Aggressive Partial Fill ---")
        # Alice places Ask @ 100 (Size 2)
        self.ex.process_limit_order(self.alice, "ask", 100.0, 2)
        
        # Bob places Bid @ 101 (Size 5) -> Match 2 @ 100, Remainder 3 @ 101
        self.ex.process_limit_order(self.bob, "bid", 101.0, 5)
        
        # Checks
        # Alice sold 2. Inventory deducted at order placement (100 -> 98).
        self.assertEqual(self.alice.inventory, 98) 
        self.assertEqual(self.alice.cash, 10200)   # +200
        
        # Bob bought 2
        # Paid 2*100 = 200 for the trades.
        # Committed 3*101 = 303 for the remainder.
        # Total cost = 503.
        # Initial cash 10000 -> 9497
        self.assertEqual(self.bob.inventory, 102)
        self.assertEqual(self.bob.cash, 10000 - 200 - 303)
        
        # Book: Ask @ 100 gone. Bid @ 101 size 3.
        self.assertTrue(100.0 not in self.ex.order_book.ask_dic)
        self.assertEqual(self.ex.order_book.bid_dic[101.0][0].size, 3)
        print("Aggressive partial fill verified.")

    def test_sweep(self):
        print("\n--- Test Sweep ---")
        # Alice places Ask @ 100 (Size 2)
        self.ex.process_limit_order(self.alice, "ask", 100.0, 2)
        # Alice places Ask @ 101 (Size 2)
        self.ex.process_limit_order(self.alice, "ask", 101.0, 2)
        
        # Bob places Bid @ 102 (Size 5) -> Match 2@100, 2@101, Remainder 1@102
        self.ex.process_limit_order(self.bob, "bid", 102.0, 5)
        
        # Checks
        # Alice sold 4 (2+2). Inventory (100 - 4 = 96).
        self.assertEqual(self.alice.inventory, 96)
        self.assertEqual(self.alice.cash, 10000 + 200 + 202) # 402
        
        # Bob bought 4
        # Paid 2*100 + 2*101 = 402
        # Committed 1*102 = 102
        # Total deduction = 504
        self.assertEqual(self.bob.inventory, 104)
        self.assertEqual(self.bob.cash, 10000 - 504)
        
        # Book: Asked cleared. Bid @ 102 size 1.
        self.assertTrue(100.0 not in self.ex.order_book.ask_dic)
        self.assertTrue(101.0 not in self.ex.order_book.ask_dic)
        self.assertEqual(self.ex.order_book.bid_dic[102.0][0].size, 1)
        print("Sweep verified.")

if __name__ == '__main__':
    unittest.main()
