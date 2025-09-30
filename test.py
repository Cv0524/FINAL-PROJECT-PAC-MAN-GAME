import pygame
import random
from collections import deque, defaultdict

# --------------------
# Config
# --------------------
TILE = 22
COLS, ROWS = 31, 21
WIDTH, HEIGHT = COLS * TILE, ROWS * TILE + 100  # HUD space
FPS = 8
TIME_LIMIT_STEPS = 3000

PELLET_SCORE = 1
POWER_PELLET_SCORE = 5
STEP_ENERGY_COST = 0.005
STALL_ENERGY_PENALTY = 0.05
POWER_PELLETS = [(1, 1), (COLS - 2, 1), (1, ROWS - 2), (COLS - 2, ROWS - 2)]

AGENT_COLORS = [(255, 200, 0), (0, 200, 255), (255, 100, 180)]
AGENT_STARTS = [(1, ROWS - 2), (COLS - 2, ROWS - 2), (COLS // 2, 1)]

# --------------------
# Colors
# --------------------
BLACK = (0, 0, 0)
WALL_BLUE = (33, 33, 200)
PELLET_YELLOW = (250, 250, 120)
POWER_PINK = (255, 120, 200)
SHARED_RED = (200, 60, 60)
HUD_GRAY = (220, 220, 220)
WHITE = (255, 255, 255)
INTERSECTION_PURPLE = (160, 120, 255)

# --------------------
# Maze generation (simple handcrafted with shared corridor)
#   '#' wall
#   '.' pellet (filled programmatically on paths)
#   ' ' path
#   'S' shared corridor cell
# --------------------
def build_maze():
    grid = [['#' for _ in range(COLS)] for _ in range(ROWS)]
    # Carve outer ring path
    for y in range(1, ROWS - 1):
        for x in range(1, COLS - 1):
            grid[y][x] = ' '

    # Add some internal walls with gaps to form corridors
    for x in range(3, COLS - 3):
        if x % 2 == 0:
            grid[5][x] = '#'
            grid[ROWS - 6][x] = '#'

    for y in range(3, ROWS - 3):
        if y % 2 == 0:
            grid[y][7] = '#'
            grid[y][COLS - 8] = '#'

    # Central vertical shared corridor
    for y in range(3, ROWS - 3):
        grid[y][COLS // 2] = 'S'

    # Add some door gaps in walls
    grid[5][COLS // 2] = 'S'
    grid[ROWS - 6][COLS // 2] = 'S'
    grid[ROWS // 2][7] = ' '
    grid[ROWS // 2][COLS - 8] = ' '

    return grid

# Pellets on all paths except special cells or starts
def place_pellets(grid):
    pellets = set()
    power = set(POWER_PELLETS)
    for y in range(ROWS):
        for x in range(COLS):
            if grid[y][x] == ' ':
                pellets.add((x, y))
    # Remove starts and power pellets from pellets
    for s in AGENT_STARTS:
        if s in pellets:
            pellets.remove(s)
    for p in list(power):
        if p in pellets:
            pellets.remove(p)
    return pellets, power

def is_walkable(grid, pos):
    x, y = pos
    if not (0 <= x < COLS and 0 <= y < ROWS):
        return False
    return grid[y][x] != '#'

def neighbors(pos):
    x, y = pos
    return [(x, y - 1), (x + 1, y), (x, y + 1), (x - 1, y)]

def bfs_next_step(grid, start, goals, blocked):
    # Goals is a set; blocked is set of cells to avoid
    if not goals:
        return None
    q = deque()
    q.append(start)
    prev = {start: None}
    while q:
        cur = q.popleft()
        if cur in goals:
            # reconstruct path
            path = []
            node = cur
            while node != start:
                path.append(node)
                node = prev[node]
            path.reverse()
            return path[0] if path else None
        for nb in neighbors(cur):
            if nb in prev:
                continue
            if not is_walkable(grid, nb):
                continue
            if nb in blocked:
                continue
            prev[nb] = cur
            q.append(nb)
    return None

class Agent:
    def __init__(self, idx, start, color):
        self.id = idx
        self.pos = start
        self.color = color
        self.score = 0
        self.energy = 1.0
        self.alive = True
        self.wait_time = 0
        self.total_wait = 0
        self.corridor_grants = 0

    def plan(self, grid, pellets, power_pellets, occupied, shared_cells):
        # Prefer nearest power pellet if close; otherwise nearest normal pellet
        goals = set(pellets)
        if power_pellets:
            # Heuristic: include power pellets as goals with same BFS for simplicity
            goals = goals.union(power_pellets)
        blocked = set(occupied) - {self.pos}
        nxt = bfs_next_step(grid, self.pos, goals, blocked)
        if nxt is None:
            # random jitter to explore
            for nb in neighbors(self.pos):
                if is_walkable(grid, nb) and nb not in blocked:
                    return nb
            return self.pos
        return nxt

class Mediator:
    def __init__(self, agent_count):
        self.token_owner = 0  # global token pass
        self.agent_count = agent_count
        self.successful_negotiations = 0
        self.arbitrations = 0

    def resolve_shared(self, contenders):
        # If token holder among contenders, grant and rotate token
        if self.token_owner in contenders:
            winner = self.token_owner
            self.token_owner = (self.token_owner + 1) % self.agent_count
            self.successful_negotiations += 1
            return winner, "token"
        # Fallback: lottery scheduling on contenders
        winner = random.choice(contenders)
        self.arbitrations += 1
        return winner, "lottery"

def compute_intersections(grid):
    # Intersection: walkable cell with degree >= 3
    inter = set()
    for y in range(ROWS):
        for x in range(COLS):
            if not is_walkable(grid, (x, y)):
                continue
            deg = sum(1 for nb in neighbors((x, y)) if is_walkable(grid, nb))
            if deg >= 3:
                inter.add((x, y))
    return inter

def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    clock = pygame.time.Clock()
    font = pygame.font.SysFont(None, 20)

    grid = build_maze()
    pellets, power_pellets = place_pellets(grid)

    agents = [Agent(i, AGENT_STARTS[i], AGENT_COLORS[i]) for i in range(3)]
    mediator = Mediator(agent_count=len(agents))

    shared_cells = {(COLS // 2, y) for y in range(3, ROWS - 3)}
    intersections = compute_intersections(grid)

    conflicts_detected = 0
    steps = 0

    running = True
    while running:
        steps += 1
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        alive_agents = [a for a in agents if a.alive]
        if not alive_agents or steps >= TIME_LIMIT_STEPS or (not pellets and not power_pellets):
            running = False

        # Intent phase
        occupied = {a.pos for a in alive_agents}
        intents = defaultdict(list)
        plans = {}
        for a in alive_agents:
            nxt = a.plan(grid, pellets, power_pellets, occupied, shared_cells)
            plans[a.id] = nxt
            intents[nxt].append(a.id)

        # Resolve phase
        winners = {}
        for cell, contenders in intents.items():
            if len(contenders) == 1:
                winners[contenders[0]] = cell
            else:
                # Conflict
                conflicts_detected += 1
                if cell in shared_cells:
                    winner, mode = mediator.resolve_shared(contenders)
                    winners[winner] = cell
                    for pid in contenders:
                        if pid != winner:
                            ag = agents[pid]
                            ag.wait_time += 1
                            ag.total_wait += 1
                            ag.energy -= STALL_ENERGY_PENALTY
                        else:
                            if mode == "token":
                                agents[pid].corridor_grants += 1
                else:
                    # Non-shared: all wait
                    for pid in contenders:
                        ag = agents[pid]
                        ag.wait_time += 1
                        ag.total_wait += 1
                        ag.energy -= STALL_ENERGY_PENALTY

        # Prevent swaps (A->B, B->A)
        positions_before = {a.id: a.pos for a in alive_agents}
        for aid, target in list(winners.items()):
            for bid, t2 in list(winners.items()):
                if aid != bid:
                    if target == positions_before.get(bid) and t2 == positions_before.get(aid):
                        # cancel both
                        del winners[aid]
                        del winners[bid]
                        a = agents[aid]
                        b = agents[bid]
                        a.wait_time += 1
                        b.wait_time += 1
                        a.total_wait += 1
                        b.total_wait += 1
                        a.energy -= STALL_ENERGY_PENALTY
                        b.energy -= STALL_ENERGY_PENALTY
                        conflicts_detected += 1
                        break

        # Move winners and update pellets/energy
        for a in alive_agents:
            if a.id in winners:
                a.pos = winners[a.id]
            # Consume if pellet or power
            if a.pos in power_pellets:
                a.score += POWER_PELLET_SCORE
                power_pellets.remove(a.pos)
            elif a.pos in pellets:
                a.score += PELLET_SCORE
                pellets.remove(a.pos)

            # Energy drain and death
            a.energy -= STEP_ENERGY_COST
            if a.energy <= 0:
                a.alive = False

        # Draw
        screen.fill(BLACK)
        # Maze
        for y in range(ROWS):
            for x in range(COLS):
                r = pygame.Rect(x * TILE, y * TILE, TILE, TILE)
                if grid[y][x] == '#':
                    pygame.draw.rect(screen, WALL_BLUE, r)
        # Shared corridor overlay
        for (x, y) in shared_cells:
            r = pygame.Rect(x * TILE, y * TILE, TILE, TILE)
            pygame.draw.rect(screen, SHARED_RED, r, 2)
        # Intersections
        for (x, y) in intersections:
            r = pygame.Rect(x * TILE + TILE // 4, y * TILE + TILE // 4, TILE // 2, TILE // 2)
            pygame.draw.rect(screen, INTERSECTION_PURPLE, r, 1)

        # Pellets
        for (x, y) in pellets:
            cx, cy = x * TILE + TILE // 2, y * TILE + TILE // 2
            pygame.draw.circle(screen, PELLET_YELLOW, (cx, cy), 3)
        for (x, y) in power_pellets:
            cx, cy = x * TILE + TILE // 2, y * TILE + TILE // 2
            pygame.draw.circle(screen, POWER_PINK, (cx, cy), 6)

        # Agents
        for a in agents:
            if not a.alive:
                continue
            cx, cy = a.pos[0] * TILE + TILE // 2, a.pos[1] * TILE + TILE // 2
            pygame.draw.circle(screen, a.color, (cx, cy), TILE // 2 - 2)

        # HUD
        hud_y = ROWS * TILE
        pygame.draw.rect(screen, HUD_GRAY, pygame.Rect(0, hud_y, WIDTH, HEIGHT - hud_y))
        info = [
            f"Step: {steps}  Pellets left: {len(pellets)+len(power_pellets)}  Conflicts: {conflicts_detected}",
            f"Negotiations(token): {mediator.successful_negotiations}  Arbitrations(lottery): {mediator.arbitrations}",
        ]
        for i, a in enumerate(agents):
            info.append(
                f"A{i} Score:{a.score} Energy:{a.energy:.2f} Wait:{a.total_wait} Grants:{a.corridor_grants} Alive:{a.alive}"
            )
        # Compute Jain's fairness on corridor grants (avoid div by zero)
        grants = [max(0, a.corridor_grants) for a in agents]
        n = len(grants)
        s1 = sum(grants)
        s2 = sum(g * g for g in grants)
        if s2 > 0:
            jain = (s1 * s1) / (n * s2)
        else:
            jain = 0.0
        info.append(f"Jain fairness (grants): {jain:.3f}")
        for i, line in enumerate(info):
            surf = font.render(line, True, (20, 20, 20))
            screen.blit(surf, (8, hud_y + 6 + i * 18))

        pygame.display.flip()
        clock.tick(FPS)

    # Print final metrics to console
    print("Final Metrics:")
    print(f"Steps: {steps}")
    print(f"Conflicts: {conflicts_detected}")
    print(f"Negotiations(token): {mediator.successful_negotiations}")
    print(f"Arbitrations(lottery): {mediator.arbitrations}")
    for i, a in enumerate(agents):
        print(f"A{i}: Score={a.score}, TotalWait={a.total_wait}, Energy={a.energy:.2f}, Grants={a.corridor_grants}, Alive={a.alive}")

if __name__ == "__main__":
    main()
