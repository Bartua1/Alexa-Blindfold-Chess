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
import time
from chess_engine.board_manager import BoardManager

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

import os

# Get path to APL folder
APL_PATH = os.path.join(os.path.dirname(__file__), "apl")

def get_board_image_url(fen=None, highlight=None, squares=None):
    """Returns a URL to a rendered board image using the local server."""
    base_url = "https://bartualfdez.asuscomm.com/blindfoldchess/chessboard"
    
    params = []
    if highlight:
        params.append(f"highlight={highlight}")
    if fen:
        params.append(f"fen={fen.replace(' ', '%20')}")
    if squares:
        params.append(f"squares={squares}")
        
    if params:
        return f"{base_url}?{'&'.join(params)}"
    
    return base_url

def get_apl_directive(handler_input, engine=None, last_move="Welcome!", type="board"):
    """Generates the APL RenderDocument directive if supported."""
    try:
        data = handler_input.attributes_manager.request_attributes["_"]
        context = handler_input.request_envelope.context
        interfaces = context.system.device.supported_interfaces
        
        # Strict check: ensure the alexa_presentation_apl interface is present
        if interfaces.alexa_presentation_apl is not None:
            if type == "menu":
                path = os.path.join(APL_PATH, "menu.json")
                with open(path) as f:
                    apl_doc = json.load(f)
                return RenderDocumentDirective(
                    document=apl_doc,
                    datasources={
                        "imageListData": {
                            "title": data["MENU_TITLE"],
                            "listItems": [
                                {
                                    "primaryText": data["MENU_MATCHES"],
                                    "secondaryText": data["MENU_MATCHES_SUB"],
                                    "imageSource": "https://bartualfdez.asuscomm.com/blindfoldchess/assets/images/match.png",
                                    "value": "matches"
                                },
                                {
                                    "primaryText": data["MENU_PUZZLES"],
                                    "secondaryText": data["MENU_PUZZLES_SUB"],
                                    "imageSource": "https://bartualfdez.asuscomm.com/blindfoldchess/assets/images/puzzles.png",
                                    "value": "puzzles"
                                },
                                {
                                    "primaryText": data["MENU_SQUARES"],
                                    "secondaryText": data["MENU_SQUARES_SUB"],
                                    "imageSource": "https://bartualfdez.asuscomm.com/blindfoldchess/assets/images/squares.png",
                                    "value": "squares"
                                }
                            ],
                            "hintText": data["HELP_MSG"]
                        }
                    }
                )
            
            if type == "squares":
                path = os.path.join(APL_PATH, "squares.json")
                with open(path) as f:
                    apl_doc = json.load(f)
                
                squares_data = engine if isinstance(engine, dict) else {}
                
                return RenderDocumentDirective(
                    document=apl_doc,
                    datasources={
                        "squaresData": {
                            "title": squares_data.get("title", data["MENU_SQUARES"]),
                            "feedback": squares_data.get("feedback", ""),
                            "logoUrl": "https://bartualfdez.asuscomm.com/blindfoldchess/assets/images/squares.png",
                            "boardUrl": squares_data.get("boardUrl", get_board_image_url()),
                            "currentQuestion": squares_data.get("currentQuestion", ""),
                            "timeText": squares_data.get("timeText", ""),
                            "ratingNumber": squares_data.get("ratingNumber", 0)
                        }
                    }
                )
            
            if type == "puzzles":
                path = os.path.join(APL_PATH, "puzzles.json")
                with open(path) as f:
                    apl_doc = json.load(f)
                
                puzzle_data = engine if isinstance(engine, dict) else {}
                
                return RenderDocumentDirective(
                    document=apl_doc,
                    datasources={
                        "puzzleData": {
                            "title": data["MENU_PUZZLES"],
                            "subtitle": puzzle_data.get("subtitle", ""),
                            "feedback": puzzle_data.get("feedback", ""),
                            "logoUrl": "https://bartualfdez.asuscomm.com/blindfoldchess/assets/images/puzzles.png",
                            "boardUrl": puzzle_data.get("boardUrl", get_board_image_url(puzzle_data.get("fen"))),
                            "description": puzzle_data.get("description", "")
                        }
                    }
                )
            
            if type == "matches":
                path = os.path.join(APL_PATH, "match.json")
                with open(path) as f:
                    apl_doc = json.load(f)
                
                fen = engine.get_fen() if engine else "8/8/8/8/8/8/8/8"
                status = engine.get_game_result() if engine else ""
                
                # Fetch move history from session attributes
                attr = handler_input.attributes_manager.session_attributes
                move_history_list = attr.get("move_history", [])
                move_history_data = get_move_history_datasource(move_history_list)
                
                return RenderDocumentDirective(
                    document=apl_doc,
                    datasources={
                        "matchData": {
                            "title": data["MENU_MATCHES"],
                            "subtitle": data.get("MOVE_HISTORY_LABEL", "Move History"),
                            "logoUrl": "https://bartualfdez.asuscomm.com/blindfoldchess/assets/images/match.png",
                            "boardUrl": get_board_image_url(fen),
                            "lastMove": last_move,
                            "moveHistory": move_history_data,
                            "status": status if status != "ONGOING" else ""
                        }
                    }
                )
            
            # Default to board (old standard view)
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

def get_verbal_board_description(engine, data):
    """Returns a spoken description of the board state."""
    positions = engine.get_piece_positions()
    
    def format_list(pieces):
        return ", ".join([
            data["PIECE_POSITION"].format(
                piece=data["PIECES"][p["piece"]], 
                square=p["square"]
            ) for p in pieces
        ])
    
    white_pieces = format_list(positions["white"])
    black_pieces = format_list(positions["black"])
    
    return data["BOARD_DESCRIPTION"].format(
        white_pieces=white_pieces, 
        black_pieces=black_pieces
    )

def get_localized_move(san_move, data):
    """Translates a SAN move like 'Nf3' to a spoken description like 'Knight to f3'."""
    if not san_move:
        return ""
        
    is_spanish = "Resuelve" in data.get("SOLVE_PUZZLE", "")
    
    # Castling
    if san_move == "O-O":
        return "Enroque corto" if is_spanish else "Kingside castle"
    if san_move == "O-O-O":
        return "Enroque largo" if is_spanish else "Queenside castle"
        
    piece_names = data.get("PIECE_NAMES", {})
    
    # Clean move from symbols like #, +, etc.
    clean_move = san_move.replace("#", "").replace("+", "")
    
    if len(clean_move) >= 1 and clean_move[0].isupper() and clean_move[0] in piece_names:
        piece_symbol = clean_move[0]
        piece_name = piece_names[piece_symbol]
        square = clean_move[-2:]
        if "x" in san_move:
            connector = " captura en " if is_spanish else " takes on "
        else:
            connector = " a " if is_spanish else " to "
        return f"{piece_name}{connector}{square}"
    else:
        # Pawn move
        if "x" in san_move:
            piece_name = piece_names.get("", "Peón" if is_spanish else "Pawn")
            square = clean_move[-2:]
            connector = " captura en " if is_spanish else " takes on "
            return f"{piece_name}{connector}{square}"
        else:
            return san_move # e.g. "e4"
def get_puzzles():
    # Use path relative to this script for robust loading in any environment
    script_dir = os.path.dirname(os.path.abspath(__file__))
    path = os.path.join(script_dir, "puzzles.json")
    
    if os.path.exists(path):
        with open(path) as f:
            return json.load(f)
            
    raise FileNotFoundError(f"puzzles.json not found at: {path}")

def get_square_color(square):
    # a1 is (0,0) and is BLACK. 
    # (file + rank) % 2 == 0 is BLACK, == 1 is WHITE
    file = ord(square[0]) - ord('a')
    rank = int(square[1]) - 1
    return "black" if (file + rank) % 2 == 0 else "white"

def get_move_history_datasource(moves):
    """Formats a list of moves into a structured list for APL Sequence."""
    if not moves:
        return []
    
    items = []
    for i in range(0, len(moves), 2):
        move_num = (i // 2) + 1
        white_move = moves[i]
        black_move = moves[i+1] if i + 1 < len(moves) else ""
        items.append({
            "number": f"{move_num}.",
            "white": white_move,
            "black": black_move
        })
    return items

def get_resolved_value(slot):
    """Safely extracts the first resolved value from an Alexa slot."""
    if not slot or not slot.resolutions or not slot.resolutions.resolutions_per_authority:
        return slot.value if slot else None
        
    for resolution in slot.resolutions.resolutions_per_authority:
        if resolution.status.code.value == "ER_SUCCESS_MATCH":
            return resolution.values[0].value.name
            
    return slot.value

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
        attr["move_history"] = []
        
        speech_text = data["WELCOME_MSG"]
        response_builder = handler_input.response_builder.speak(speech_text).ask(speech_text)
        
        # Add APL if supported
        directive = get_apl_directive(handler_input, type="menu")
        if directive:
            response_builder.add_directive(directive)
            
        return response_builder.response

class SwitchModeIntentHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        return is_intent_name("SwitchModeIntent")(handler_input)

    def handle(self, handler_input):
        data = handler_input.attributes_manager.request_attributes["_"]
        attr = handler_input.attributes_manager.session_attributes
        
        slot = handler_input.request_envelope.request.intent.slots.get("mode")
        mode = get_resolved_value(slot)
        
        logger.info(f"SwitchModeIntent received. Slot value: {slot.value if slot else 'None'}, Resolved mode: {mode}")
        
        if not mode or mode not in ["matches", "puzzles", "squares"]:
            # Better clarification instead of just switching
            speech_text = data.get("HELP_MSG", "You can play a Match, practice with Puzzles, or train your visualization with Squares. Which one?")
            return handler_input.response_builder.speak(speech_text).ask(speech_text).response
            
        if mode != "squares":
            attr.pop("current_square", None)

        attr["mode"] = mode

        if mode == "squares":
            attr["squares_history"] = {}
            attr["squares_correct_count"] = 0
            attr["squares_start_timestamp"] = time.time()
            
            all_squares = [f"{f}{r}" for f in "abcdefgh" for r in "12345678"]
            square = random.choice(all_squares)
            attr["current_square"] = square
            attr["start_time"] = time.time()
            speech_text = data["SQUARES_MODE_START"].format(square=square)
            
            response_builder = handler_input.response_builder.speak(speech_text).ask(speech_text)
            squares_info = {
                "boardUrl": get_board_image_url(highlight=square), 
                "feedback": "",
                "isCorrect": True,
                "currentQuestion": data["SQUARES_MODE_START"].format(square=square).split('?')[-1].strip() or square,
                "timeText": "",
                "ratingNumber": 0
            }
            directive = get_apl_directive(handler_input, engine=squares_info, type="squares")
            if directive:
                response_builder.add_directive(directive)
            return response_builder.response
        
        if mode == "puzzles":
            # Just trigger puzzle logic
            return PuzzleIntentHandler().handle(handler_input)
            
        if mode == "matches":
            engine = BoardManager()
            attr["board_fen"] = engine.get_fen()
            attr["move_history"] = []
        else:
            engine = BoardManager(attr.get("board_fen"))
            
        mode_names = {
            "matches": data.get("MENU_MATCHES", "Matches"),
            "puzzles": data.get("MENU_PUZZLES", "Puzzles"),
            "squares": data.get("MENU_SQUARES", "Squares")
        }
        display_mode = mode_names.get(mode, mode)
        msg_template = data.get("MODE_SWITCHED", "Switched to {mode} mode.")
        speech_text = msg_template.format(mode=display_mode)
        response_builder = handler_input.response_builder.speak(speech_text).ask(data["YOUR_MOVE"])
        directive = get_apl_directive(handler_input, engine, "", type="matches")
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
        success, engine_move = engine.make_move(san_move)
        
        if success:
            history = attr.get("move_history", [])
            history.append(engine_move)
            attr["move_history"] = history
        
        if not success:
            logger.info(f"Invalid move attempted: {san_move} - {error_msg}")
            speech_text = data["INVALID_MOVE_RESPONSE"].format(move=san_move, error=error_msg)
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
                speech_text = data["CORRECT_ANSWER"] + " " + data["READY_FOR_NEXT"]
                attr["puzzle_solved"] = True
            else:
                speech_text = data["WRONG_ANSWER"]
            
            response_builder = handler_input.response_builder.speak(speech_text).ask(data["YOUR_MOVE"])
            
            localized_solution = get_localized_move(solution, data)
            puzzle_info = {
                "fen": engine.get_fen(),
                "description": attr.get("puzzle_description", ""),
                "feedback": data["CORRECT_ANSWER"] if attr.get("puzzle_solved") else data["WRONG_ANSWER"],
                "subtitle": data["SOLUTION_LABEL"].format(move=localized_solution) if attr.get("puzzle_solved") else data["TRY_SOLVE"]
            }
            
            directive = get_apl_directive(handler_input, engine=puzzle_info, type="puzzles")
            if directive:
                response_builder.add_directive(directive)
            return response_builder.response
        
        # Execute AI move (Matches mode)
        if engine.is_game_over():
            speech_text = data["REFLECT_MOVE"].format(piece=piece, square=square) + " " + engine.get_game_result()
        else:
            ai_move = engine.get_ai_move()
            
            # Record AI move in history
            history = attr.get("move_history", [])
            history.append(ai_move)
            attr["move_history"] = history

            localized_ai_move = get_localized_move(ai_move, data)
            ai_text = data["AI_MOVE_RESPONSE"].format(move=localized_ai_move)
            speech_text = data["REFLECT_MOVE"].format(piece=piece, square=square) + " " + ai_text
            
            if engine.is_game_over():
                speech_text += " " + engine.get_game_result()
        
        # Save board back to session
        attr["board_fen"] = engine.get_fen()
        
        response_builder = handler_input.response_builder.speak(speech_text).ask(data["YOUR_MOVE"])
        
        # Add APL if supported
        is_spanish = "Resuelve" in data.get("SOLVE_PUZZLE", "")
        last_move_text = f"Tú: {piece} a {square}" if is_spanish else f"You: {piece} to {square}"
        if not engine.is_game_over():
            localized_ai_move = get_localized_move(ai_move, data)
            last_move_text += f" | IA: {localized_ai_move}" if is_spanish else f" | AI: {ai_move}"
            
        directive = get_apl_directive(handler_input, engine, last_move_text, type="matches")
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
        
        user_color = get_resolved_value(handler_input.request_envelope.request.intent.slots["color"])
        current_square = attr.get("current_square")
        correct_color = get_square_color(current_square)
        
        is_correct = user_color and user_color.lower() == correct_color
        
        # Track history
        history = attr.get("squares_history", {})
        history[current_square] = "C" if is_correct else "W"
        attr["squares_history"] = history
        if is_correct:
            attr["squares_correct_count"] = attr.get("squares_correct_count", 0) + 1

        # Calculate time taken for THIS square
        now = time.time()
        elapsed_time = round(now - attr.get("start_time", now), 1)
        last_time = attr.get("last_time")
        arrow = ""
        if last_time is not None:
            if elapsed_time < last_time:
                arrow = "↓"
            elif elapsed_time > last_time:
                arrow = "↑"
        attr["last_time"] = elapsed_time
        attr["start_time"] = now

        # Convert history to string for server
        squares_param = ",".join([f"{k}:{v}" for k, v in history.items()])
        
        color_green = "#2E7D32"
        color_red = "#C62828"
        
        # Determine color for time based on trend
        time_color = color_green if last_time is None or elapsed_time <= last_time else color_red
        time_text = f"<font color='{time_color}'>{data['TIME_TAKEN_LABEL'].format(time=elapsed_time, arrow=arrow)}</font>"
        
        # Check if completed
        all_squares = [f"{f}{r}" for f in "abcdefgh" for r in "12345678"]
        remaining = [s for s in all_squares if s not in history]
        
        if not remaining:
            # Completion!
            total_time_seconds = int(now - attr.get("squares_start_timestamp", now))
            minutes = total_time_seconds // 60
            seconds = total_time_seconds % 60
            time_str = f"{minutes}m {seconds}s" if minutes > 0 else f"{seconds}s"
            
            correct_count = attr.get("squares_correct_count", 0)
            accuracy = int((correct_count / 64) * 100)
            
            speech_text = data.get("SQUARES_COMPLETED", "Congratulations! You have completed the board.") + " "
            speech_text += data.get("SQUARES_SUMMARY", "Total time: {time}. Accuracy: {accuracy}%. Would you like to play again?").format(
                time=time_str, accuracy=accuracy)
            
            # Clear state so user can restart or switch mode
            attr["mode"] = "squares_summary" # Temporary mode to handle Yes/No
            
            response_builder = handler_input.response_builder.speak(speech_text).ask(speech_text)
            
            squares_info = {
                "boardUrl": get_board_image_url(squares=squares_param),
                "feedback": f"<font color='{color_green}'>{data['SQUARES_COMPLETED']}</font>",
                "isCorrect": True,
                "currentQuestion": data.get("SQUARES_SUMMARY_TITLE", "Session Summary"),
                "timeText": f"Time: {time_str} | Accuracy: {accuracy}%",
                "ratingNumber": 5 if accuracy == 100 else (accuracy // 20)
            }
            
            directive = get_apl_directive(handler_input, engine=squares_info, type="squares")
            if directive:
                response_builder.add_directive(directive)
            return response_builder.response

        # Not completed, get next square
        new_square = random.choice(remaining)
        attr["current_square"] = new_square
        
        feedback_msg = data['CORRECT_ANSWER'] if is_correct else data['WRONG_ANSWER']
        speech_text = f"{feedback_msg} {data['NEXT_SQUARE'].format(square=new_square)}"
        feedback_text = f"<font color='{color_green if is_correct else color_red}'>{feedback_msg}</font>"
        
        # Rating logic for correct answers
        if is_correct:
            if elapsed_time < 10:
                rating_number = 5
            else:
                rating_number = max(0, 5.0 - ((elapsed_time - 10) // 5 + 1) * 0.5)
        else:
            rating_number = 0
            
        response_builder = handler_input.response_builder.speak(speech_text).ask(speech_text)
        
        squares_info = {
            "boardUrl": get_board_image_url(highlight=new_square, squares=squares_param),
            "feedback": feedback_text,
            "isCorrect": is_correct,
            "currentQuestion": data["SQUARES_MODE_START"].format(square=new_square).split('?')[-1].strip() or new_square,
            "timeText": time_text,
            "ratingNumber": rating_number
        }
        
        directive = get_apl_directive(handler_input, engine=squares_info, type="squares")
        if directive:
            response_builder.add_directive(directive)
            
        return response_builder.response

class PuzzleIntentHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        if is_intent_name("PuzzleIntent")(handler_input):
            return True
            
        if is_intent_name("SwitchModeIntent")(handler_input):
            slot = handler_input.request_envelope.request.intent.slots.get("mode")
            return get_resolved_value(slot) == "puzzles"
            
        return False

    def handle(self, handler_input):
        data = handler_input.attributes_manager.request_attributes["_"]
        attr = handler_input.attributes_manager.session_attributes
        locale = handler_input.request_envelope.request.locale
        is_spanish = locale.startswith("es")
        
        current_puzzle_id = attr.get("puzzle_id")
        puzzles = get_puzzles()
        all_puzzles = puzzles["easy"] + puzzles["medium"]
        
        # Try to find a different puzzle if we are already in puzzles mode
        available_puzzles = [p for p in all_puzzles if p["id"] != current_puzzle_id]
        if not available_puzzles:
            available_puzzles = all_puzzles
            
        puzzle = random.choice(available_puzzles)
        
        # Determine localized description
        puzzle_desc = puzzle.get("description_es") if is_spanish else puzzle.get("description")
        if not puzzle_desc:
            puzzle_desc = puzzle.get("description")
            
        # Determine greeting
        if attr.get("mode") == "puzzles":
            if attr.get("puzzle_solved"):
                speech_text = data["NEXT_PUZZLE"].format(description=puzzle_desc)
            else:
                # If they just asked for a puzzle while in the middle of one, maybe they want a new one or just a reminder
                speech_text = data["PUZZLE_RETRY"].format(description=puzzle_desc)
        else:
            speech_text = data["PUZZLES_MODE_START"].format(description=puzzle_desc)
            
        attr["mode"] = "puzzles"
        attr["board_fen"] = puzzle["fen"]
        attr["puzzle_solution"] = puzzle["solution"]
        attr["puzzle_id"] = puzzle["id"]
        attr["puzzle_solved"] = False
        attr["puzzle_description"] = puzzle_desc
        
        engine = BoardManager(puzzle["fen"])
        
        # Add verbal description if APL is not supported
        interfaces = handler_input.request_envelope.context.system.device.supported_interfaces
        if interfaces.alexa_presentation_apl is None:
            speech_text += " " + get_verbal_board_description(engine, data)
            
        response_builder = handler_input.response_builder.speak(speech_text).ask(speech_text)
        
        puzzle_info = {
            "fen": puzzle["fen"],
            "description": puzzle_desc,
            "feedback": "",
            "subtitle": data["SOLVE_PUZZLE"]
        }
        
        directive = get_apl_directive(handler_input, engine=puzzle_info, type="puzzles")
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
        attr = handler_input.attributes_manager.session_attributes
        mode = attr.get("mode", "matches")
        
        speech_key = f"GOODBYE_{mode.upper()}"
        speech_text = data.get(speech_key, data["GOODBYE_MSG"])
            
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

class YesIntentHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        return is_intent_name("AMAZON.YesIntent")(handler_input)

    def handle(self, handler_input):
        attr = handler_input.attributes_manager.session_attributes
        mode = attr.get("mode")
        
        if mode == "squares_summary":
            # Restart Squares mode
            return SwitchModeIntentHandler().handle(handler_input)
            
        if mode == "puzzles":
            return PuzzleIntentHandler().handle(handler_input)
            
        # Default behavior if not in a specific confirmable state
        data = handler_input.attributes_manager.request_attributes["_"]
        speech_text = data["HELP_MSG"]
        return handler_input.response_builder.speak(speech_text).ask(speech_text).response

class NoIntentHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        return is_intent_name("AMAZON.NoIntent")(handler_input)

    def handle(self, handler_input):
        data = handler_input.attributes_manager.request_attributes["_"]
        attr = handler_input.attributes_manager.session_attributes
        mode = attr.get("mode", "matches")
        
        if mode == "squares_summary":
            # Return to menu
            attr["mode"] = "none"
            speech_text = data["WELCOME_MSG"]
            response_builder = handler_input.response_builder.speak(speech_text).ask(speech_text)
            directive = get_apl_directive(handler_input, type="menu")
            if directive:
                response_builder.add_directive(directive)
            return response_builder.response

        speech_key = f"GOODBYE_{mode.upper()}"
        speech_text = data.get(speech_key, data["GOODBYE_MSG"])
        
        return handler_input.response_builder.speak(speech_text).response

class UserEventHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        return is_request_type("Alexa.Presentation.APL.UserEvent")(handler_input)

    def handle(self, handler_input):
        data = handler_input.attributes_manager.request_attributes["_"]
        request = handler_input.request_envelope.request
        arguments = request.arguments
        
        if arguments and arguments[0] == "SwitchModeIntent":
            mode = arguments[1]
            
            # Update session attributes
            attr = handler_input.attributes_manager.session_attributes
            attr["mode"] = mode
            
            # Map mode to localized display name for feedback
            mode_name_key = f"MENU_{mode.upper()}"
            mode_name = data.get(mode_name_key, mode)
            
            # Immediately trigger the mode switch response
            # This ensures the user hears confirmation of their tap
            return SwitchModeIntentHandler().handle(handler_input)
            
        if arguments and arguments[0] == "goBack":
            # Return to main menu
            attr = handler_input.attributes_manager.session_attributes
            attr["mode"] = "none"
            
            speech_text = data["WELCOME_MSG"]
            response_builder = handler_input.response_builder.speak(speech_text).ask(speech_text)
            
            directive = get_apl_directive(handler_input, type="menu")
            if directive:
                response_builder.add_directive(directive)
            return response_builder.response
            
        return handler_input.response_builder.response

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
sb.add_request_handler(UserEventHandler())
sb.add_request_handler(SwitchModeIntentHandler())
sb.add_request_handler(SquareColorIntentHandler())
sb.add_request_handler(PuzzleIntentHandler())
sb.add_request_handler(MoveIntentHandler())
sb.add_request_handler(HelpIntentHandler())
sb.add_request_handler(YesIntentHandler())
sb.add_request_handler(NoIntentHandler())
sb.add_request_handler(CancelOrStopIntentHandler())
sb.add_request_handler(FallbackIntentHandler())
sb.add_request_handler(SessionEndedRequestHandler())

sb.add_exception_handler(CatchAllExceptionHandler())

sb.add_global_request_interceptor(LocalizationInterceptor())

lambda_handler = sb.lambda_handler()
