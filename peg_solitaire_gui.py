import tkinter as tk
from tkinter import messagebox
from peg_solitaire_logic import PegSolitaireGame


class PegSolitaireGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Peg Solitaire")

        self.game = PegSolitaireGame("English", 7)
        self.selected_pos = None

        self._setup_ui()
        self.draw_board()

    def _setup_ui(self):
        self.root.columnconfigure(1, weight=1)
        self.root.rowconfigure(0, weight=1)

        # Left: board type selector
        left_frame = tk.Frame(self.root)
        left_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nw")

        tk.Label(left_frame, text="Board Type").pack(anchor="w")

        self.board_type_var = tk.StringVar(value="English")
        for name in ("English", "Hexagon", "Diamond"):
            tk.Radiobutton(
                left_frame, text=name,
                variable=self.board_type_var, value=name,
                command=self.new_game
            ).pack(anchor="w")

        # Centre: game canvas
        center_frame = tk.Frame(self.root)
        center_frame.grid(row=0, column=1, padx=10, pady=10)

        self.canvas_size = 500
        self.canvas = tk.Canvas(
            center_frame,
            width=self.canvas_size, height=self.canvas_size,
            bg="white"
        )
        self.canvas.pack()
        self.canvas.bind("<Button-1>", self.on_canvas_click)

        # Right: size entry and new-game button
        right_frame = tk.Frame(self.root)
        right_frame.grid(row=0, column=2, padx=10, pady=10, sticky="ne")

        size_frame = tk.Frame(right_frame)
        size_frame.pack(pady=(0, 20), anchor="e")
        tk.Label(size_frame, text="Board size").pack(side="left")

        self.size_var = tk.StringVar(value="7")
        size_entry = tk.Entry(size_frame, textvariable=self.size_var, width=3)
        size_entry.pack(side="left")
        size_entry.bind("<Return>", lambda event: self.new_game())

        tk.Button(right_frame, text="New Game", command=self.new_game).pack(anchor="e")

    def new_game(self):
        """Start a fresh game with the current type and size settings."""
        board_type = self.board_type_var.get()
        try:
            size_val = int(self.size_var.get())
            if not 3 <= size_val <= 15:
                raise ValueError
        except ValueError:
            messagebox.showerror("Invalid Size", "Please enter an integer from 3 to 15.")
            return

        self.game = PegSolitaireGame(board_type, size_val)
        self.selected_pos = None
        self.draw_board()

    def draw_board(self):
        """Redraw the entire board on the canvas."""
        self.canvas.delete("all")
        size = self.game.size

        padding = 40
        self.cell_size = (self.canvas_size - 2 * padding) // size
        actual = self.cell_size * size
        self.offset_x = (self.canvas_size - actual) // 2
        self.offset_y = (self.canvas_size - actual) // 2

        for r in range(size):
            for c in range(size):
                val = self.game.board[r][c]
                if val == 0:
                    continue

                cx = self.offset_x + c * self.cell_size
                cy = self.offset_y + r * self.cell_size

                if self.game.board_type == "Hexagon":
                    cx += (r * self.cell_size // 2) - (size * self.cell_size // 4)

                self.canvas.create_rectangle(
                    cx, cy, cx + self.cell_size, cy + self.cell_size,
                    outline="black", fill="white"
                )

                center_x = cx + self.cell_size // 2
                center_y = cy + self.cell_size // 2
                radius = self.cell_size * 0.3

                if val == 1:  # peg
                    color = "red" if self.selected_pos == (r, c) else "black"
                    self.canvas.create_oval(
                        center_x - radius, center_y - radius,
                        center_x + radius, center_y + radius,
                        fill=color
                    )
                elif val == 2:  # empty hole
                    self.canvas.create_oval(
                        center_x - radius, center_y - radius,
                        center_x + radius, center_y + radius,
                        outline="black"
                    )

    def on_canvas_click(self, event):
        """Handle a click on the canvas: select a peg or attempt a move."""
        x, y = event.x, event.y
        size = self.game.size
        clicked_r = clicked_c = -1

        for r in range(size):
            for c in range(size):
                if self.game.board[r][c] == 0:
                    continue

                cx = self.offset_x + c * self.cell_size
                cy = self.offset_y + r * self.cell_size

                if self.game.board_type == "Hexagon":
                    cx += (r * self.cell_size // 2) - (size * self.cell_size // 4)

                if cx <= x <= cx + self.cell_size and cy <= y <= cy + self.cell_size:
                    clicked_r, clicked_c = r, c
                    break
            if clicked_r != -1:
                break

        if clicked_r == -1:
            return

        val = self.game.board[clicked_r][clicked_c]
        if val == 1:
            self.selected_pos = (clicked_r, clicked_c)
            self.draw_board()
        elif val == 2 and self.selected_pos is not None:
            if self.game.make_move(self.selected_pos[0], self.selected_pos[1], clicked_r, clicked_c):
                self.selected_pos = None
                self.draw_board()
                if self.game.has_won():
                    messagebox.showinfo("Game Over", "You Win!")
                elif self.game.is_game_over():
                    messagebox.showinfo("Game Over", "No more valid moves.")


def main():
    root = tk.Tk()
    app = PegSolitaireGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
