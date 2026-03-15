import unittest
from peg_solitaire_logic import PegSolitaireGame

class TestPegSolitaireGame(unittest.TestCase):

    # AC 1.1 – Record and store board size selection
    # Given: a board size option is selected
    # When:  the game is constructed with that size
    # Then:  the size is stored in the game object
    def test_ac1_1_record_board_size(self):
        game = PegSolitaireGame("English", 9)
        self.assertEqual(game.size, 9)

        game2 = PegSolitaireGame("Diamond", 5)
        self.assertEqual(game2.size, 5)

    # AC 1.2 – Board size chosen is reflected in generation
    # Given: a board size has been selected
    # When:  the game is initialized
    # Then:  the generated board dimensions match the selected size
    def test_ac1_2_board_size_reflected(self):
        game = PegSolitaireGame("English", 7)
        self.assertEqual(len(game.board), 7)
        self.assertEqual(len(game.board[0]), 7)

        game2 = PegSolitaireGame("Diamond", 5)
        self.assertEqual(len(game2.board), 5)
        self.assertEqual(len(game2.board[0]), 5)

    # AC 2.1 – Record and store board type selection
    # Given: a board type option is selected
    # When:  the game is constructed with that type
    # Then:  the type is stored in the game object
    def test_ac2_1_record_board_type(self):
        game = PegSolitaireGame("English", 7)
        self.assertEqual(game.board_type, "English")

        game2 = PegSolitaireGame("Diamond", 5)
        self.assertEqual(game2.board_type, "Diamond")

        game3 = PegSolitaireGame("Hexagon", 5)
        self.assertEqual(game3.board_type, "Hexagon")

    # AC 2.2 – Board type chosen is reflected in generation
    # Given: different board types are selected with the same size
    # When:  the game is initialized
    # Then:  each board has a distinct layout (different invalid-cell arrangements)
    def test_ac2_2_board_type_reflected(self):
        english = PegSolitaireGame("English", 7)
        diamond = PegSolitaireGame("Diamond", 7)
        hexagon = PegSolitaireGame("Hexagon", 7)

        # Cell (0, 2): peg on English (inside the cross arm), invalid on Diamond.
        # This confirms that the board shape genuinely changes with type.
        self.assertEqual(english.board[0][2], 1)   # English: valid cell with peg
        self.assertEqual(diamond.board[0][2], 0)   # Diamond: corner region is invalid

        # Peg counts are all distinct: English=32, Diamond=24, Hexagon=36
        self.assertNotEqual(english.get_peg_count(), diamond.get_peg_count())
        self.assertNotEqual(diamond.get_peg_count(), hexagon.get_peg_count())
        self.assertNotEqual(english.get_peg_count(), hexagon.get_peg_count())

    # AC 3.1 – Solitaire board is generated
    # Given: user input (board type and size)
    # When:  the system initializes the game
    # Then:  a valid Solitaire board is generated with pegs, a starting hole,
    #        and at least one legal move available
    def test_ac3_1_board_generated(self):
        game = PegSolitaireGame("English", 7)

        # Board has pegs
        self.assertGreater(game.get_peg_count(), 0)

        # Center is the starting empty hole (value 2)
        center = game.size // 2
        self.assertEqual(game.board[center][center], 2)

        # Game is not immediately over — at least one legal move exists
        self.assertFalse(game.is_game_over())

    # AC 4.1 – Valid move is executed
    # Given: a legal move exists on an English board
    # When:  the player makes that move
    # Then:  the peg moves, the jumped peg is removed, and the board updates
    def test_ac4_1_valid_move_executed(self):
        game = PegSolitaireGame("English", 7)
        # Center (3,3) is empty; peg at (1,3) jumps over (2,3) to (3,3)
        self.assertTrue(game.is_valid_move(1, 3, 3, 3))
        self.assertTrue(game.make_move(1, 3, 3, 3))

        self.assertEqual(game.board[1][3], 2)  # start is now empty
        self.assertEqual(game.board[2][3], 2)  # jumped peg removed
        self.assertEqual(game.board[3][3], 1)  # destination has peg

        # The same move is no longer valid
        self.assertFalse(game.is_valid_move(1, 3, 3, 3))
        # Out-of-bounds move is invalid
        self.assertFalse(game.is_valid_move(0, 3, -2, 3))
        # Diagonal move is invalid on English
        self.assertFalse(game.is_valid_move(2, 2, 4, 4))

    # AC 4.2 – Invalid move is rejected  (ChatGPT test #1 – modified)
    # Given: the game board is displayed
    # When:  the player selects an invalid destination
    # Then:  the move is rejected and the board state is unchanged
    def test_ac4_2_invalid_move_rejected(self):
        game = PegSolitaireGame("English", 7)

        # Attempt a move that is only one space away (invalid)
        result = game.make_move(2, 3, 3, 3)

        # Move should fail
        self.assertFalse(result)

        # Board should remain unchanged
        self.assertEqual(game.board[2][3], 1)  # original peg still there
        self.assertEqual(game.board[3][3], 2)  # center still empty

    # AC 5.1 – Player wins the game  (ChatGPT test #2 – modified)
    # Given: only one peg remains on the board
    # When:  the win condition is checked
    # Then:  has_won() returns True and no further moves are possible
    def test_ac5_1_player_wins(self):
        game = PegSolitaireGame("English", 7)

        # Manually place exactly one peg on the board
        for r in range(game.size):
            for c in range(game.size):
                if game.board[r][c] != 0:
                    game.board[r][c] = 2  # empty hole

        game.board[3][3] = 1  # one remaining peg

        self.assertTrue(game.has_won())
        # No moves available when only one peg remains
        self.assertTrue(game.is_game_over())

    # AC 5.2 – Player loses the game
    # Given: more than one peg remains but no legal moves exist
    # When:  the game-over condition is checked
    # Then:  is_game_over() returns True and has_won() returns False
    def test_ac5_2_player_loses(self):
        # A size-3 English board has pegs but no jumpable moves from the start
        game = PegSolitaireGame("English", 3)
        self.assertTrue(game.is_game_over())
        self.assertFalse(game.has_won())

if __name__ == '__main__':
    unittest.main()
