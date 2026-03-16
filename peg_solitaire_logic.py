class PegSolitaireGame:
    def __init__(self, board_type="English", size=7):
        self.board_type = board_type
        self.size = size
        self.board = []
        self._initialize_board()

    def _initialize_board(self):
        """Set up the board grid based on type and size.

        Cell values: 0 = invalid, 1 = peg, 2 = empty hole.
        """
        self.board = [[0 for _ in range(self.size)] for _ in range(self.size)]

        if self.board_type == "English":
            # Cross shape: corners (one-third of each side) are invalid.
            one_third = self.size // 3
            two_thirds = self.size - one_third

            for r in range(self.size):
                for c in range(self.size):
                    in_corner = (
                        (r < one_third and c < one_third)
                        or (r < one_third and c >= two_thirds)
                        or (r >= two_thirds and c < one_third)
                        or (r >= two_thirds and c >= two_thirds)
                    )
                    self.board[r][c] = 0 if in_corner else 1

        elif self.board_type == "Diamond":
            # Diamond shape: cells within Manhattan distance of center are valid.
            center = self.size // 2
            for r in range(self.size):
                for c in range(self.size):
                    if abs(r - center) + abs(c - center) <= center:
                        self.board[r][c] = 1

        elif self.board_type == "Hexagon":
            # Hexagonal shape using axial coordinates mapped to a square grid.
            center = self.size // 2
            for r in range(self.size):
                for c in range(self.size):
                    dq, dr = r - center, c - center
                    if abs(dq) <= center and abs(dr) <= center and abs(dq + dr) <= center:
                        self.board[r][c] = 1

        # Center cell starts as an empty hole.
        center = self.size // 2
        self.board[center][center] = 2

    def is_valid_position(self, r, c):
        """Return True if (r, c) is within bounds and not an invalid cell."""
        return 0 <= r < self.size and 0 <= c < self.size and self.board[r][c] != 0

    def get_peg(self, r, c):
        """Return the cell value at (r, c), or 0 if out of bounds."""
        if self.is_valid_position(r, c):
            return self.board[r][c]
        return 0

    def is_valid_move(self, start_r, start_c, end_r, end_c):
        """Return True if moving from start to end is a legal jump."""
        if not self.is_valid_position(start_r, start_c) or not self.is_valid_position(end_r, end_c):
            return False

        if self.board[start_r][start_c] != 1 or self.board[end_r][end_c] != 2:
            return False

        dr = end_r - start_r
        dc = end_c - start_c

        if self.board_type in ["English", "Diamond"]:
            # Orthogonal jumps only (2 cells in one axis, 0 in the other).
            if (abs(dr) == 2 and dc == 0) or (dr == 0 and abs(dc) == 2):
                mid_r = start_r + dr // 2
                mid_c = start_c + dc // 2
                return self.board[mid_r][mid_c] == 1

        elif self.board_type == "Hexagon":
            # Orthogonal + two diagonal axial directions.
            valid_jump = (
                (abs(dr) == 2 and dc == 0)
                or (dr == 0 and abs(dc) == 2)
                or (dr == 2 and dc == -2)
                or (dr == -2 and dc == 2)
            )
            if valid_jump:
                mid_r = start_r + dr // 2
                mid_c = start_c + dc // 2
                return self.board[mid_r][mid_c] == 1

        return False

    def make_move(self, start_r, start_c, end_r, end_c):
        """Execute a move if valid; return True on success, False otherwise."""
        if self.is_valid_move(start_r, start_c, end_r, end_c):
            dr = end_r - start_r
            dc = end_c - start_c
            mid_r = start_r + dr // 2
            mid_c = start_c + dc // 2

            self.board[start_r][start_c] = 2  # vacate start
            self.board[mid_r][mid_c] = 2       # remove jumped peg
            self.board[end_r][end_c] = 1       # place peg at destination
            return True
        return False

    def is_game_over(self):
        """Return True if no valid moves remain."""
        moves = [(0, 2), (0, -2), (2, 0), (-2, 0)]
        if self.board_type == "Hexagon":
            moves += [(2, -2), (-2, 2)]

        for r in range(self.size):
            for c in range(self.size):
                if self.board[r][c] == 1:
                    if any(self.is_valid_move(r, c, r + dr, c + dc) for dr, dc in moves):
                        return False
        return True

    def get_peg_count(self):
        """Return the number of pegs currently on the board."""
        return sum(
            self.board[r][c] == 1
            for r in range(self.size)
            for c in range(self.size)
        )

    def has_won(self):
        """Return True if exactly one peg remains."""
        return self.get_peg_count() == 1
