# -*- coding: utf-8 -*-

import logging
from ask_sdk_core.skill_builder import SkillBuilder
from ask_sdk_core.dispatch_components import AbstractRequestHandler, AbstractExceptionHandler, AbstractRequestInterceptor
from ask_sdk_core.utils import is_request_type, is_intent_name
from ask_sdk_core.handler_input import HandlerInput
from ask_sdk_model import Response
from ask_sdk_model.interfaces.alexa.presentation.apl import RenderDocumentDirective
import json
import os
import random
import logging
import language_strings
from chess_engine.board_manager import BoardManager

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

import os

# Get path to APL folder
APL_PATH = os.path.join(os.path.dirname(__file__), "apl")

def get_board_image_url(fen):
    """Returns a URL to a rendered board image using a 3rd party service."""
    # Using fen-to-image for a cleaner look
    encoded_fen = fen.replace(" ", "%20")
    return f"https://fen-to-image.com/image/{encoded_fen}"

def get_apl_directive(handler_input, engine, last_move="Welcome!"):
    """Generates the APL RenderDocument directive if supported."""
    try:
        context = handler_input.request_envelope.context
        interfaces = context.system.device.supported_interfaces
        logger.info(f"Supported Interfaces: {interfaces}")
        
        # Check if APL is supported or if there is a Viewport (indicating a screen)
        has_apl = getattr(interfaces, 'alexa_presentation_apl', None) is not None
        has_viewport = getattr(context, 'viewport', None) is not None
        
        if has_apl or has_viewport:
            # Use absolute path for robustness in Lambda
            # Use absolute path for robustness in Lambda
            path = os.path.join(APL_PATH, "chessboard.json")
            with open(path) as f:
                apl_doc = json.load(f)
            
            fen = engine.get_fen() if engine else "8/8/8/8/8/8/8/8"
            status = engine.get_game_result() if engine else ""
                
            return RenderDocumentDirective(
                document=apl_doc,
                datasources={
                    "payload": {
                        "boardData": {
                            "boardUrl": get_board_image_url(fen),
                            "status": status,
                            "lastMove": last_move
                        }
                    }
                }
            )
    except Exception as e:
        logger.error(f"Error generating APL: {e}", exc_info=True)
    return None

def get_puzzles():
    # Try to find the file in the same directory as this script
    script_dir = os.path.dirname(os.path.abspath(__file__))
    path = os.path.join(script_dir, "puzzles.json")
    
    if os.path.exists(path):
        with open(path) as f:
            return json.load(f)
            
    # Fallback to current working directory
    path = os.path.join(os.getcwd(), "puzzles.json")
    if os.path.exists(path):
        with open(path) as f:
            return json.load(f)
            
    raise FileNotFoundError(f"puzzles.json not found in absolute path: {os.path.abspath(path)}")

def get_square_color(square):
    # a1 is (0,0) and is BLACK. 
    # (file + rank) % 2 == 0 is BLACK, == 1 is WHITE
    file = ord(square[0]) - ord('a')
    rank = int(square[1]) - 1
    return "black" if (file + rank) % 2 == 0 else "white"

class LaunchRequestHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        return is_request_type("LaunchRequest")(handler_input)

    def handle(self, handler_input):
        data = handler_input.attributes_manager.request_attributes["_"]
        
        # Initialize session state
        attr = handler_input.attributes_manager.session_attributes
        attr["mode"] = "matches"
        
        # Initialize board for Matches mode
        engine = BoardManager()
        attr["board_fen"] = engine.get_fen()
        
        speech_text = data["WELCOME_MSG"]
        response_builder = handler_input.response_builder.speak(speech_text).ask(speech_text)
        
        # Add APL if supported
        directive = get_apl_directive(handler_input, engine)
        if directive:
            response_builder.add_directive(directive)
            
        return response_builder.response

class SwitchModeIntentHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        return is_intent_name("SwitchModeIntent")(handler_input)

    def handle(self, handler_input):
        data = handler_input.attributes_manager.request_attributes["_"]
        attr = handler_input.attributes_manager.session_attributes
        
        mode = handler_input.request_envelope.request.intent.slots["mode"].value
        if not mode:
            mode = "matches" # Default fallback
            
        attr["mode"] = mode
        speech_text = data["MODE_SWITCHED"].format(mode=mode)
        
        if mode == "squares":
            square = random.choice([f"{f}{r}" for f in "abcdefgh" for r in "12345678"])
            attr["current_square"] = square
            speech_text = data["SQUARES_MODE_START"].format(square=square)
            return handler_input.response_builder.speak(speech_text).ask(speech_text).response
        
        if mode == "puzzles":
            # Just trigger puzzle logic
            return PuzzleIntentHandler().handle(handler_input)
            
        # Default back to matches
        engine = BoardManager(attr.get("board_fen"))
        response_builder = handler_input.response_builder.speak(speech_text).ask("Your move?")
        directive = get_apl_directive(handler_input, engine, f"Switched to {mode}")
        if directive:
            response_builder.add_directive(directive)
        return response_builder.response

class MoveIntentHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        return is_intent_name("MoveIntent")(handler_input)

    def handle(self, handler_input):
        data = handler_input.attributes_manager.request_attributes["_"]
        attr = handler_input.attributes_manager.session_attributes
        
        mode = attr.get("mode", "matches")
        
        if mode == "squares":
            return handler_input.response_builder.speak(data["ERROR_MSG"]).ask(data["HELP_MSG"]).response
            
        piece = handler_input.request_envelope.request.intent.slots["piece"].value
        square = handler_input.request_envelope.request.intent.slots["square"].value
        
        # Load board from session
        fen = attr.get("board_fen")
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
            
        if mode == "puzzles":
            solution = attr.get("puzzle_solution")
            # Loose comparison (solution might be UCI or SAN)
            if san_move.lower() == solution.lower() or error_msg.lower() == solution.lower():
                speech_text = data["CORRECT_ANSWER"] + " Would you like another one?"
                attr["puzzle_solved"] = True
            else:
                speech_text = data["WRONG_ANSWER"]
            
            response_builder = handler_input.response_builder.speak(speech_text).ask("What is your move?")
            directive = get_apl_directive(handler_input, engine, f"Puzzle Solution: {solution}")
            if directive:
                response_builder.add_directive(directive)
            return response_builder.response
        
        # Execute AI move (Matches mode)
        if engine.is_game_over():
            speech_text = data["REFLECT_MOVE"].format(piece=piece, square=square) + " " + engine.get_game_result()
        else:
            ai_move = engine.get_ai_move()
            speech_text = data["REFLECT_MOVE"].format(piece=piece, square=square) + f" I play {ai_move}. Your turn."
            
            if engine.is_game_over():
                speech_text += " " + engine.get_game_result()
        
        # Save board back to session
        attr["board_fen"] = engine.get_fen()
        
        response_builder = handler_input.response_builder.speak(speech_text).ask("Your move?")
        
        # Add APL if supported
        last_move_text = f"You: {piece} to {square}"
        if not engine.is_game_over():
            last_move_text += f" | AI: {ai_move}"
            
        directive = get_apl_directive(handler_input, engine, last_move_text)
        if directive:
            response_builder.add_directive(directive)
            
        return response_builder.response

class SquareColorIntentHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        attr = handler_input.attributes_manager.session_attributes
        return (attr.get("mode") == "squares" and 
                is_intent_name("SquareColorIntent")(handler_input))

    def handle(self, handler_input):
        data = handler_input.attributes_manager.request_attributes["_"]
        attr = handler_input.attributes_manager.session_attributes
        
        user_color = handler_input.request_envelope.request.intent.slots["color"].value
        correct_color = get_square_color(attr.get("current_square"))
        
        # Normalize comparison
        if user_color.lower() in [correct_color, "blanco" if correct_color == "white" else "negro"]:
            new_square = random.choice([f"{f}{r}" for f in "abcdefgh" for r in "12345678"])
            attr["current_square"] = new_square
            speech_text = data["NEXT_SQUARE"].format(square=new_square)
        else:
            speech_text = data["WRONG_ANSWER"]
            
        return handler_input.response_builder.speak(speech_text).ask(speech_text).response

class PuzzleIntentHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        return (is_intent_name("PuzzleIntent")(handler_input) or 
                (is_intent_name("SwitchModeIntent")(handler_input) and 
                 handler_input.request_envelope.request.intent.slots["mode"].value == "puzzles"))

    def handle(self, handler_input):
        data = handler_input.attributes_manager.request_attributes["_"]
        attr = handler_input.attributes_manager.session_attributes
        
        puzzles = get_puzzles()
        # Mix easy/medium for now
        all_puzzles = puzzles["easy"] + puzzles["medium"]
        puzzle = random.choice(all_puzzles)
        
        attr["mode"] = "puzzles"
        attr["board_fen"] = puzzle["fen"]
        attr["puzzle_solution"] = puzzle["solution"]
        attr["puzzle_id"] = puzzle["id"]
        
        speech_text = data["PUZZLES_MODE_START"].format(description=puzzle["description"])
        
        engine = BoardManager(puzzle["fen"])
        response_builder = handler_input.response_builder.speak(speech_text).ask(speech_text)
        
        directive = get_apl_directive(handler_input, engine, puzzle["description"])
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
sb.add_request_handler(SwitchModeIntentHandler())
sb.add_request_handler(SquareColorIntentHandler())
sb.add_request_handler(PuzzleIntentHandler())
sb.add_request_handler(MoveIntentHandler())
sb.add_request_handler(HelpIntentHandler())
sb.add_request_handler(CancelOrStopIntentHandler())
sb.add_request_handler(FallbackIntentHandler())
sb.add_request_handler(SessionEndedRequestHandler())

sb.add_exception_handler(CatchAllExceptionHandler())

sb.add_global_request_interceptor(LocalizationInterceptor())

lambda_handler = sb.lambda_handler()
