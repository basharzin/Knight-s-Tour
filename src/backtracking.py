import sys
import time


sys.setrecursionlimit(50000)

class BacktrackingSolver:
    """
    Implements the Knight's Tour solution using a Backtracking algorithm.
    
    Optimization:
    This implementation utilizes 'Warnsdorff's Rule' heuristic. Instead of exploring 
    moves sequentially, it prioritizes moves that lead to squares with the fewest 
    onward moves. This drastically reduces the search space and backtracking steps.
    """

    def __init__(self, n):
        """
        Initialize the solver with board size N.
        
        Args:
            n (int): The dimension of the chessboard (NxN).
        """
        self.n = n
        
        self.board = [[-1 for _ in range(n)] for _ in range(n)]
        
        self.moves = [(2,1), (1,2), (-1,2), (-2,1), (-2,-1), (-1,-2), (1,-2), (2,-1)]
        self.final_path = []

    def is_valid(self, x, y):
        """
        Check if a move is within board boundaries and the square is unvisited.
        """
        return 0 <= x < self.n and 0 <= y < self.n and self.board[x][y] == -1

    def get_degree(self, x, y):
        """
        Calculates the number of valid onward moves from a given square (x, y).
        This is the core of Warnsdorff's heuristic.
        """
        count = 0
        for dx, dy in self.moves:
            if self.is_valid(x + dx, y + dy):
                count += 1
        return count

    def solve_recursive(self, curr_x, curr_y, pos):
        """
        The recursive function that attempts to build the path.
        
        Args:
            curr_x, curr_y: Current position of the knight.
            pos: The current step number (0 to N*N-1).
        
        Returns:
            bool: True if a solution is found, False otherwise.
        """
        self.board[curr_x][curr_y] = pos
        self.final_path.append((curr_x, curr_y))

        
        if pos == self.n * self.n - 1:
            return True

        
        possible_moves = []
        for dx, dy in self.moves:
            nx, ny = curr_x + dx, curr_y + dy
            if self.is_valid(nx, ny):
                possible_moves.append((nx, ny))

        
        possible_moves.sort(key=lambda m: self.get_degree(m[0], m[1]))

        
        for nx, ny in possible_moves:
            if self.solve_recursive(nx, ny, pos + 1):
                return True

        
        self.board[curr_x][curr_y] = -1
        self.final_path.pop()
        return False

    def run(self, start_x, start_y):
        """
        Executes the solver starting from a specific position.
        
        Returns:
            dict: Contains algorithm name, success status, execution time, steps, and path.
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