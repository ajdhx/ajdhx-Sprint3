import unittest
# [Sprint 3 Change] Imported AutomatedGame for our new automated unit tests. ManualGame aliases to PegSolitaireGame for backward compatibility in tests.
from peg_solitaire_logic import ManualGame as PegSolitaireGame, AutomatedGame


class TestPegSolitaireGame(unittest.TestCase):

    # US 1, AC 1.1 – stored size and type matches input
    def test_us1_ac1_1_record_board_settings(self):
        game = PegSolitaireGame("English", 9)
        self.assertEqual(game.size, 9)

        game2 = PegSolitaireGame("Diamond", 5)
        self.assertEqual(game2.size, 5)

    # US 1, AC 1.2 – generated board dimensions match stored size
    def test_us1_ac1_2_board_size_reflected(self):
        game = PegSolitaireGame("English", 7)
        self.assertEqual(len(game.get_board()), 7)
        self.assertEqual(len(game.get_board()[0]), 7)

        game2 = PegSolitaireGame("Diamond", 5)
        self.assertEqual(len(game2.get_board()), 5)
        self.assertEqual(len(game2.get_board()[0]), 5)

    # US 1, AC 1.3 – stored type matches input
    def test_us1_ac1_3_record_board_type(self):
        game = PegSolitaireGame("English", 7)
        self.assertEqual(game.board_type, "English")

        game2 = PegSolitaireGame("Diamond", 5)
        self.assertEqual(game2.board_type, "Diamond")

        game3 = PegSolitaireGame("Hexagon", 5)
        self.assertEqual(game3.board_type, "Hexagon")

    # US 1, AC 1.4 – each type produces a distinct board layout
    def test_us1_ac1_4_board_type_reflected(self):
        english = PegSolitaireGame("English", 7)
        diamond = PegSolitaireGame("Diamond", 7)
        hexagon = PegSolitaireGame("Hexagon", 7)

        # (0, 2) is a valid peg on English but invalid on Diamond
        self.assertEqual(english.get_board()[0][2], 1)
        self.assertEqual(diamond.get_board()[0][2], 0)

        # Peg counts differ across all three types (32, 24, 36)
        self.assertNotEqual(english.get_peg_count(), diamond.get_peg_count())
        self.assertNotEqual(diamond.get_peg_count(), hexagon.get_peg_count())
        self.assertNotEqual(english.get_peg_count(), hexagon.get_peg_count())

    # US 3, AC 3.1 – board has pegs, a starting hole, and at least one legal move
    def test_us3_ac3_1_board_generated(self):
        game = PegSolitaireGame("English", 7)
        center = game.size // 2

        self.assertGreater(game.get_peg_count(), 0)
        self.assertEqual(game.get_board()[center][center], 2)  # center starts empty
        self.assertFalse(game.is_game_over())

    # US 4, AC 4.1 – valid move updates the board correctly
    def test_us4_ac4_1_valid_move_executed(self):
        game = PegSolitaireGame("English", 7)
        # Peg at (1,3) jumps over (2,3) into empty center (3,3)
        self.assertTrue(game.is_valid_move(1, 3, 3, 3))
        self.assertTrue(game.make_move(1, 3, 3, 3))

        self.assertEqual(game.get_board()[1][3], 2)  # start is now empty
        self.assertEqual(game.get_board()[2][3], 2)  # jumped peg removed
        self.assertEqual(game.get_board()[3][3], 1)  # peg placed at destination

        self.assertFalse(game.is_valid_move(1, 3, 3, 3))   # already moved
        self.assertFalse(game.is_valid_move(0, 3, -2, 3))  # out of bounds
        self.assertFalse(game.is_valid_move(2, 2, 4, 4))   # diagonal invalid

    # US 4, AC 4.2 – invalid move is rejected and board is unchanged
    def test_us4_ac4_2_invalid_move_rejected(self):
        game = PegSolitaireGame("English", 7)

        result = game.make_move(2, 3, 3, 3)  # only one space away

        self.assertFalse(result)
        self.assertEqual(game.get_board()[2][3], 1)  # original peg still there
        self.assertEqual(game.get_board()[3][3], 2)  # center still empty

    # US 5, AC 5.1 – one peg remaining means the player has won
    def test_us5_ac5_1_player_wins(self):
        game = PegSolitaireGame("English", 7)

        # Clear the board, leave a single peg
        for r in range(game.size):
            for c in range(game.size):
                if game._board[r][c] != 0:
                    game._board[r][c] = 2
        game._board[3][3] = 1

        self.assertTrue(game.has_won())
        self.assertTrue(game.is_game_over())  # no moves left either

    # US 5, AC 5.2 – multiple pegs with no legal moves means the player has lost
    def test_us5_ac5_2_player_loses(self):
        # A size-3 English board starts with pegs but no jumpable moves
        game = PegSolitaireGame("English", 3)
        self.assertTrue(game.is_game_over())
        self.assertFalse(game.has_won())


# [Sprint 3 Change] Added a test suite specifically addressing the AutomatedGame mechanics and requirements.
class TestAutomatedGame(unittest.TestCase):

    # US 6, AC 6.1 - Automated moves are retrieved and executed correctly
    def test_us6_ac6_1_auto_move(self):
        game = AutomatedGame("English", 7)
        result = game.make_auto_move()
        self.assertTrue(result or game.is_game_over())

    # US 7, AC 7.1 - Ensure the automated loop reaches an end state
    def test_us7_ac7_1_auto_game_ends(self):
        game = AutomatedGame("English", 3)
        while game.make_auto_move():
            pass
        self.assertTrue(game.is_game_over())


if __name__ == '__main__':
    unittest.main(verbosity=2)
