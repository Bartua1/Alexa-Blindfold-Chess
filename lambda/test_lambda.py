import unittest
from unittest.mock import MagicMock
from lambda_function import LaunchRequestHandler, LocalizationInterceptor
import language_strings

class TestLocalization(unittest.TestCase):
    def test_localization_interceptor_en(self):
        handler_input = MagicMock()
        handler_input.request_envelope.request.locale = "en-US"
        handler_input.attributes_manager.request_attributes = {}
        
        interceptor = LocalizationInterceptor()
        interceptor.process(handler_input)
        
        self.assertEqual(handler_input.attributes_manager.request_attributes["_"]["WELCOME_MSG"], 
                         language_strings.data["en"]["translation"]["WELCOME_MSG"])

    def test_localization_interceptor_es(self):
        handler_input = MagicMock()
        handler_input.request_envelope.request.locale = "es-ES"
        handler_input.attributes_manager.request_attributes = {}
        
        interceptor = LocalizationInterceptor()
        interceptor.process(handler_input)
        
        self.assertEqual(handler_input.attributes_manager.request_attributes["_"]["WELCOME_MSG"], 
                         language_strings.data["es"]["translation"]["WELCOME_MSG"])

    def test_launch_request_handler(self):
        handler_input = MagicMock()
        handler_input.request_envelope.request.object_type = "LaunchRequest"
        handler_input.attributes_manager.request_attributes = {"_": language_strings.data["en"]["translation"]}
        
        handler = LaunchRequestHandler()
        self.assertTrue(handler.can_handle(handler_input))
        
if __name__ == '__main__':
    unittest.main()
