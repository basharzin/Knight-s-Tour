import random
import time

class CulturalSolver:
    def __init__(self, n, pop_size=150, max_gens=2000):
        self.n = n
        self.pop_size = pop_size
        self.max_gens = max_gens
        self.moves = [(2,1), (1,2), (-1,2), (-2,1), (-2,-1), (-1,-2), (1,-2), (2,-1)]
        
        # Belief Space
        self.belief_best_genome = [] 
        self.belief_best_score = 0
        self.belief_best_path = []

    def genome_to_path(self, genome, start_x, start_y):
        path = [(start_x, start_y)]
        visited = {(start_x, start_y)}
        curr_x, curr_y = start_x, start_y
        
        for move_idx in genome:
            dx, dy = self.moves[move_idx]
            nx, ny = curr_x + dx, curr_y + dy
            
            if 0 <= nx < self.n and 0 <= ny < self.n and (nx, ny) not in visited:
                curr_x, curr_y = nx, ny
                path.append((nx, ny))
                visited.add((nx, ny))
            else:
                break 
        return path

    def run(self, start_x, start_y):
        start_time = time.time()
        
        # Initialize Population
        genome_len = self.n * self.n
        population = [[random.randint(0, 7) for _ in range(genome_len)] for _ in range(self.pop_size)]

        for gen in range(1, self.max_gens + 1):
            scored_population = []
            
            # Evaluate & Update Belief Space
            for genome in population:
                path = self.genome_to_path(genome, start_x, start_y)
                score = len(path)
                scored_population.append((score, genome))
                
                if score > self.belief_best_score:
                    self.belief_best_score = score
                    self.belief_best_path = path
                    self.belief_best_genome = genome[:]
            
            if self.belief_best_score == self.n * self.n:
                break # Found solution
            
            # Reproduction (Elitism + Guided Mutation)
            scored_population.sort(key=lambda x: x[0], reverse=True)
            top_performers = [x[1] for x in scored_population[:int(self.pop_size * 0.3)]]
            
            new_pop = [self.belief_best_genome[:]] # Elitism
            
            while len(new_pop) < self.pop_size:
                parent = random.choice(top_performers)
                child = parent[:]
                
                # Knowledge-based Mutation
                fail_idx = self.belief_best_score - 1
                if fail_idx < len(child):
                    mutation_start = max(0, fail_idx - random.randint(0, 5))
                    for k in range(mutation_start, len(child)):
                        if random.random() < 0.2:
                            child[k] = random.randint(0, 7)     
                new_pop.append(child)
            
            population = new_pop
            
        end_time = time.time()
        
        success = (self.belief_best_score == self.n * self.n)
        
        return {
            "algorithm": "Cultural Algorithm",
            "success": success,
            "path": self.belief_best_path,
            "time": end_time - start_time,
            "steps": len(self.belief_best_path)
        }