import pygame
import sys
import random
import copy

# Constants for the game
SIZE = 4
TILE_SIZE = 100
MARGIN = 10
WIDTH = SIZE * TILE_SIZE + (SIZE + 1) * MARGIN
HEIGHT = WIDTH
FONT_SIZE = 36
BACKGROUND_COLOR = (187, 173, 160)
TILE_COLORS = {
    0: (205, 193, 180),
    2: (238, 228, 218),
    4: (237, 224, 200),
    8: (242, 177, 121),
    16: (245, 149, 99),
    32: (246, 124, 95),
    64: (246, 94, 59),
    128: (237, 207, 114),
    256: (237, 204, 97),
    512: (237, 200, 80),
    1024: (237, 197, 63),
    2048: (237, 194, 46),
    4096: (60, 58, 50),
    8192: (28, 25, 20),
}
TEXT_COLOR = (119, 110, 101)
SCORE_COLOR = (255, 255, 255)

# Game Class
class Game2048:
    def __init__(self, size=4):
        self.size = size
        self.board = [[0] * size for _ in range(size)]
        self.score = 0
        self.add_new_tile()
        self.add_new_tile()
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT + 100))  # Extra space for score
        pygame.display.set_caption('2048')
        self.font = pygame.font.SysFont('arial', FONT_SIZE)
        self.score_font = pygame.font.SysFont('arial', 24)

    def add_new_tile(self):
        """
        Adds a new tile (2 or 4) to a random empty cell on the board
        """
        empty_cells = [(i, j) for i in range(self.size) for j in range(self.size) if self.board[i][j] == 0]
        if not empty_cells:
            return False
        i, j = random.choice(empty_cells)
        self.board[i][j] = random.choice([2, 4])
        return True

    def compress(self, row):
        """
        Compress the row by moving all non-zero elements to the left side
        """
        new_row = [i for i in row if i != 0]
        new_row += [0] * (self.size - len(new_row))
        return new_row

    def merge(self, row):
        """
        Merge the row by adding the same adjacent elements
        """
        for i in range(self.size - 1):
            if row[i] == row[i + 1] and row[i] != 0:
                row[i] *= 2
                self.score += row[i]
                row[i + 1] = 0
        return row

    def move_left(self):
        """
        Move all tiles to the left and merge
        """
        changed = False
        new_board = []
        for row in self.board:
            compressed_row = self.compress(row)
            merged_row = self.merge(compressed_row)
            final_row = self.compress(merged_row)
            if final_row != row:
                changed = True
            new_board.append(final_row)
        self.board = new_board
        return changed

    def move_right(self):
        """
        Flips the board and moves left and then flips it back
        """
        self.reverse()
        changed = self.move_left()
        self.reverse()
        return changed

    def move_up(self):
        """
        Turns the board, moves left and then turns it back
        """
        self.transpose()
        changed = self.move_left()
        self.transpose()
        return changed

    def move_down(self):
        """
        Turns the board, moves right (which flips it, compresses it, and flips it back) and then turns it back
        """
        self.transpose()
        changed = self.move_right()
        self.transpose()
        return changed

    def reverse(self):
        """
        Reverses all the rows of the board
        """
        for i in range(self.size):
            self.board[i] = self.board[i][::-1]

    def transpose(self):
        """
        Turns the columns of the board into rows
        """
        self.board = [list(row) for row in zip(*self.board)]

    def is_game_over(self):
        """
        Check if the game is over by checking if there are any empty cells or if there are any adjacent cells with the same value
        """
        for i in range(self.size):
            for j in range(self.size):
                if self.board[i][j] == 0:
                    return False
                if i < self.size - 1 and self.board[i][j] == self.board[i + 1][j]:
                    return False
                if j < self.size - 1 and self.board[i][j] == self.board[i][j + 1]:
                    return False
        return True

    def draw_board(self):
        """
        Draw the board on the screen
        """
        self.screen.fill(BACKGROUND_COLOR)
        for row in range(self.size):
            for col in range(self.size):
                value = self.board[row][col]
                color = TILE_COLORS.get(value, TILE_COLORS[8192])
                rect = pygame.Rect(
                    MARGIN + col * (TILE_SIZE + MARGIN),
                    MARGIN + row * (TILE_SIZE + MARGIN),
                    TILE_SIZE, TILE_SIZE
                )
                pygame.draw.rect(self.screen, color, rect)
                if value != 0:
                    text_surface = self.font.render(str(value), True, TEXT_COLOR)
                    text_rect = text_surface.get_rect(center=rect.center)
                    self.screen.blit(text_surface, text_rect)

        # Draw the score
        score_surface = self.score_font.render(f"Score: {self.score}", True, SCORE_COLOR)
        self.screen.blit(score_surface, (MARGIN, HEIGHT + MARGIN))

        pygame.display.update()

    def handle_game_over(self):
        """
        Handles the game over screen and allows the player to restart or quit
        """
        self.draw_board()
        font = pygame.font.SysFont('arial', 72)
        text_surface = font.render("Game Over!", True, TEXT_COLOR)
        text_rect = text_surface.get_rect(center=(WIDTH // 2, HEIGHT // 2))
        self.screen.blit(text_surface, text_rect)

        pygame.display.update()
        pygame.time.wait(2000)

        # Restart the game
        self.__init__(self.size)

    def play(self):
        """
        Main game loop that handles drawing and user input
        """
        running = True
        ai = WordleAI(self)
        while running:
            self.draw_board()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_UP:
                        changed = self.move_up()
                    elif event.key == pygame.K_LEFT:
                        changed = self.move_left()
                    elif event.key == pygame.K_DOWN:
                        changed = self.move_down()
                    elif event.key == pygame.K_RIGHT:
                        changed = self.move_right()
                    elif event.key == pygame.K_a:  # AI Move
                        ai_move = ai.get_next_move()
                        print(f"AI suggests moving {ai_move}")
                        """
                        if ai_move == "UP":
                            changed = self.move_up()
                        elif ai_move == "DOWN":
                            changed = self.move_down()
                        elif ai_move == "LEFT":
                            changed = self.move_left()
                        elif ai_move == "RIGHT":
                            changed = self.move_right()
                        """
                        changed = False
                    else:
                        continue

                    if changed:
                        self.add_new_tile()
                        if self.is_game_over():
                            self.handle_game_over()


import math

class WordleAI:
    def __init__(self, game):
        self.game = game

    def simulate_move(self, board, score, move):
        """
        Simulates a move and returns the resulting board, score, and whether the move was effective.
        """
        temp_game = Game2048(self.game.size)
        temp_game.board = copy.deepcopy(board)
        temp_game.score = score
        
        if move == "UP":
            changed = temp_game.move_up()
        elif move == "DOWN":
            changed = temp_game.move_down()
        elif move == "LEFT":
            changed = temp_game.move_left()
        elif move == "RIGHT":
            changed = temp_game.move_right()

        return temp_game.board, temp_game.score, changed

    def get_all_possible_boards(self, board, score):
        """
        Generates all possible board states after a move, considering where the new tile might appear.
        """
        possible_boards = []
        empty_cells = [(i, j) for i in range(self.game.size) for j in range(self.game.size) if board[i][j] == 0]
        for cell in empty_cells:
            for value in [2, 4]:  # The new tile can be 2 or 4
                new_board = copy.deepcopy(board)
                new_board[cell[0]][cell[1]] = value
                possible_boards.append((new_board, score))
        return possible_boards

    def monotonicity_score(self, board):
        """
        Calculates how "monotonic" the board is, rewarding boards where values consistently increase or decrease along rows or columns.
        """
        score = 0
        for i in range(self.game.size):
            for j in range(self.game.size - 1):
                if board[i][j] != 0:
                    if board[i][j] >= board[i][j + 1]:
                        score += board[i][j]
                    if board[j][i] >= board[j + 1][i]:
                        score += board[j][i]
        return score

    def clustering_score(self, board):
        """
        Rewards board configurations where similar tiles are close together, which can facilitate future merges.
        """
        score = 0
        for i in range(self.game.size):
            for j in range(self.game.size):
                if board[i][j] == 0:
                    continue
                for ni, nj in [(i - 1, j), (i + 1, j), (i, j - 1), (i, j + 1)]:
                    if 0 <= ni < self.game.size and 0 <= nj < self.game.size and board[ni][nj] != 0:
                        score -= abs(board[i][j] - board[ni][nj])
        return score

    def corner_preference_score(self, board):
        """
        Encourages higher tiles to be placed in the corners of the board, which is a common strategy for 2048.
        """
        max_tile = max([board[i][j] for i in range(self.game.size) for j in range(self.game.size)])
        if board[0][0] == max_tile or board[0][self.game.size - 1] == max_tile or \
           board[self.game.size - 1][0] == max_tile or board[self.game.size - 1][self.game.size - 1] == max_tile:
            return max_tile * 2  # Strong preference for corners
        return 0

    def calculate_board_score(self, board, score):
        """
        Evaluates the board by combining different heuristics to produce a single score.
        """
        monotonicity = self.monotonicity_score(board)
        clustering = self.clustering_score(board)
        corner_preference = self.corner_preference_score(board)
        empty_cells = sum([1 for i in range(self.game.size) for j in range(self.game.size) if board[i][j] == 0])

        # Combine scores, giving weight to each heuristic
        total_score = score + monotonicity + clustering + corner_preference + math.log2(empty_cells + 1) * 10
        return total_score

    def get_best_move(self):
        """
        Determines the best move by looking ahead up to 3 moves, considering board heuristics and probabilities.
        """
        moves = ["UP", "DOWN", "LEFT", "RIGHT"]
        best_score = -1
        best_move = None
        best_sequence = []

        for move in moves:
            # Simulate first move
            board_after_first_move, score_after_first_move, changed = self.simulate_move(self.game.board, self.game.score, move)
            
            # Skip move if it doesn't change the board
            if not changed:
                continue

            first_move_score = 0
            possible_boards_after_first = self.get_all_possible_boards(board_after_first_move, score_after_first_move)

            for (board_after_first, _) in possible_boards_after_first:
                for move2 in moves:
                    board_after_second_move, score_after_second_move, changed2 = self.simulate_move(board_after_first, score_after_first_move, move2)

                    if not changed2:
                        continue

                    second_move_score = 0
                    possible_boards_after_second = self.get_all_possible_boards(board_after_second_move, score_after_second_move)

                    for (board_after_second, _) in possible_boards_after_second:
                        for move3 in moves:
                            board_after_third_move, score_after_third_move, changed3 = self.simulate_move(board_after_second, score_after_second_move, move3)

                            if not changed3:
                                continue

                            third_move_score = self.calculate_board_score(board_after_third_move, score_after_third_move)
                            second_move_score += third_move_score

                    first_move_score += second_move_score / len(possible_boards_after_second)

            first_move_score /= len(possible_boards_after_first)
            print(f"Move {move}: Average Score {first_move_score}")

            if first_move_score > best_score:
                best_score = first_move_score
                best_move = move
                best_sequence = [move]

        print(f"Best score: {best_score}, Best sequence: {best_sequence}")
        return best_move, best_sequence

    def get_next_move(self):
        """
        Returns the best move by analyzing the next three possible moves.
        """
        best_move, best_sequence = self.get_best_move()

        if best_move is None:
            # If no valid move found (which is unlikely), default to random valid move
            valid_moves = ["UP", "DOWN", "LEFT", "RIGHT"]
            random.shuffle(valid_moves)
            for move in valid_moves:
                board_after_move, score_after_move, changed = self.simulate_move(self.game.board, self.game.score, move)
                if changed:
                    best_move = move
                    break

            best_sequence = [best_move]
        
        print(f"Best move is {best_move}")
        print(f"Sequence of moves: {best_sequence}")
        return best_move

if __name__ == "__main__":
    game = Game2048()
    game.play()