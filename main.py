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
        self.previous_board = None
        self.score = 0
        self.previous_score = 0
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

    def save_state(self):
        """
        Save the current state of the game for undo functionality
        """
        self.previous_board = copy.deepcopy(self.board)
        self.previous_score = self.score

    def undo(self):
        """
        Revert to the previous state of the game
        """
        if self.previous_board:
            self.board = self.previous_board
            self.score = self.previous_score

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
        while running:
            self.draw_board()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame.KEYDOWN:
                    self.save_state()
                    if event.key == pygame.K_UP:
                        changed = self.move_up()
                    elif event.key == pygame.K_LEFT:
                        changed = self.move_left()
                    elif event.key == pygame.K_DOWN:
                        changed = self.move_down()
                    elif event.key == pygame.K_RIGHT:
                        changed = self.move_right()
                    elif event.key == pygame.K_u:
                        self.undo()
                        changed = False
                    else:
                        continue

                    if changed:
                        self.add_new_tile()
                        if self.is_game_over():
                            self.handle_game_over()

if __name__ == "__main__":
    game = Game2048()
    game.play()
