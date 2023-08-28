import tkinter as tk
from itertools import cycle
from tkinter import font
from typing import NamedTuple


class Player(NamedTuple):
    label: str
    color: str


class Move(NamedTuple):
    row: int
    col: int
    label: str = ""


BOARD_SIZE = 3
DEFAULT_PLAYERS = (
    Player(label="X", color="red"),
    Player(label="O", color="green"),
)


class Scoreboard:
    def __init__(self, players):
        self.players = players
        self.scores = {player.label: 0 for player in players}

    def increase_score(self, player_label):
        self.scores[player_label] += 1

    def get_score(self, player_label):
        return self.scores[player_label]


class CustomTicTacToeGame:
    def __init__(self, players=DEFAULT_PLAYERS, board_size=BOARD_SIZE):
        self._players = cycle(players)
        self.board_size = board_size
        self.current_player = next(self._players)
        self.winner_combo = []
        self._current_moves = []
        self._has_winner = False
        self._winning_combos = []
        self.scoreboard = Scoreboard(players)
        self._setup_board()

    def _setup_board(self):
        self._current_moves = [
            [Move(row, col) for col in range(self.board_size)]
            for row in range(self.board_size)
        ]
        self._winning_combos = self._get_winning_combos()

    def _get_winning_combos(self):
        rows = [
            [(move.row, move.col) for move in row]
            for row in self._current_moves
        ]
        columns = [list(col) for col in zip(*rows)]
        first_diagonal = [row[i] for i, row in enumerate(rows)]
        second_diagonal = [col[j] for j, col in enumerate(reversed(columns))]
        return rows + columns + [first_diagonal, second_diagonal]

    def toggle_player(self):
        self.current_player = next(self._players)

    def is_valid_move(self, move):
        row, col = move.row, move.col
        move_was_not_played = self._current_moves[row][col].label == ""
        no_winner = not self._has_winner
        return no_winner and move_was_not_played

    def process_move(self, move):
        row, col = move.row, move.col
        self._current_moves[row][col] = move
        for combo in self._winning_combos:
            results = set(self._current_moves[n][m].label for n, m in combo)
            is_win = (len(results) == 1) and ("" not in results)
            if is_win:
                self._has_winner = True
                self.scoreboard.increase_score(self.current_player.label)
                self.winner_combo = combo
                break

    def has_winner(self):
        return self._has_winner

    def is_tied(self):
        no_winner = not self._has_winner
        played_moves = (
            move.label for row in self._current_moves for move in row
        )
        return no_winner and all(played_moves)

    def reset_game(self):
        for row, row_content in enumerate(self._current_moves):
            for col, _ in enumerate(row_content):
                row_content[col] = Move(row, col)
        self._has_winner = False
        self.winner_combo = []


class CustomTicTacToeBoard(tk.Tk):
    def __init__(self, game):
        super().__init__()
        self.title("Tic-Tac-Toe Game PRO")
        self._cells = {}
        self._game = game
        self._configure_styles()
        self._create_menu()
        self._create_board_display()
        self._create_scoreboard_display()
        self._create_board_grid()
        self._create_button_frame()

    def _configure_styles(self):
        self.board_style = {
            "font": font.Font(family="Helvetica", size=24, weight="bold"),
            "bg": "white",
            "fg": "black"
        }
        self.button_style = {
            "font": font.Font(family="Helvetica", size=18, weight="bold"),
            "bg": "lightgreen",
            "fg": "black"
        }

    def _create_menu(self):
        menu_bar = tk.Menu(master=self)
        self.config(menu=menu_bar)
        file_menu = tk.Menu(master=menu_bar)
        file_menu.add_command(label="Play Again", command=self.reset_board)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=quit)
        menu_bar.add_cascade(label="Pin Option", menu=file_menu)

    def _create_board_display(self):
        display_frame = tk.Frame(master=self)
        display_frame.pack(fill=tk.X)
        self.display = tk.Label(
            master=display_frame,
            text="Let's Play!",
            font=font.Font(size=28, weight="bold"),
        )
        self.display.pack()

    def _create_scoreboard_display(self):
        scoreboard_frame = tk.Frame(master=self)
        scoreboard_frame.pack(fill=tk.X)
        self.scoreboard_labels = []
        for player in self._game.scoreboard.players:
            label = tk.Label(
                master=scoreboard_frame,
                text=f"{player.label}: {self._game.scoreboard.get_score(player.label)}",
                font=font.Font(size=18),
                fg=player.color
            )
            label.pack(side=tk.LEFT, padx=10)
            self.scoreboard_labels.append(label)

    def _create_board_grid(self):
        grid_frame = tk.Frame(master=self, bg="black")
        grid_frame.pack()
        for row in range(self._game.board_size):
            self.rowconfigure(row, weight=1, minsize=100)
            self.columnconfigure(row, weight=1, minsize=100)
            for col in range(self._game.board_size):
                button = tk.Button(
                    master=grid_frame,
                    text="",
                    **self.board_style,
                    width=6,
                    height=3,
                    relief=tk.GROOVE,
                )
                self._cells[button] = (row, col)
                button.bind("<ButtonPress-1>", self.play)
                button.grid(row=row, column=col, padx=1, pady=1, sticky="nsew")

    def _create_button_frame(self):
        button_frame = tk.Frame(master=self, bg="Gray")
        button_frame.pack(pady=10)

        play_again_button = tk.Button(
            master=button_frame,
            text="Play Again",
            **self.button_style,
            command=self.reset_board
        )
        play_again_button.pack(side=tk.LEFT, padx=(70, 10))

        exit_button = tk.Button(
            master=button_frame,
            text="Exit",
            **self.button_style,
            command=self.quit
        )
        exit_button.pack(side=tk.LEFT, padx=(20, 50))

    def play(self, event):
        clicked_btn = event.widget
        row, col = self._cells[clicked_btn]
        move = Move(row, col, self._game.current_player.label)
        if self._game.is_valid_move(move):
            self._update_button(clicked_btn)
            self._game.process_move(move)
            if self._game.is_tied():
                self._update_display(msg="It's a Tie!", color="blue")
            elif self._game.has_winner():
                self._highlight_cells()
                msg = f'Player "{self._game.current_player.label}" Wins!'
                color = self._game.current_player.color
                self._update_display(msg, color)
            else:
                self._game.toggle_player()
                msg = f"{self._game.current_player.label}'s Turn"
                self._update_display(msg)

    def _update_button(self, clicked_btn):
        clicked_btn.config(text=self._game.current_player.label)
        clicked_btn.config(fg=self._game.current_player.color)

    def _update_display(self, msg, color="black"):
        self.display["text"] = msg
        self.display["fg"] = color

    def _highlight_cells(self):
        for button, coordinates in self._cells.items():
            if coordinates in self._game.winner_combo:
                button.config(highlightbackground="red")

    def reset_board(self):
        self._game.reset_game()
        self._update_display(msg="Get Ready!")
        for button in self._cells.keys():
            button.config(highlightbackground="lightgreen")
            button.config(text="")
            button.config(fg="black")
        for label in self.scoreboard_labels:
            player_label = label["text"].split(":")[0]
            new_score = self._game.scoreboard.get_score(player_label)
            label["text"] = f"{player_label}: {new_score}"


def main():
    custom_game = CustomTicTacToeGame()
    custom_board = CustomTicTacToeBoard(custom_game)
    custom_board.mainloop()


if __name__ == "__main__":
    main()
