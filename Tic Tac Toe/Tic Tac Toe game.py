import tkinter as tk
from tkinter import messagebox, ttk
from abc import ABC, abstractmethod
import math
import random
from datetime import datetime
import pygame
import json
import copy

# Initialize pygame mixer for sound
pygame.mixer.init()

class Board:
    """Represents the Tic Tac Toe board and game state"""
    def __init__(self):
        self.reset()
    
    def reset(self):
        self.grid = [[None for _ in range(3)] for _ in range(3)]
        self.winning_line = None
    
    def place_move(self, row: int, col: int, symbol: str) -> bool:
        if self.is_valid_move(row, col):
            self.grid[row][col] = symbol
            return True
        return False
    
    def is_valid_move(self, row: int, col: int) -> bool:
        return 0 <= row < 3 and 0 <= col < 3 and self.grid[row][col] is None
    
    def check_win(self) -> tuple:
        # Check rows and columns
        for i in range(3):
            if self.grid[i][0] == self.grid[i][1] == self.grid[i][2] and self.grid[i][0]:
                return (self.grid[i][0], [(i,0), (i,1), (i,2)])
            if self.grid[0][i] == self.grid[1][i] == self.grid[2][i] and self.grid[0][i]:
                return (self.grid[0][i], [(0,i), (1,i), (2,i)])
        
        # Check diagonals
        if self.grid[0][0] == self.grid[1][1] == self.grid[2][2] and self.grid[0][0]:
            return (self.grid[0][0], [(0,0), (1,1), (2,2)])
        if self.grid[0][2] == self.grid[1][1] == self.grid[2][0] and self.grid[0][2]:
            return (self.grid[0][2], [(0,2), (1,1), (2,0)])
        return (None, None)
    
    def is_full(self) -> bool:
        return all(cell is not None for row in self.grid for cell in row)
    
    def get_available_moves(self) -> list:
        return [(r, c) for r in range(3) for c in range(3) if self.grid[r][c] is None]

class Player(ABC):
    def __init__(self, symbol: str):
        self.symbol = symbol
    
    @abstractmethod
    def make_move(self, board: Board) -> tuple:
        pass

class HumanPlayer(Player):
    def __init__(self, symbol: str, gui):
        super().__init__(symbol)
        self.gui = gui
    
    def make_move(self, board: Board) -> tuple:
        self.gui.wait_for_human_move = True
        self.gui.status_label.config(text="Your turn! Click an empty cell")
        while self.gui.wait_for_human_move:
            self.gui.window.update()
        return self.gui.last_human_move

class AIPlayer(Player):
    def __init__(self, symbol: str, strategy: 'Strategy'):
        super().__init__(symbol)
        self.strategy = strategy
    
    def make_move(self, board: Board) -> tuple:
        return self.strategy.choose_move(board, self.symbol)

class Strategy(ABC):
    @abstractmethod
    def choose_move(self, board: Board, symbol: str) -> tuple:
        pass

class RandomStrategy(Strategy):
    def choose_move(self, board: Board, symbol: str) -> tuple:
        return random.choice(board.get_available_moves())

class IntermediateStrategy(Strategy):
    def choose_move(self, board: Board, symbol: str) -> tuple:
        # Try to win immediately
        for move in board.get_available_moves():
            temp_board = self.copy_board(board)
            temp_board.place_move(move[0], move[1], symbol)
            if self.check_win(temp_board, symbol):
                return move
        
        # Block opponent's win
        opponent = 'O' if symbol == 'X' else 'X'
        for move in board.get_available_moves():
            temp_board = self.copy_board(board)
            temp_board.place_move(move[0], move[1], opponent)
            if self.check_win(temp_board, opponent):
                return move
        
        # Choose center or random
        if (1,1) in board.get_available_moves():
            return (1,1)
        return random.choice(board.get_available_moves())
    
    def copy_board(self, board):
        new_board = Board()
        new_board.grid = [row[:] for row in board.grid]
        return new_board
    
    def check_win(self, board, symbol):
        winner, _ = board.check_win()
        return winner == symbol

class MinimaxStrategy(Strategy):
    def choose_move(self, board: Board, symbol: str) -> tuple:
        best_score = -math.inf
        best_move = None
        opponent = 'O' if symbol == 'X' else 'X'
        
        for move in board.get_available_moves():
            new_board = self.copy_board(board)
            new_board.place_move(move[0], move[1], symbol)
            score = self.minimax(new_board, False, symbol, opponent)
            if score > best_score:
                best_score = score
                best_move = move
                
        return best_move
    
    def minimax(self, board: Board, is_maximizing: bool, player: str, opponent: str) -> int:
        winner, _ = board.check_win()
        
        if winner == player:
            return 1
        elif winner == opponent:
            return -1
        if board.is_full():
            return 0
            
        if is_maximizing:
            best_score = -math.inf
            for move in board.get_available_moves():
                new_board = self.copy_board(board)
                new_board.place_move(move[0], move[1], player)
                score = self.minimax(new_board, False, player, opponent)
                best_score = max(score, best_score)
            return best_score
        else:
            best_score = math.inf
            for move in board.get_available_moves():
                new_board = self.copy_board(board)
                new_board.place_move(move[0], move[1], opponent)
                score = self.minimax(new_board, True, player, opponent)
                best_score = min(score, best_score)
            return best_score
    
    def copy_board(self, board):
        new_board = Board()
        new_board.grid = [row[:] for row in board.grid]
        return new_board

class TicTacToeGUI:
    def __init__(self):
        self.window = tk.Tk()
        self.window.title("Ultimate Tic Tac Toe")
        self.window.minsize(500, 550)
        self.style = {
            'bg': '#2C3E50',
            'x_color': '#3498DB',
            'o_color': '#E74C3C',
            'grid_color': '#34495E',
            'text_color': '#ECF0F1',
            'button_bg': '#2980B9',
            'font': ('Helvetica', 14, 'bold')
        }
        self.window.configure(bg=self.style['bg'])
        
        # Game state
        self.board = Board()
        self.current_player = None
        self.players = None
        self.human_turn = False
        self.wait_for_human_move = False
        self.last_human_move = None
        self.move_history = []
        self.score = {'X': 0, 'O': 0, 'Draws': 0}
        self.settings = {
            'difficulty': 'minimax',
            'sound': True,
            'first_player': 'human',
            'game_mode': 'human_vs_ai'
        }
        
        # Initialize components
        self.create_widgets()
        self.setup_menu()
        self.reset_game()
        self.window.mainloop()
    
    def create_widgets(self):
        # Main container
        self.main_frame = tk.Frame(self.window, bg=self.style['bg'])
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Scoreboard
        self.score_frame = tk.Frame(self.main_frame, bg=self.style['bg'])
        self.score_frame.pack(pady=10)
        
        self.score_labels = {
            'X': tk.Label(self.score_frame, text="X: 0", font=self.style['font'], 
                        bg=self.style['bg'], fg=self.style['x_color']),
            'O': tk.Label(self.score_frame, text="O: 0", font=self.style['font'], 
                        bg=self.style['bg'], fg=self.style['o_color']),
            'Draws': tk.Label(self.score_frame, text="Draws: 0", font=self.style['font'], 
                            bg=self.style['bg'], fg=self.style['text_color'])
        }
        for label in self.score_labels.values():
            label.pack(side=tk.LEFT, padx=10)
        
        # Game board
        self.canvas = tk.Canvas(self.main_frame, bg=self.style['bg'], highlightthickness=0)
        self.canvas.pack(fill=tk.BOTH, expand=True)
        
        # Status and controls
        self.status_label = tk.Label(self.main_frame, text="Game Started!", 
                                   font=self.style['font'], bg=self.style['bg'], 
                                   fg=self.style['text_color'])
        self.status_label.pack(pady=10)
        
        self.control_frame = tk.Frame(self.main_frame, bg=self.style['bg'])
        self.control_frame.pack(pady=10)
        
        self.restart_btn = tk.Button(self.control_frame, text="New Game", 
                                   command=self.reset_game, font=self.style['font'],
                                   bg=self.style['button_bg'], fg='white')
        self.restart_btn.pack(side=tk.LEFT, padx=5)
        
        self.settings_btn = tk.Button(self.control_frame, text="Settings", 
                                    command=self.show_settings, font=self.style['font'],
                                    bg=self.style['button_bg'], fg='white')
        self.settings_btn.pack(side=tk.LEFT, padx=5)
        
        # Event bindings
        self.canvas.bind("<Button-1>", self.on_click)
        self.canvas.bind("<Motion>", self.on_hover)
        self.window.bind("<Configure>", self.on_resize)
    
    def setup_menu(self):
        menu_bar = tk.Menu(self.window)
        
        # Game menu
        game_menu = tk.Menu(menu_bar, tearoff=0)
        game_menu.add_command(label="New Game", command=self.reset_game)
        game_menu.add_command(label="Statistics", command=self.show_stats)
        game_menu.add_separator()
        game_menu.add_command(label="Exit", command=self.window.quit)
        menu_bar.add_cascade(label="Game", menu=game_menu)
        
        # Mode menu
        mode_menu = tk.Menu(menu_bar, tearoff=0)
        self.mode_var = tk.StringVar()
        modes = [
            ("Human vs AI", "human_vs_ai"),
            ("AI vs Human", "ai_vs_human"),
            ("Human vs Human", "human_vs_human"),
            ("AI vs AI", "ai_vs_ai")
        ]
        for text, mode in modes:
            mode_menu.add_radiobutton(label=text, variable=self.mode_var,
                                    value=mode, command=self.change_mode)
        menu_bar.add_cascade(label="Mode", menu=mode_menu)
        self.mode_var.set("human_vs_ai")
        
        self.window.config(menu=menu_bar)
    
    def change_mode(self):
        self.reset_game()
    
    def create_players(self):
        mode = self.mode_var.get()
        difficulty = self.settings['difficulty']
        
        strategies = {
            'random': RandomStrategy(),
            'intermediate': IntermediateStrategy(),
            'minimax': MinimaxStrategy()
        }
        
        strategy = strategies.get(difficulty, MinimaxStrategy())
        
        if mode == 'human_vs_ai':
            return (HumanPlayer('X', self), AIPlayer('O', strategy))
        elif mode == 'ai_vs_human':
            return (AIPlayer('X', strategy), HumanPlayer('O', self))
        elif mode == 'human_vs_human':
            return (HumanPlayer('X', self), HumanPlayer('O', self))
        else:
            return (AIPlayer('X', strategy), AIPlayer('O', strategy))
    
    def reset_game(self):
        self.board.reset()
        self.move_history = []
        self.players = self.create_players()
        self.current_player = self.players[0]
        self.human_turn = isinstance(self.current_player, HumanPlayer)
        self.update_display()
        self.start_game()
    
    def start_game(self):
        if not self.human_turn:
            self.ai_move()
    
    def ai_move(self):
        if isinstance(self.current_player, AIPlayer):
            self.window.after(500, self.process_ai_move)
    
    def process_ai_move(self):
        row, col = self.current_player.make_move(self.board)
        self.process_move(row, col)
    
    def process_move(self, row, col):
        if self.board.place_move(row, col, self.current_player.symbol):
            self.move_history.append({
                'player': self.current_player.symbol,
                'position': (row, col),
                'time': datetime.now().isoformat()
            })
            self.update_display()
            self.check_game_state()
    
    def check_game_state(self):
        winner, win_line = self.board.check_win()
        
        if winner:
            self.handle_win(winner, win_line)
        elif self.board.is_full():
            self.handle_draw()
        else:
            self.switch_player()
            self.start_game()
    
    def handle_win(self, winner, win_line):
        self.board.winning_line = win_line
        self.score[winner] += 1
        self.play_sound('win')
        self.update_display()
        self.save_game_history(f"{winner} wins")
        messagebox.showinfo("Game Over", f"Player {winner} wins!")
        self.reset_game()
    
    def handle_draw(self):
        self.score['Draws'] += 1
        self.play_sound('draw')
        self.save_game_history("Draw")
        messagebox.showinfo("Game Over", "It's a draw!")
        self.reset_game()
    
    def switch_player(self):
        self.current_player = self.players[1] if self.current_player == self.players[0] else self.players[0]
        self.human_turn = isinstance(self.current_player, HumanPlayer)
    
    def update_display(self):
        self.draw_board()
        self.update_score_display()
    
    def draw_board(self):
        self.canvas.delete("all")
        w = self.canvas.winfo_width()
        h = self.canvas.winfo_height()
        cell_w = w // 3
        cell_h = h // 3
        
        # Draw grid
        for i in range(1, 3):
            self.canvas.create_line(i*cell_w, 0, i*cell_w, h, 
                                  fill=self.style['grid_color'], width=3)
            self.canvas.create_line(0, i*cell_h, w, i*cell_h, 
                                  fill=self.style['grid_color'], width=3)
        
        # Draw symbols
        for row in range(3):
            for col in range(3):
                symbol = self.board.grid[row][col]
                x = col * cell_w + cell_w//2
                y = row * cell_h + cell_h//2
                size = min(cell_w, cell_h) // 3
                
                if symbol == 'X':
                    self.draw_x(x, y, size)
                elif symbol == 'O':
                    self.draw_o(x, y, size)
        
        # Draw winning line
        if self.board.winning_line:
            self.draw_winning_line()
    
    def draw_x(self, x, y, size):
        self.canvas.create_line(x-size, y-size, x+size, y+size, 
                              width=3, fill=self.style['x_color'], tags="x")
        self.canvas.create_line(x+size, y-size, x-size, y+size, 
                              width=3, fill=self.style['x_color'], tags="x")
    
    def draw_o(self, x, y, size):
        self.canvas.create_oval(x-size, y-size, x+size, y+size,
                              width=3, outline=self.style['o_color'], tags="o")
    
    def draw_winning_line(self):
        line_coords = []
        for row, col in self.board.winning_line:
            w = self.canvas.winfo_width()
            h = self.canvas.winfo_height()
            line_coords.extend([
                col * w/3 + w/6,
                row * h/3 + h/6
            ])
        
        self.canvas.create_line(*line_coords, fill='#2ECC71', width=5, tags="winline")
    
    def on_resize(self, event):
        self.draw_board()
    
    def on_hover(self, event):
        if not self.human_turn:
            return
        
        w = self.canvas.winfo_width()
        h = self.canvas.winfo_height()
        col = event.x // (w // 3)
        row = event.y // (h // 3)
        
        self.canvas.delete("hover")
        if self.board.is_valid_move(row, col):
            cell_w = w // 3
            cell_h = h // 3
            x1 = col * cell_w + 5
            y1 = row * cell_h + 5
            x2 = (col+1) * cell_w - 5
            y2 = (row+1) * cell_h - 5
            
            self.canvas.create_rectangle(x1, y1, x2, y2, outline='#27AE60', 
                                       width=2, tags="hover")
    
    def on_click(self, event):
        if not self.human_turn:
            return
        
        w = self.canvas.winfo_width()
        h = self.canvas.winfo_height()
        col = event.x // (w // 3)
        row = event.y // (h // 3)
        
        if self.board.is_valid_move(row, col):
            self.play_sound('move')
            self.last_human_move = (row, col)
            self.wait_for_human_move = False
            self.process_move(row, col)
    
    def update_score_display(self):
        self.score_labels['X'].config(text=f"X: {self.score['X']}")
        self.score_labels['O'].config(text=f"O: {self.score['O']}")
        self.score_labels['Draws'].config(text=f"Draws: {self.score['Draws']}")
    
    def show_settings(self):
        settings_window = tk.Toplevel(self.window)
        settings_window.title("Game Settings")
        settings_window.configure(bg=self.style['bg'])
        
        ttk.Label(settings_window, text="Difficulty:", background=self.style['bg'],
                foreground=self.style['text_color']).grid(row=0, column=0, padx=10, pady=5)
        difficulty = ttk.Combobox(settings_window, values=["Random", "Intermediate", "Minimax"])
        difficulty.grid(row=0, column=1, padx=10, pady=5)
        difficulty.set(self.settings['difficulty'].capitalize())
        
        ttk.Label(settings_window, text="First Player:", background=self.style['bg'],
                foreground=self.style['text_color']).grid(row=1, column=0, padx=10, pady=5)
        first_player = ttk.Combobox(settings_window, values=["Human", "AI"])
        first_player.grid(row=1, column=1, padx=10, pady=5)
        first_player.set(self.settings['first_player'].capitalize())
        
        sound_var = tk.BooleanVar(value=self.settings['sound'])
        ttk.Checkbutton(settings_window, text="Enable Sounds", variable=sound_var).grid(row=2, columnspan=2, pady=5)
        
        ttk.Button(settings_window, text="Save", command=lambda: self.save_settings(
            difficulty.get().lower(),
            first_player.get().lower(),
            sound_var.get()
        )).grid(row=3, columnspan=2, pady=10)
    
    def save_settings(self, difficulty, first_player, sound):
        self.settings.update({
            'difficulty': difficulty,
            'first_player': first_player,
            'sound': sound
        })
        self.reset_game()
    
    def play_sound(self, sound_type):
        if self.settings['sound']:
            try:
                sounds = {
                    'move': 'move.wav',
                    'win': 'win.wav',
                    'draw': 'draw.wav'
                }
                pygame.mixer.Sound(sounds[sound_type]).play()
            except Exception as e:
                print(f"Error playing sound: {e}")
    
    def show_stats(self):
        stats_window = tk.Toplevel(self.window)
        stats_window.title("Game Statistics")
        
        tree = ttk.Treeview(stats_window, columns=("Date", "Result"), show="headings")
        tree.heading("Date", text="Date")
        tree.heading("Result", text="Result")
        tree.pack(padx=10, pady=10)
        
        try:
            with open('game_history.json') as f:
                for line in f:
                    game = json.loads(line)
                    tree.insert("", "end", values=(game['date'], game['result']))
        except FileNotFoundError:
            tk.Label(stats_window, text="No game history found").pack()
    
    def save_game_history(self, result):
        game_data = {
            'date': datetime.now().isoformat(),
            'result': result,
            'moves': self.move_history,
            'mode': self.mode_var.get()
        }
        
        try:
            with open('game_history.json', 'a') as f:
                f.write(json.dumps(game_data) + '\n')
        except Exception as e:
            print(f"Error saving game history: {e}")

if __name__ == "__main__":
    TicTacToeGUI()