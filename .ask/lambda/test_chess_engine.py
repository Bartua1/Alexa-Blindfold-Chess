import unittest
from chess_engine.board_manager import BoardManager

class TestChessEngine(unittest.TestCase):
    def test_initial_board(self):
        engine = BoardManager()
        self.assertEqual(engine.board.fen(), "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1")

    def test_make_move_legal(self):
        engine = BoardManager()
        success, uci = engine.make_move("e4")
        self.assertTrue(success)
        self.assertEqual(uci, "e2e4")

    def test_make_move_illegal(self):
        engine = BoardManager()
        success, error = engine.make_move("e5") # Illegal second move for white
        self.assertFalse(success)
        self.assertEqual(error, "Illegal move")

    def test_ai_move(self):
        engine = BoardManager()
        engine.make_move("e4")
        ai_move = engine.get_ai_move()
        self.assertIsNotNone(ai_move)
        # Check if AI actually made a move (it's black's turn now)
        self.assertEqual(engine.board.turn, True) # White's turn again after AI move

    def test_parse_slots(self):
        self.assertEqual(BoardManager.parse_alexa_slots("pawn", "e4"), "e4")
        self.assertEqual(BoardManager.parse_alexa_slots("knight", "f3"), "Nf3")
        self.assertEqual(BoardManager.parse_alexa_slots("Peón", "e4"), "e4")
        self.assertEqual(BoardManager.parse_alexa_slots("Caballo", "f3"), "Nf3")

if __name__ == '__main__':
    unittest.main()
