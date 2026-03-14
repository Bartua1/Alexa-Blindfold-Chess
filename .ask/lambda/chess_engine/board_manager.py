import chess
import random

class BoardManager:
    def __init__(self, fen=None):
        if fen:
            self.board = chess.Board(fen)
        else:
            self.board = chess.Board()

    def get_fen(self):
        return self.board.fen()

    def make_move(self, move_san):
        """Attempts to make a move from SAN string (e.g., 'e4', 'Nf3')."""
        try:
            move = self.board.parse_san(move_san)
            self.board.push(move)
            return True, move.uci()
        except Exception:
            return False, "Illegal move"

    def get_ai_move(self):
        """Generates a random legal move for the AI."""
        legal_moves = list(self.board.legal_moves)
        if not legal_moves:
            return None
        move = random.choice(legal_moves)
        san_move = self.board.san(move)
        self.board.push(move)
        return san_move

    def is_game_over(self):
        return self.board.is_game_over()

    def get_game_result(self):
        if self.board.is_checkmate():
            return "CHECKMATE"
        if self.board.is_stalemate():
            return "STALEMATE"
        if self.board.is_insufficient_material():
            return "DRAW_INSUFFICIENT_MATERIAL"
        return "ONGOING"

    @staticmethod
    def parse_alexa_slots(piece, square):
        """
        Converts Alexa slots to SAN.
        Handles None values and defaults piece to empty string (pawn).
        """
        piece_map = {
            "pawn": "",
            "knight": "N",
            "bishop": "B",
            "rook": "R",
            "queen": "Q",
            "king": "K",
            # Spanish mapping
            "peón": "",
            "caballo": "N",
            "alfil": "B",
            "torre": "R",
            "reina": "Q",
            "rey": "K"
        }
        
        # Handle missing slots
        piece_val = piece.lower() if piece else "pawn"
        square_val = square.lower() if square else ""
        
        prefix = piece_map.get(piece_val, "")
        return f"{prefix}{square_val}"

    def get_piece_positions(self):
        """Returns a dictionary of pieces and their squares, grouped by color."""
        positions = {"white": [], "black": []}
        for square in chess.SQUARES:
            piece = self.board.piece_at(square)
            if piece:
                color = "white" if piece.color == chess.WHITE else "black"
                positions[color].append({
                    "piece": piece.symbol().upper(),
                    "square": chess.square_name(square)
                })
        return positions
