# -*- coding: utf-8 -*-

from ask_sdk_core.skill_builder import SkillBuilder
from ask_sdk_core.dispatch_components import AbstractRequestHandler
from ask_sdk_core.utils import is_request_type, is_intent_name

class LaunchRequestHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        return is_request_type("LaunchRequest")(handler_input)

    def handle(self, handler_input):
        speech_text = "Welcome to Blindfold Chess! You can start a game by saying a move like move pawn to e4."
        return (
            handler_input.response_builder
                .speak(speech_text)
                .ask(speech_text)
                .response
        )

class MoveIntentHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        return is_intent_name("MoveIntent")(handler_input)

    def handle(self, handler_input):
        piece = handler_input.request_envelope.request.intent.slots["piece"].value
        square = handler_input.request_envelope.request.intent.slots["square"].value
        speech_text = f"You moved your {piece} to {square}. I am processing the move."
        return (
            handler_input.response_builder
                .speak(speech_text)
                .response
        )

sb = SkillBuilder()
sb.add_request_handler(LaunchRequestHandler())
sb.add_request_handler(MoveIntentHandler())

lambda_handler = sb.lambda_handler()
