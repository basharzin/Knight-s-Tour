import sys
import time

# Increase recursion limit for deep searches
sys.setrecursionlimit(20000)

class BacktrackingSolver:
    def __init__(self, n):
        self.n = n
        self.board = [[-1 for _ in range(n)] for _ in range(n)]
        self.moves = [(2,1), (1,2), (-1,2), (-2,1), (-2,-1), (-1,-2), (1,-2), (2,-1)]
        self.final_path = []

    def is_valid(self, x, y):
        return 0 <= x < self.n and 0 <= y < self.n and self.board[x][y] == -1

    def get_degree(self, x, y):
        # Warnsdorff's heuristic
        count = 0
        for dx, dy in self.moves:
            if self.is_valid(x + dx, y + dy):
                count += 1
        return count

    def solve_recursive(self, curr_x, curr_y, pos):
        self.board[curr_x][curr_y] = pos
        self.final_path.append((curr_x, curr_y))

        if pos == self.n * self.n - 1:
            return True

        possible_moves = []
        for dx, dy in self.moves:
            nx, ny = curr_x + dx, curr_y + dy
            if self.is_valid(nx, ny):
                possible_moves.append((nx, ny))

        # Optimization: Sort by degree (Warnsdorff's Rule)
        possible_moves.sort(key=lambda m: self.get_degree(m[0], m[1]))

        for nx, ny in possible_moves:
            if self.solve_recursive(nx, ny, pos + 1):
                return True

        # Backtrack
        self.board[curr_x][curr_y] = -1
        self.final_path.pop()
        return False

    def run(self, start_x, start_y):
        """
        Runs the algorithm and returns a dictionary with results.
        """
        start_time = time.time()
        success = self.solve_recursive(start_x, start_y, 0)
        end_time = time.time()
        
        return {
            "algorithm": "Backtracking",
            "success": success,
            "path": self.final_path,
            "time": end_time - start_time,
            "steps": len(self.final_path)
        }