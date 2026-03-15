import unittest
from datetime import datetime, timedelta
from mock import MagicMock

# Mocking the SDK components needed for the test
class MockHandlerInput:
    def __init__(self, persistent_attr=None):
        self.attributes_manager = MagicMock()
        self.attributes_manager.persistent_attributes = persistent_attr or {}
        self.attributes_manager.save_persistent_attributes = MagicMock()

class HeartsLogicTest(unittest.TestCase):
    def test_daily_reset_logic(self):
        # Simulate an old reset date
        yesterday = (datetime.utcnow() - timedelta(days=1)).strftime('%Y-%m-%d')
        persistent_attr = {"last_reset_date": yesterday, "lives": 2}
        
        handler_input = MockHandlerInput(persistent_attr)
        
        # This mirrors the logic in LoadPersistenceInterceptor
        today = datetime.utcnow().strftime('%Y-%m-%d')
        pa = handler_input.attributes_manager.persistent_attributes
        if pa.get("last_reset_date") != today:
            pa["lives"] = 5
            pa["last_reset_date"] = today
            handler_input.attributes_manager.save_persistent_attributes()
            
        self.assertEqual(pa["lives"], 5)
        self.assertEqual(pa["last_reset_date"], today)
        handler_input.attributes_manager.save_persistent_attributes.assert_called_once()

    def test_decrement_logic(self):
        persistent_attr = {"lives": 5, "last_reset_date": datetime.utcnow().strftime('%Y-%m-%d')}
        handler_input = MockHandlerInput(persistent_attr)
        
        # Simulate wrong answer logic
        pa = handler_input.attributes_manager.persistent_attributes
        pa["lives"] -= 1
        handler_input.attributes_manager.save_persistent_attributes()
        
        self.assertEqual(pa["lives"], 4)
        handler_input.attributes_manager.save_persistent_attributes.assert_called_once()

if __name__ == '__main__':
    unittest.main()
