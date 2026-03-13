# -*- coding: utf-8 -*-

import logging
from ask_sdk_core.skill_builder import SkillBuilder
from ask_sdk_core.dispatch_components import AbstractRequestHandler, AbstractExceptionHandler, AbstractRequestInterceptor
from ask_sdk_core.utils import is_request_type, is_intent_name
from ask_sdk_core.handler_input import HandlerInput
from ask_sdk_model import Response
import json
import language_strings
from chess_engine.board_manager import BoardManager

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

import os

# Get path to APL folder
APL_PATH = os.path.join(os.path.dirname(__file__), "apl")

def get_board_image_url(fen):
    """Returns a URL to a rendered board image using a 3rd party service."""
    # Using chess-board.com as a simple public renderer
    encoded_fen = fen.replace(" ", "%20")
    return f"https://www.chess-board.com/board.png?fen={encoded_fen}"

def get_apl_directive(handler_input, engine):
    """Generates the APL RenderDocument directive if supported."""
    try:
        supported = getattr(handler_input.request_envelope.context.system.device.supported_interfaces, 'alexa_presentation_apl', None)
        if supported:
            # Use absolute path for robustness in Lambda
            path = os.path.join(APL_PATH, "chessboard.json")
            with open(path) as f:
                apl_doc = json.load(f)
                
            return {
                "type": "Alexa.Presentation.APL.RenderDocument",
                "document": apl_doc,
                "datasources": {
                    "payload": {
                        "boardData": {
                            "boardUrl": get_board_image_url(engine.get_fen()),
                            "status": engine.get_game_result()
                        }
                    }
                }
            }
    except Exception as e:
        logger.error(f"Error generating APL: {e}", exc_info=True)
    return None

class LaunchRequestHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        return is_request_type("LaunchRequest")(handler_input)

    def handle(self, handler_input):
        data = handler_input.attributes_manager.request_attributes["_"]
        
        # Initialize board
        engine = BoardManager()
        handler_input.attributes_manager.session_attributes["board_fen"] = engine.get_fen()
        
        speech_text = data["WELCOME_MSG"]
        response_builder = handler_input.response_builder.speak(speech_text).ask(speech_text)
        
        # Add APL if supported
        directive = get_apl_directive(handler_input, engine)
        if directive:
            response_builder.add_directive(directive)
            
        return response_builder.response

class MoveIntentHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        return is_intent_name("MoveIntent")(handler_input)

    def handle(self, handler_input):
        data = handler_input.attributes_manager.request_attributes["_"]
        piece = handler_input.request_envelope.request.intent.slots["piece"].value
        square = handler_input.request_envelope.request.intent.slots["square"].value
        
        # Load board from session
        session_attr = handler_input.attributes_manager.session_attributes
        fen = session_attr.get("board_fen")
        engine = BoardManager(fen)
        
        # Parse and execute player move
        san_move = BoardManager.parse_alexa_slots(piece, square)
        success, error_msg = engine.make_move(san_move)
        
        if not success:
            logger.info(f"Invalid move attempted: {san_move} - {error_msg}")
            speech_text = f"{san_move} " + data["ERROR_MSG"]
            return (
                handler_input.response_builder
                    .speak(speech_text)
                    .ask(data["HELP_MSG"])
                    .response
            )
        
        # Execute AI move
        if engine.is_game_over():
            speech_text = data["REFLECT_MOVE"].format(piece=piece, square=square) + " " + engine.get_game_result()
        else:
            ai_move = engine.get_ai_move()
            speech_text = data["REFLECT_MOVE"].format(piece=piece, square=square) + f" I play {ai_move}. Your turn."
            
            if engine.is_game_over():
                speech_text += " " + engine.get_game_result()
        
        # Save board back to session
        session_attr["board_fen"] = engine.get_fen()
        
        response_builder = handler_input.response_builder.speak(speech_text).ask("Your move?")
        
        # Add APL if supported
        directive = get_apl_directive(handler_input, engine)
        if directive:
            response_builder.add_directive(directive)
            
        return response_builder.response

class HelpIntentHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        return is_intent_name("AMAZON.HelpIntent")(handler_input)

    def handle(self, handler_input):
        data = handler_input.attributes_manager.request_attributes["_"]
        speech_text = data["HELP_MSG"]
        return (
            handler_input.response_builder
                .speak(speech_text)
                .ask(speech_text)
                .response
        )

class CancelOrStopIntentHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        return (is_intent_name("AMAZON.CancelIntent")(handler_input) or
                is_intent_name("AMAZON.StopIntent")(handler_input))

    def handle(self, handler_input):
        data = handler_input.attributes_manager.request_attributes["_"]
        speech_text = data["GOODBYE_MSG"]
        return (
            handler_input.response_builder
                .speak(speech_text)
                .response
        )

class FallbackIntentHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        return is_intent_name("AMAZON.FallbackIntent")(handler_input)

    def handle(self, handler_input):
        data = handler_input.attributes_manager.request_attributes["_"]
        speech_text = data["FALLBACK_MSG"]
        return (
            handler_input.response_builder
                .speak(speech_text)
                .ask(speech_text)
                .response
        )

class SessionEndedRequestHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        return is_request_type("SessionEndedRequest")(handler_input)

    def handle(self, handler_input):
        return handler_input.response_builder.response

class CatchAllExceptionHandler(AbstractExceptionHandler):
    def can_handle(self, handler_input, exception):
        return True

    def handle(self, handler_input, exception):
        logger.error(exception, exc_info=True)
        data = handler_input.attributes_manager.request_attributes["_"]
        speech_text = data["ERROR_MSG"]
        return (
            handler_input.response_builder
                .speak(speech_text)
                .ask(speech_text)
                .response
        )

class LocalizationInterceptor(AbstractRequestInterceptor):
    def process(self, handler_input):
        locale = handler_input.request_envelope.request.locale
        logger.info(f"Locale: {locale}")
        
        # Simplified localization: match prefix (e.g., 'en-US' -> 'en')
        lang = locale.split('-')[0]
        if lang not in language_strings.data:
            lang = 'en' # Default
            
        handler_input.attributes_manager.request_attributes["_"] = language_strings.data[lang]["translation"]

sb = SkillBuilder()

sb.add_request_handler(LaunchRequestHandler())
sb.add_request_handler(MoveIntentHandler())
sb.add_request_handler(HelpIntentHandler())
sb.add_request_handler(CancelOrStopIntentHandler())
sb.add_request_handler(FallbackIntentHandler())
sb.add_request_handler(SessionEndedRequestHandler())

sb.add_exception_handler(CatchAllExceptionHandler())

sb.add_global_request_interceptor(LocalizationInterceptor())

lambda_handler = sb.lambda_handler()
