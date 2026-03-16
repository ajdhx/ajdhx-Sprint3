import unittest
from peg_solitaire_logic import PegSolitaireGame


class TestPegSolitaireGame(unittest.TestCase):

    # AC 1.1 – stored size matches input
    def test_ac1_1_record_board_size(self):
        game = PegSolitaireGame("English", 9)
        self.assertEqual(game.size, 9)

        game2 = PegSolitaireGame("Diamond", 5)
        self.assertEqual(game2.size, 5)

    # AC 1.2 – generated board dimensions match stored size
    def test_ac1_2_board_size_reflected(self):
        game = PegSolitaireGame("English", 7)
        self.assertEqual(len(game.board), 7)
        self.assertEqual(len(game.board[0]), 7)

        game2 = PegSolitaireGame("Diamond", 5)
        self.assertEqual(len(game2.board), 5)
        self.assertEqual(len(game2.board[0]), 5)

    # AC 2.1 – stored type matches input
    def test_ac2_1_record_board_type(self):
        game = PegSolitaireGame("English", 7)
        self.assertEqual(game.board_type, "English")

        game2 = PegSolitaireGame("Diamond", 5)
        self.assertEqual(game2.board_type, "Diamond")

        game3 = PegSolitaireGame("Hexagon", 5)
        self.assertEqual(game3.board_type, "Hexagon")

    # AC 2.2 – each type produces a distinct board layout
    def test_ac2_2_board_type_reflected(self):
        english = PegSolitaireGame("English", 7)
        diamond = PegSolitaireGame("Diamond", 7)
        hexagon = PegSolitaireGame("Hexagon", 7)

        # (0, 2) is a valid peg on English but invalid on Diamond
        self.assertEqual(english.board[0][2], 1)
        self.assertEqual(diamond.board[0][2], 0)

        # Peg counts differ across all three types (32, 24, 36)
        self.assertNotEqual(english.get_peg_count(), diamond.get_peg_count())
        self.assertNotEqual(diamond.get_peg_count(), hexagon.get_peg_count())
        self.assertNotEqual(english.get_peg_count(), hexagon.get_peg_count())

    # AC 3.1 – board has pegs, a starting hole, and at least one legal move
    def test_ac3_1_board_generated(self):
        game = PegSolitaireGame("English", 7)
        center = game.size // 2

        self.assertGreater(game.get_peg_count(), 0)
        self.assertEqual(game.board[center][center], 2)  # center starts empty
        self.assertFalse(game.is_game_over())

    # AC 4.1 – valid move updates the board correctly
    def test_ac4_1_valid_move_executed(self):
        game = PegSolitaireGame("English", 7)
        # Peg at (1,3) jumps over (2,3) into empty center (3,3)
        self.assertTrue(game.is_valid_move(1, 3, 3, 3))
        self.assertTrue(game.make_move(1, 3, 3, 3))

        self.assertEqual(game.board[1][3], 2)  # start is now empty
        self.assertEqual(game.board[2][3], 2)  # jumped peg removed
        self.assertEqual(game.board[3][3], 1)  # peg placed at destination

        self.assertFalse(game.is_valid_move(1, 3, 3, 3))   # already moved
        self.assertFalse(game.is_valid_move(0, 3, -2, 3))  # out of bounds
        self.assertFalse(game.is_valid_move(2, 2, 4, 4))   # diagonal invalid

    # AC 4.2 – invalid move is rejected and board is unchanged  (ChatGPT test #1)
    def test_ac4_2_invalid_move_rejected(self):
        game = PegSolitaireGame("English", 7)

        result = game.make_move(2, 3, 3, 3)  # only one space away

        self.assertFalse(result)
        self.assertEqual(game.board[2][3], 1)  # original peg still there
        self.assertEqual(game.board[3][3], 2)  # center still empty

    # AC 5.1 – one peg remaining means the player has won  (ChatGPT test #2)
    def test_ac5_1_player_wins(self):
        game = PegSolitaireGame("English", 7)

        # Clear the board, leave a single peg
        for r in range(game.size):
            for c in range(game.size):
                if game.board[r][c] != 0:
                    game.board[r][c] = 2
        game.board[3][3] = 1

        self.assertTrue(game.has_won())
        self.assertTrue(game.is_game_over())  # no moves left either

    # AC 5.2 – multiple pegs with no legal moves means the player has lost
    def test_ac5_2_player_loses(self):
        # A size-3 English board starts with pegs but no jumpable moves
        game = PegSolitaireGame("English", 3)
        self.assertTrue(game.is_game_over())
        self.assertFalse(game.has_won())


if __name__ == '__main__':
    unittest.main()
