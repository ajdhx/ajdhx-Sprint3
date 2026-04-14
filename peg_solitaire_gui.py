import tkinter as tk
from tkinter import messagebox, filedialog
import json
# [Sprint 3 Change] Imported the new subclasses from our refactored class hierarchy.
from peg_solitaire_logic import ManualGame, AutomatedGame
import random


class PegSolitaireGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Peg Solitaire")

        self.game = ManualGame("English", 7)
        self.selected_pos = None

        # [Sprint 4 Change] Initialize recording state variables.
        self.recording_var = tk.BooleanVar(value=False)
        self.record_data = []
        self.is_replaying = False

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

        # [Sprint 3 Change] Added Game Mode UI selector (Manual vs. Automated) for Sprint 3 requirements.
        tk.Label(left_frame, text="Game Mode").pack(anchor="w", pady=(10, 0))

        self.mode_var = tk.StringVar(value="Manual")
        for mode in ("Manual", "Automated"):
            tk.Radiobutton(
                left_frame, text=mode,
                variable=self.mode_var, value=mode,
                command=self.new_game
            ).pack(anchor="w")

        # [Sprint 4 Change] Added Record game checkbox to left frame.
        tk.Checkbutton(
            left_frame, text="Record game",
            variable=self.recording_var,
            command=self.on_toggle_record
        ).pack(anchor="w", pady=(10, 0))

        # Center: game canvas
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
        # [Sprint 3 Change] Added 'Autoplay' and 'Randomize' buttons.
        tk.Button(right_frame, text="Autoplay", command=self.autoplay).pack(anchor="e")
        tk.Button(right_frame, text="Randomize", command=self.randomize).pack(anchor="e")
        # [Sprint 4 Change] Added 'Replay' button.
        tk.Button(right_frame, text="Replay", command=self.replay_game).pack(anchor="e")

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

        mode = self.mode_var.get()

        # [Sprint 3 Change] Instantiate the appropriate subclass based on the selected game mode.
        if mode == "Manual":
            self.game = ManualGame(board_type, size_val)
        else:
            self.game = AutomatedGame(board_type, size_val)

        # [Sprint 4 Change] Reset record data for the new game.
        self.record_data = []
        if self.recording_var.get():
            self._record_setup()

        self.selected_pos = None
        self.draw_board()

    def _record_setup(self):
        """Record the initial board configuration."""
        self.record_data.append({
            "type": "SETUP",
            "board_type": self.game.board_type,
            "size": self.game.size,
            "mode": self.mode_var.get(),
            "board_state": self.game.get_board()
        })

    def _record_event(self, event_type, data):
        """Helper to append an event to record data if recording is enabled."""
        if self.recording_var.get() and not self.is_replaying:
            entry = {"type": event_type}
            entry.update(data)
            self.record_data.append(entry)

    def on_toggle_record(self):
        """Handle toggle of 'Record game' checkbox."""
        if self.recording_var.get():
            # If turned on mid-game, record current setup as the start.
            if not self.record_data:
                self._record_setup()
        else:
            # If turned off, prompt to save what we have.
            self.save_record()

    def save_record(self):
        """Prompt user to save the recorded game to a file."""
        if not self.record_data:
            return

        file_path = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")],
            title="Save Game Record"
        )
        if file_path:
            with open(file_path, 'w') as f:
                # Use a simple text format as requested, but structured (JSON-like)
                # The user asked for "some notation". I'll use a readable format.
                f.write(f"BOARD_TYPE: {self.game.board_type}\n")
                f.write(f"SIZE: {self.game.size}\n")
                f.write(f"MODE: {self.mode_var.get()}\n\n")
                for entry in self.record_data:
                    if entry["type"] == "SETUP":
                        f.write(f"START_STATE: {json.dumps(entry['board_state'])}\n")
                    elif entry["type"] == "MOVE":
                        f.write(f"MOVE: ({entry['start'][0]},{entry['start'][1]}) -> ({entry['end'][0]},{entry['end'][1]})\n")
                    elif entry["type"] == "RANDOMIZE":
                        f.write(f"RANDOMIZE: {json.dumps(entry['board_state'])}\n")
                    elif entry["type"] == "GAME_OVER":
                        f.write(f"RESULT: {entry['result']} (Pegs: {entry['pegs']})\n")
            messagebox.showinfo("Success", "Game record saved.")
            self.record_data = []  # Clear after saving
            self.recording_var.set(False)

    def draw_board(self):
        """Redraw the entire board on the canvas."""
        self.canvas.delete("all")
        size = self.game.size

        padding = 40
        self.cell_size = (self.canvas_size - 2 * padding) // size
        actual = self.cell_size * size
        self.offset_x = (self.canvas_size - actual) // 2
        self.offset_y = (self.canvas_size - actual) // 2

        board = self.game.get_board()
        for r in range(size):
            for c in range(size):
                val = board[r][c]
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

        board = self.game.get_board()
        for r in range(size):
            for c in range(size):
                if board[r][c] == 0:
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

        val = board[clicked_r][clicked_c]
        if val == 1:
            self.selected_pos = (clicked_r, clicked_c)
            self.draw_board()
        elif val == 2 and self.selected_pos is not None:
            start_pos = self.selected_pos
            if self.game.make_move(start_pos[0], start_pos[1], clicked_r, clicked_c):
                # [Sprint 4 Change] Record the move.
                self._record_event("MOVE", {"start": start_pos, "end": (clicked_r, clicked_c)})
                
                self.selected_pos = None
                self.draw_board()
                
                if self.game.has_won():
                    self._handle_game_over("Win")
                elif self.game.is_game_over():
                    self._handle_game_over("Loss")

    def _handle_game_over(self, result):
        """Unified game over handling for Manual, Auto, and Replay."""
        pegs = self.game.get_peg_count()
        self._record_event("GAME_OVER", {"result": result, "pegs": pegs})
        
        if result == "Win":
            msg = "You Win! (1 peg remaining)"
        else:
            msg = f"No more valid moves. You Lost! ({pegs} pegs remaining)"
        
        messagebox.showinfo("Game Over", msg)
        if self.recording_var.get():
            self.save_record()

    # [Sprint 3 Change] Added autoplay functionality to loop automated moves until the game ends.
    def autoplay(self):
        if not isinstance(self.game, AutomatedGame):
            messagebox.showerror("Error", "Switch to Automated mode first.")
            return

        def step():
            moves = self.game.get_all_valid_moves()
            if not moves:
                if self.game.has_won():
                    self._handle_game_over("Win")
                else:
                    self._handle_game_over("Loss")
                return

            # Note: make_auto_move internally picks a random move. 
            # We want to record WHICH move it picked.
            move = random.choice(moves)
            self.game.make_move(*move)
            self._record_event("MOVE", {"start": (move[0], move[1]), "end": (move[2], move[3])})
            
            self.draw_board()
            self.root.after(300, step)

        step()

    # [Sprint 3 Change] Added randomize functionality.
    def randomize(self):
        self.game.randomize_board()
        # [Sprint 4 Change] Record the board state after randomization.
        self._record_event("RANDOMIZE", {"board_state": self.game.get_board()})
        self.draw_board()

    # [Sprint 4 Change] Added Replay functionality.
    def replay_game(self):
        """Load a game record and replay it step by step."""
        file_path = filedialog.askopenfilename(
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")],
            title="Open Game Record"
        )
        if not file_path:
            return

        try:
            with open(file_path, 'r') as f:
                lines = f.readlines()
        except Exception as e:
            messagebox.showerror("Error", f"Could not read file: {e}")
            return

        self.is_replaying = True
        steps = []
        setup_data = {}

        for line in lines:
            line = line.strip()
            if not line: continue
            if line.startswith("BOARD_TYPE:"): setup_data["type"] = line.split(": ")[1]
            elif line.startswith("SIZE:"): setup_data["size"] = int(line.split(": ")[1])
            elif line.startswith("MODE:"): setup_data["mode"] = line.split(": ")[1]
            elif line.startswith("START_STATE:"): steps.append(("SET", json.loads(line.split(": ", 1)[1])))
            elif line.startswith("MOVE:"):
                # MOVE: (r1,c1) -> (r2,c2)
                parts = line.split(": ")[1].split(" -> ")
                start = eval(parts[0])
                end = eval(parts[1])
                steps.append(("MOVE", start, end))
            elif line.startswith("RANDOMIZE:"): steps.append(("SET", json.loads(line.split(": ", 1)[1])))
            elif line.startswith("RESULT:"):
                result_info = line.split(": ")[1]
                steps.append(("END", result_info))

        # Setup initial board for replay
        if "type" in setup_data and "size" in setup_data:
            self.size_var.set(str(setup_data["size"]))
            self.board_type_var.set(setup_data["type"])
            self.mode_var.set(setup_data.get("mode", "Manual"))
            self.new_game()
        
        def execute_step(index):
            if index >= len(steps):
                self.is_replaying = False
                return

            step = steps[index]
            if step[0] == "SET":
                self.game.set_board(step[1])
                self.draw_board()
            elif step[0] == "MOVE":
                self.game.make_move(step[1][0], step[1][1], step[2][0], step[2][1])
                self.draw_board()
            elif step[0] == "END":
                messagebox.showinfo("Replay Finished", f"Recorded Outcome: {step[1]}")
                self.is_replaying = False
                return

            self.root.after(500, lambda: execute_step(index + 1))

        execute_step(0)


def main():
    root = tk.Tk()
    app = PegSolitaireGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
