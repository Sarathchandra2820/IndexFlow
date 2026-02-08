import unittest
from exchange import Exchange
from agent_logic import Agent

class TestPassiveLimitOrder(unittest.TestCase):
    def setUp(self):
        self.ex = Exchange()
        # Alice has lots of cash, 0 inventory
        self.alice = Agent(id="Alice", cash=1000.0, inventory=0)
        # Bob has 0 cash, lots of inventory
        self.bob = Agent(id="Bob", cash=0.0, inventory=10)
        
        self.ex.register_agent(self.alice)
        self.ex.register_agent(self.bob)

    def test_passive_bid_outside_spread(self):
        """
        Test placing a BID that is lower than any ASK (or in empty book).
        Result: Should NOT trade. Should lock cash. Should sit in book.
        """
        print("\n--- Test: Passive Bid (Outside Spread) ---")
        
        # 1. Inspect Initial State
        print(f"[Initial] Alice Cash: {self.alice.cash}, Inventory: {self.alice.inventory}")
        initial_cash = self.alice.cash
        
        # 2. Place Passive Bid
        # Price 90.0, Size 1.
        # This is the first order, so it's definitely passive.
        limit_price = 90.0
        size = 1
        
        print(f"Action: Alice places BID @ {limit_price} (Size {size})")
        self.ex.process_limit_order(self.alice, "bid", limit_price, size)
        
        # 3. Verify Cash Locked
        # Cash should decrease by price * size immediately
        expected_cash = initial_cash - (limit_price * size)
        self.assertEqual(self.alice.cash, expected_cash, "Cash should be deducted (locked) immediately")
        print(f"[Check] Cash locked correctly. New Balance: {self.alice.cash}")
        
        # 4. Verify No Trade Occurred
        self.assertEqual(self.alice.inventory, 0, "Inventory should NOT change (no trade)")
        print("[Check] Inventory unchanged (No trade detected).")
        
        # 5. Verify Order in Book
        # Should be in bid_dic at price 90.0
        bids = self.ex.order_book.bid_dic
        self.assertTrue(limit_price in bids, "Order price should exist in Bid Book")
        self.assertEqual(bids[limit_price][0].agent_id, "Alice", "Order in book should belong to Alice")
        self.assertEqual(bids[limit_price][0].size, size, "Order size in book should match")
        print(f"[Check] Order confirmed in Book: {bids[limit_price][0]}")

    def test_passive_ask_outside_spread(self):
        """
        Test placing an ASK that is higher than any BID.
        Result: Should NOT trade. Should lock inventory. Should sit in book.
        """
        print("\n--- Test: Passive Ask (Outside Spread) ---")
        
        # Setup: Put a Bid in first so we have a spread
        # Alice bids @ 90
        self.ex.process_limit_order(self.alice, "bid", 90.0, 1)
        
        # 1. Inspect Bob's Initial State
        print(f"[Initial] Bob Cash: {self.bob.cash}, Inventory: {self.bob.inventory}")
        initial_inv = self.bob.inventory
        
        # 2. Place Passive Ask
        # Price 110.0 (Higher than best bid 90.0) -> Outside Spread
        limit_price = 110.0
        size = 2
        
        print(f"Action: Bob places ASK @ {limit_price} (Size {size})")
        self.ex.process_limit_order(self.bob, "ask", limit_price, size)
        
        # 3. Verify Inventory Locked
        expected_inv = initial_inv - size
        self.assertEqual(self.bob.inventory, expected_inv, "Inventory should be deducted (locked) immediately")
        print(f"[Check] Inventory locked correctly. New Inventory: {self.bob.inventory}")
        
        # 4. Verify No Trade
        self.assertEqual(self.bob.cash, 0.0, "Cash should NOT change (no trade)")
        print("[Check] Cash unchanged (No trade detected).")
        
        # 5. Verify Order in Book
        asks = self.ex.order_book.ask_dic
        self.assertTrue(limit_price in asks, "Order price should exist in Ask Book")
        self.assertEqual(asks[limit_price][0].agent_id, "Bob")
        print(f"[Check] Order confirmed in Book: {asks[limit_price][0]}")
        
    def test_spread_formation(self):
        print("\n--- Test: Spread Formation ---")
        # Alice Bids @ 90
        self.ex.process_limit_order(self.alice, "bid", 90.0, 1)
        # Bob Asks @ 110
        self.ex.process_limit_order(self.bob, "ask", 110.0, 1)
        
        # Check Best Bid / Best Ask
        bb = self.ex.order_book.get_best_bid()
        ba = self.ex.order_book.get_best_ask()
        
        print(f"Best Bid: {bb}, Best Ask: {ba}")
        self.assertEqual(bb, 90.0)
        self.assertEqual(ba, 110.0)
        self.assertTrue(bb < ba, "Best Bid should be less than Best Ask (Normal Spread)")
        print(f"[Check] Spread is {ba - bb}")

if __name__ == '__main__':
    unittest.main()
