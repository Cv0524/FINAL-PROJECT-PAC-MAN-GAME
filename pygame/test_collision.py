"""
Multi-Agent Pac-Men Challenge - Python Turtle
Single-file implementation (autonomous agents)

How to run: save as multi_agent_pacmen_turtle.py and run with Python 3:
    python multi_agent_pacmen_turtle.py

Controls: None (autonomous). Close window to stop. Metrics printed to console when simulation ends.

Features implemented:
- Grid-based maze with walls, pellets and shared-route corridors (marked as locks)
- Three autonomous Pac-Men agents that collect pellets and have energy/score
- When multiple agents attempt to enter the same shared corridor cell at the same time,
  they negotiate using a simple protocol (compare score, then lottery). If negotiation
  fails, fallback arbitration is random and loser waits (penalty).
- Token passing synchronization for multi-cell corridor traversal (simple lock)
- Metrics recorded: conflicts detected, successful negotiations, average wait times,
  fairness (simple access counts), total scores, and agents dropped out on low energy.
- Simulation uses turtle for visualization and a discrete tick loop.

Note: This is an educational, extensible prototype not an optimized game engine.
"""

import turtle
import random
from collections import deque, defaultdict

# === Configuration ===
CELL = 24  # pixels
ROWS, COLS = 21, 31  # typical Pac-Man-ish grid (odd numbers for corridors)
SCREEN_WIDTH = COLS * CELL
SCREEN_HEIGHT = ROWS * CELL
FPS = 8  # ticks per second
MAX_TICKS = 2000

# Colors
BACKGROUND = "black"
WALL_COLOR = "navy"
PELLET_COLOR = "white"
POWER_PELLET_COLOR = "gold"
AGENT_COLORS = ["red", "orange", "cyan"]
SHARED_ROUTE_COLOR = "darkgreen"

# Agent params
START_POS = [(1, 1), (ROWS-2, 1), (1, COLS-2)]
INITIAL_SCORE = 0
INITIAL_ENERGY = 100
PELLET_VALUE = 1
STALL_PENALTY = 2  # energy lost when forced to wait/fail negotiation
DROP_ENERGY_THRESHOLD = 5

# === Maze definition (0 empty/pellet, 1 wall, 2 shared-route) ===

def generate_maze(rows, cols):
    grid = [[0 for _ in range(cols)] for _ in range(rows)]
    for r in range(rows):
        grid[r][0] = 1
        grid[r][cols-1] = 1
    for c in range(cols):
        grid[0][c] = 1
        grid[rows-1][c] = 1

    for r in range(2, rows-2, 2):
        for c in range(2, cols-2, 4):
            grid[r][c] = 1
            if c+1 < cols-1:
                grid[r][c+1] = 1

    shared = set()
    for r in range(3, rows-3, 6):
        for c in range(3, cols-3):
            if grid[r][c] == 0 and c % 6 in (0, 1):
                shared.add((r, c))
    for c in range(3, cols-3, 6):
        for r in range(3, rows-3):
            if grid[r][c] == 0 and r % 6 in (0, 1):
                shared.add((r, c))

    for (r, c) in shared:
        grid[r][c] = 2

    return grid

def neighbors(pos):
    r, c = pos
    return [(r-1, c), (r+1, c), (r, c-1), (r, c+1)]

# === Visualization ===

screen = turtle.Screen()
screen.setup(width=SCREEN_WIDTH+50, height=SCREEN_HEIGHT+50)
screen.title("Multi-Agent Pac-Men - Turtle")
screen.bgcolor(BACKGROUND)
screen.tracer(0, 0)

pen = turtle.Turtle()
pen.hideturtle()
pen.penup()

def to_pixel(pos):
    r, c = pos
    x = -SCREEN_WIDTH/2 + c*CELL + CELL/2
    y = SCREEN_HEIGHT/2 - r*CELL - CELL/2
    return x, y

# === Maze class ===
class Maze:
    def __init__(self, rows, cols):
        self.rows = rows
        self.cols = cols
        self.grid = generate_maze(rows, cols)
        self.pellets = set()
        for r in range(rows):
            for c in range(cols):
                if self.grid[r][c] == 0:
                    self.pellets.add((r, c))
        self.power_pellets = {(1,1), (1,cols-2), (rows-2,1), (rows-2,cols-2)}

    def is_wall(self, pos):
        r, c = pos
        if not (0 <= r < self.rows and 0 <= c < self.cols):
            return True
        return self.grid[r][c] == 1

    def is_shared(self, pos):
        r, c = pos
        if not (0 <= r < self.rows and 0 <= c < self.cols):
            return False
        return self.grid[r][c] == 2

    def draw(self):
        pen.clear()
        for r in range(self.rows):
            for c in range(self.cols):
                x, y = to_pixel((r, c))
                cell_type = self.grid[r][c]
                pen.goto(x - CELL/2, y - CELL/2)
                if cell_type == 1:
                    pen.fillcolor(WALL_COLOR)
                    pen.begin_fill()
                    for _ in range(4):
                        pen.forward(CELL)
                        pen.left(90)
                    pen.end_fill()
                elif cell_type == 2:
                    pen.fillcolor(SHARED_ROUTE_COLOR)
                    pen.begin_fill()
                    for _ in range(4):
                        pen.forward(CELL)
                        pen.left(90)
                    pen.end_fill()
                if (r, c) in self.pellets:
                    pen.goto(x, y-4)
                    pen.dot(4, PELLET_COLOR)
                if (r, c) in self.power_pellets:
                    pen.goto(x, y)
                    pen.dot(8, POWER_PELLET_COLOR)

# === Corridor Lock Manager ===
class CorridorLockManager:
    def __init__(self):
        self.owner = {}
        self.queue = defaultdict(deque)
        self.conflicts = 0
        self.successful_negotiations = 0

    def request(self, cell, agent_id, agent_score):
        if cell not in self.owner:
            self.owner[cell] = agent_id
            self.successful_negotiations += 1
            return True
        else:
            self.queue[cell].append((agent_id, agent_score))
            self.conflicts += 1
            return False

    def release(self, cell, agent_id):
        if self.owner.get(cell) == agent_id:
            del self.owner[cell]
            if self.queue[cell]:
                contenders = list(self.queue[cell])
                self.queue[cell].clear()
                contenders.sort(key=lambda x: x[1], reverse=True)
                best_score = contenders[0][1]
                top = [a for a, s in contenders if s == best_score]
                winner = random.choice(top)
                self.owner[cell] = winner
                self.successful_negotiations += 1
            return True
        return False

    def force_arbitrate(self, cell):
        if cell not in self.owner and self.queue[cell]:
            agent, _ = self.queue[cell].popleft()
            self.owner[cell] = agent
            return agent
        return None

# === Agent class ===
class Agent:
    def __init__(self, aid, start_pos, color, maze, lock_mgr):
        self.id = aid
        self.pos = start_pos
        self.color = color
        self.maze = maze
        self.lock_mgr = lock_mgr
        self.turtle = turtle.Turtle()
        self.turtle.shape('circle')
        self.turtle.shapesize(0.9)
        self.turtle.penup()
        self.turtle.color('black', color)
        self.update_turtle()

        self.score = INITIAL_SCORE
        self.energy = INITIAL_ENERGY
        self.wait_time = 0
        self.access_count = 0
        self.alive = True
        self.path = []

    def update_turtle(self):
        x, y = to_pixel(self.pos)
        self.turtle.goto(x, y)

    def sense(self):
        cand = []
        for n in neighbors(self.pos):
            if not self.maze.is_wall(n):
                cand.append(n)
        return cand

    def plan_move(self):
        if not self.maze.pellets:
            return self.pos
        if self.path:
            nxt = self.path.pop(0)
            return nxt
        best = None
        bestd = 1e9
        for p in self.maze.pellets:
            d = abs(p[0]-self.pos[0]) + abs(p[1]-self.pos[1])
            if d < bestd:
                bestd = d
                best = p
        from collections import deque
        q = deque()
        q.append((self.pos, []))
        seen = {self.pos}
        while q:
            cur, path = q.popleft()
            if cur == best:
                self.path = path[1:] if len(path) > 0 else []
                if self.path:
                    return self.path.pop(0)
                else:
                    return self.pos
            for nb in neighbors(cur):
                if nb in seen: continue
                if self.maze.is_wall(nb): continue
                seen.add(nb)
                q.append((nb, path + [nb]))
        cands = self.sense()
        if cands:
            return random.choice(cands)
        return self.pos

    def step(self):
        if not self.alive:
            return
        nxt = self.plan_move()
        if nxt == self.pos:
            self.energy -= 0.1
            return
        if self.maze.is_shared(nxt):
            got = self.lock_mgr.request(nxt, self.id, self.score)
            if got:
                self.access_count += 1
                self.move_to(nxt)
            else:
                self.wait_time += 1
                self.energy -= STALL_PENALTY
        else:
            self.move_to(nxt)
        if self.energy <= DROP_ENERGY_THRESHOLD:
            self.alive = False

    def move_to(self, nxt):
        if self.maze.is_shared(self.pos):
            self.lock_mgr.release(self.pos, self.id)
        self.pos = nxt
        self.update_turtle()
        if self.pos in self.maze.pellets:
            self.maze.pellets.remove(self.pos)
            self.score += PELLET_VALUE
            self.energy += 1
        if self.pos in self.maze.power_pellets:
            self.score += 5
            self.energy += 5

    def force_wait(self):
        self.wait_time += 1
        self.energy -= STALL_PENALTY

# === Simulation controller ===
class Simulation:
    def __init__(self):
        self.maze = Maze(ROWS, COLS)
        self.lock_mgr = CorridorLockManager()
        self.agents = []
        for i, start in enumerate(START_POS):
            a = Agent(i, start, AGENT_COLORS[i % len(AGENT_COLORS)], self.maze, self.lock_mgr)
            self.agents.append(a)
        self.ticks = 0
        self.metrics = {
            'conflicts': 0,
            'successful_negotiations': 0,
            'wait_times': defaultdict(int),
            'access_counts': defaultdict(int),
        }
        self.running = True

    def draw(self):
        self.maze.draw()
        pen.goto(-SCREEN_WIDTH/2 + 10, SCREEN_HEIGHT/2 - 12)
        pen.color('white')
        info = ' | '.join([f'A{a.id}: S{a.score} E{int(a.energy)} W{a.wait_time}' for a in self.agents])
        pen.write(info, font=(None, 10, 'normal'))

    def step(self):
        if not self.running:
            return
        for a in self.agents:
            if a.alive:
                a.step()

        if self.ticks % 30 == 0:
            for cell, q in list(self.lock_mgr.queue.items()):
                if cell not in self.lock_mgr.owner and q:
                    self.lock_mgr.force_arbitrate(cell)

        self.ticks += 1
        self.metrics['conflicts'] = self.lock_mgr.conflicts
        self.metrics['successful_negotiations'] = self.lock_mgr.successful_negotiations

        pellets_left = len(self.maze.pellets)
        alive_agents = [a for a in self.agents if a.alive]
        if pellets_left == 0 or not alive_agents or self.ticks >= MAX_TICKS:
            self.running = False
            self.finish()

    def finish(self):
        screen.update()
        print("--- Simulation finished ---")
        print(f"Ticks: {self.ticks}")
        print(f"Pellets left: {len(self.maze.pellets)}")
        print(f"Conflicts detected: {self.metrics['conflicts']}")
        print(f"Successful negotiations (lock grants): {self.metrics['successful_negotiations']}")
        for a in self.agents:
            print(f"Agent {a.id}: Score={a.score} Energy={a.energy} Wait={a.wait_time} Accesses={a.access_count} Alive={a.alive}")
        counts = [self.metrics['access_counts'].get(a.id, 0) for a in self.agents]
        avg = sum(counts)/len(counts) if counts else 0
        var = sum((x-avg)**2 for x in counts)/len(counts) if counts else 0
        print(f"Fairness (access variance): {var:.2f}")
        turtle.bye()

    def run_tick(self):
        if not self.running:
            return
        self.draw()
        self.step()
        screen.update()
        screen.ontimer(self.run_tick, int(1000/FPS))

# === Main ===

def main():
    sim = Simulation()
    sim.draw()
    screen.update()
    screen.ontimer(sim.run_tick, int(1000/FPS))
    screen.mainloop()

if __name__ == '__main__':
    main()