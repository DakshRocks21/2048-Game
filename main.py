import random

class Game2048:
    def __init__(self, size=4):
        self.size = size
        self.board = [[0] * size for _ in range(size)]
        self.add_new_tile()
        self.add_new_tile()
    
    def add_new_tile(self):
        empty_cells = [(i, j) for i in range(self.size) for j in range(self.size) if self.board[i][j] == 0]
        if not empty_cells:
            return False
        i, j = random.choice(empty_cells)
        self.board[i][j] = random.choice([2, 4])
        return True

    def compress(self, row):
        new_row = [i for i in row if i != 0]
        new_row += [0] * (self.size - len(new_row))
        return new_row

    def merge(self, row):
        for i in range(self.size - 1):
            if row[i] == row[i + 1] and row[i] != 0:
                row[i] *= 2
                row[i + 1] = 0
        return row

    def move_left(self):
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
        self.reverse()
        changed = self.move_left()
        self.reverse()
        return changed

    def move_up(self):
        self.transpose()
        changed = self.move_left()
        self.transpose()
        return changed

    def move_down(self):
        self.transpose()
        changed = self.move_right()
        self.transpose()
        return changed

    def reverse(self):
        for i in range(self.size):
            self.board[i] = self.board[i][::-1]

    def transpose(self):
        self.board = [list(row) for row in zip(*self.board)]

    def is_game_over(self):
        for i in range(self.size):
            for j in range(self.size):
                if self.board[i][j] == 0:
                    return False
                if i < self.size - 1 and self.board[i][j] == self.board[i + 1][j]:
                    return False
                if j < self.size - 1 and self.board[i][j] == self.board[i][j + 1]:
                    return False
        return True

    def print_board(self):
        for row in self.board:
            print("\t".join(map(str, row)))
        print()

    def play(self):
        while True:
            self.print_board()
            move = input("Enter move (w/a/s/d): ").strip().lower()
            if move in ['w', 'a', 's', 'd']:
                if move == 'w':
                    changed = self.move_up()
                elif move == 'a':
                    changed = self.move_left()
                elif move == 's':
                    changed = self.move_down()
                elif move == 'd':
                    changed = self.move_right()
                else:
                    continue

                if changed:
                    self.add_new_tile()
                    if self.is_game_over():
                        self.print_board()
                        print("Game Over!")
                        break
            else:
                print("Invalid move! Please enter w, a, s, or d.")

if __name__ == "__main__":
    game = Game2048()
    game.play()