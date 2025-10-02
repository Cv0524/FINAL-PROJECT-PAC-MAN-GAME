"""
Multi-Agent Pac-Men Challenge (Tkinter)
- Maze with walls and path (odd/odd walls as pillars)
- Pellets placed on paths
- 3 autonomous agents seeking pellets
- Shared-route corridors with negotiation + token synchronization
- Metrics collection and UI display
"""

import tkinter as tk
import random
from collections import deque, defaultdict
import time
import math
import statistics

# ---------- Configuration ----------
GRID_SIZE = 21          # odd for centered start (21x21)
CELL_SIZE = 28          # pixels
AGENT_SIZE = 18         # diameter in pixels (smaller than cell)
TICK_MS = 250           # world tick in milliseconds
NUM_AGENTS = 3
PELLET_VALUE = 10
POWER_PELLET_VALUE = 50
ENERGY_LOSS_ON_PENALTY = 20
MAX_ENERGY = 200
# -----------------------------------

# Colors
WALL_COLOR = "#111"
PATH_COLOR = "#fff"
PELLET_COLOR = "#f4c542"
POWER_PELLET_COLOR = "#ff6b6b"
AGENT_COLORS = ["#ffcc00", "#4ad0ff", "#9bff7a"]

random.seed(1)  # deterministic for consistent behavior; remove for variety


# ---------- Utility functions ----------
def in_bounds(r, c):
    return 0 <= r < GRID_SIZE and 0 <= c < GRID_SIZE

dirs = [(-1, 0), (1, 0), (0, -1), (0, 1)]
# --------------------------------------


class Maze:
    """
    Maze grid with simple pillar-walls approach:
    - If both r and c are odd -> wall (pillar)
    - Else path
    This leaves corridors for movement.
    Maze also stores pellet locations and corridor ids (shared routes).
    """
    def __init__(self):
        self.grid = [[0]*GRID_SIZE for _ in range(GRID_SIZE)]  # 0 path, 1 wall
        self.pellets = {}  # (r,c) -> value
        self.corridor_id = {}  # (r,c) -> corridor id or None
        self.generate_basic_maze()
        self.place_pellets()
        self.define_shared_corridors()

    def generate_basic_maze(self):
        for r in range(GRID_SIZE):
            for c in range(GRID_SIZE):
                if (r % 2 == 1) and (c % 2 == 1):
                    self.grid[r][c] = 1  # wall pillar
                else:
                    self.grid[r][c] = 0  # path

    def place_pellets(self):
        # put pellet on most paths, but not where our agents will start (center)
        for r in range(GRID_SIZE):
            for c in range(GRID_SIZE):
                if self.grid[r][c] == 0:
                    # keep center empty for agent starts
                    if (r, c) == (GRID_SIZE//2, GRID_SIZE//2):
                        continue
                    # random chance to have pellet
                    if random.random() < 0.55:
                        self.pellets[(r, c)] = PELLET_VALUE
        # place a few power pellets
        for _ in range(6):
            r = random.randrange(0, GRID_SIZE)
            c = random.randrange(0, GRID_SIZE)
            if self.grid[r][c] == 0 and (r, c) in self.pellets:
                self.pellets[(r, c)] = POWER_PELLET_VALUE

    def define_shared_corridors(self):
        """
        Define several 'shared corridors' (each is a small set of contiguous path cells)
        We'll mark corridor ids for certain linear segments (pref-defined).
        """
        self.corridor_map = defaultdict(list)
        # simple approach: pick some straight corridors across the grid mid-lines
        id_counter = 1
        mid = GRID_SIZE // 2
        # horizontal corridor near top quarter
        start_r = mid - 4
        if start_r < 1: start_r = 1
        for c in range(2, GRID_SIZE-2):
            if self.grid[start_r][c] == 0:
                self.corridor_id[(start_r, c)] = id_counter
                self.corridor_map[id_counter].append((start_r, c))
        id_counter += 1

        # vertical corridor near left quarter
        start_c = mid - 4
        if start_c < 1: start_c = 1
        for r in range(2, GRID_SIZE-2):
            if self.grid[r][start_c] == 0:
                self.corridor_id[(r, start_c)] = id_counter
                self.corridor_map[id_counter].append((r, start_c))
        id_counter += 1

        # central horizontal corridor (long)
        for c in range(1, GRID_SIZE-1):
            if self.grid[mid][c] == 0:
                self.corridor_id[(mid, c)] = id_counter
                self.corridor_map[id_counter].append((mid, c))
        id_counter += 1

        # a couple of smaller corridors randomly
        for _ in range(2):
            orientation = random.choice(["h", "v"])
            idc = id_counter
            if orientation == "h":
                r = random.randrange(1, GRID_SIZE-1, 2)  # choose a path row
                for c in range(2, GRID_SIZE-2):
                    if self.grid[r][c] == 0:
                        self.corridor_id[(r, c)] = idc
                        self.corridor_map[idc].append((r, c))
            else:
                c = random.randrange(1, GRID_SIZE-1, 2)
                for r in range(2, GRID_SIZE-2):
                    if self.grid[r][c] == 0:
                        self.corridor_id[(r, c)] = idc
                        self.corridor_map[idc].append((r, c))
            id_counter += 1

        # ensure any cell not explicitly assigned remains absent from corridor_id
        # done: self.corridor_id set only for selected cells


# ---------- Agent implementation ----------
class Agent:
    def __init__(self, aid, start_pos, color, maze: Maze):
        self.id = aid
        self.row, self.col = start_pos
        self.color = color
        self.maze = maze
        self.score = 0
        self.energy = MAX_ENERGY
        self.alive = True
        self.wait_time_total = 0
        self.wait_counts = 0
        self.failed_negotiations = 0
        self.successful_negotiations = 0
        self.conflicts = 0
        self.path = []  # planned path (list of (r,c))
        self.target = None  # current pellet target
        self.stalled_ticks = 0
        self.dropdown = False  # dropped out flag
        # alternating priority state for fairness (0 or 1)
        self.alternate_priority_state = 0

    def plan_to_nearest_pellet(self, occupied_cells):
        """
        BFS to nearest pellet (shortest path), avoiding walls and occupied cells.
        Return path list excluding current cell.
        """
        if not self.maze.pellets:
            self.path = []
            self.target = None
            return
        start = (self.row, self.col)
        q = deque()
        q.append(start)
        parent = {start: None}
        found_target = None
        # BFS
        while q:
            cur = q.popleft()
            if cur in self.maze.pellets:
                found_target = cur
                break
            for dr, dc in dirs:
                nr, nc = cur[0] + dr, cur[1] + dc
                if not in_bounds(nr, nc): continue
                if self.maze.grid[nr][nc] == 1: continue
                if (nr, nc) in occupied_cells and (nr, nc) != start:
                    # avoid stepping into currently occupied cells (simple safety)
                    continue
                if (nr, nc) not in parent:
                    parent[(nr, nc)] = cur
                    q.append((nr, nc))
        if found_target is None:
            self.path = []
            self.target = None
            return
        # reconstruct path
        p = []
        cur = found_target
        while parent[cur] is not None:
            p.append(cur)
            cur = parent[cur]
        p.reverse()
        self.path = p
        self.target = found_target

    def next_step(self):
        """Return next cell to move into or None if idle."""
        if not self.path:
            return None
        return self.path[0]

    def pop_step(self):
        """Pop the next step after moving into it."""
        if self.path:
            self.path.pop(0)

    def apply_pellet(self, pos):
        """Collect pellet if present."""
        if pos in self.maze.pellets:
            val = self.maze.pellets.pop(pos)
            self.score += val

    def record_wait(self, ticks=1):
        self.wait_time_total += ticks
        self.wait_counts += 1
        self.stalled_ticks += ticks

    def average_wait(self):
        if self.wait_counts == 0:
            return 0.0
        return self.wait_time_total / self.wait_counts

    def is_in_corridor(self, cell):
        return cell in self.maze.corridor_id

    def __repr__(self):
        return f"Agent({self.id}) score={self.score} energy={self.energy} pos=({self.row},{self.col})"


# ---------- Negotiation manager ----------
class CorridorManager:
    """
    Manage corridor tokens and negotiation.
    Each corridor id has a single token. Agents must request token to enter corridor cells.
    When multiple agents request simultaneously, apply negotiation rules:
      - Primary: lower score (help weaker agent)
      - If tie: random lottery
      - Fallback: predetermined priority by agent id or random arbitration
    Metrics tracked: conflicts_detected, successful_negotiations
    """
    def __init__(self):
        self.token_holder = {}  # corridor_id -> agent_id or None
        self.pending_requests = defaultdict(list)  # corridor_id -> list of (agent, desired_cell)
        self.conflicts_detected = 0
        self.successful_negotiations = 0
        self.arbitrations = 0

    def request(self, agent: Agent, corridor_id, desired_cell):
        self.pending_requests[corridor_id].append((agent, desired_cell))

    def resolve_requests(self):
        """
        Resolve all pending requests. If corridor is free and exactly one requester -> grant.
        If multiple -> negotiate.
        """
        results = {}  # (agent -> granted boolean, reason)
        for cid, reqs in list(self.pending_requests.items()):
            if not reqs:
                continue
            holder = self.token_holder.get(cid, None)
            if holder is not None:
                # corridor occupied -> nobody gets it this tick
                for agent, _ in reqs:
                    results[agent] = (False, "occupied")
                self.pending_requests[cid] = []
                continue
            if len(reqs) == 1:
                # single requester -> grant token
                agent, _ = reqs[0]
                self.token_holder[cid] = agent.id
                results[agent] = (True, "granted")
                self.successful_negotiations += 1
                self.pending_requests[cid] = []
                continue
            # multiple requesters -> negotiation
            self.conflicts_detected += 1
            # choose winner: lower score priority (to balance); then lottery on ties
            reqs_sorted = sorted(reqs, key=lambda a_d: (a_d[0].score, a_d[0].id))
            # Note: lower score first; but to reduce starvation we can implement alternating priority
            # We'll do: compute minimal score then check if multiple have that minimal score -> lottery
            min_score = reqs_sorted[0][0].score
            candidates = [ag for ag, cell in reqs if ag.score == min_score]
            if len(candidates) > 1:
                winner = random.choice(candidates)
                reason = "lottery among lowest-score"
            else:
                winner = reqs_sorted[0][0]
                reason = "lowest-score priority"
            # grant token to winner
            self.token_holder[cid] = winner.id
            # mark results: winner True, losers False with penalty reason
            for agent, _ in reqs:
                if agent is winner:
                    results[agent] = (True, reason)
                    agent.successful_negotiations += 1
                else:
                    results[agent] = (False, "lost_negotiation")
                    agent.conflicts += 1
                    agent.failed_negotiations += 1
            self.pending_requests[cid] = []
            self.successful_negotiations += 1
            # if some fairness mechanisms wanted, implement here (not needed now)

        # clear pending requests map
        self.pending_requests.clear()
        return results

    def release_token_by_agent(self, agent_id):
        # release any tokens held by this agent id (called when agent leaves corridor)
        to_release = []
        for cid, holder in list(self.token_holder.items()):
            if holder == agent_id:
                to_release.append(cid)
        for cid in to_release:
            self.token_holder.pop(cid, None)

    def release_token_by_cell(self, corridor_id, agent_id):
        # release token for a corridor if held by this agent
        if self.token_holder.get(corridor_id, None) == agent_id:
            self.token_holder.pop(corridor_id, None)

    def is_held(self, corridor_id):
        return self.token_holder.get(corridor_id, None) is not None

    def holder_of(self, corridor_id):
        return self.token_holder.get(corridor_id, None)


# ---------- Main Application ----------
class PacMenApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Multi-Agent Pac-Men Challenge")
        self.canvas = tk.Canvas(root, width=GRID_SIZE*CELL_SIZE, height=GRID_SIZE*CELL_SIZE, bg=PATH_COLOR)
        self.canvas.grid(row=0, column=0, padx=5, pady=5)

        # Stats panel
        self.stats_frame = tk.Frame(root)
        self.stats_frame.grid(row=0, column=1, sticky="nw")
        self.stats_text = tk.Text(self.stats_frame, width=40, height=30, bg="#111", fg="#eee")
        self.stats_text.pack()

        # Maze and manager
        self.maze = Maze()
        self.corridor_mgr = CorridorManager()

        # Agent creation: place them at distinct starting positions (spread out)
        starts = self._choose_start_positions(NUM_AGENTS)
        self.agents = []
        for i in range(NUM_AGENTS):
            agent = Agent(i+1, starts[i], AGENT_COLORS[i % len(AGENT_COLORS)], self.maze)
            self.agents.append(agent)

        # for drawing objects
        self.canvas_ids = {"walls": [], "pellets": {}, "agents": {}, "corridor_cells": []}

        # metrics
        self.tick_count = 0
        self.history_conflicts = 0

        # draw initial state
        self.draw_grid()
        self.draw_pellets()
        self.draw_corridors()
        self.draw_agents()

        # Occupation map (dynamic)
        self.occupied = set((a.row, a.col) for a in self.agents)

        # Start AI loop
        self.root.after(500, self.tick)

    def _choose_start_positions(self, n):
        # pick positions near different quadrants that are path cells and distinct
        spots = []
        possible = []
        for r in range(GRID_SIZE):
            for c in range(GRID_SIZE):
                if self.maze.grid[r][c] == 0:
                    possible.append((r, c))
        random.shuffle(possible)
        # prefer positions around center, but separated
        mid = GRID_SIZE // 2
        offsets = [(-2, -2), (-2, 2), (2, -2), (2, 2)]
        chosen = []
        idx = 0
        while len(chosen) < n and idx < len(possible):
            pos = possible[idx]
            # ensure adequate spacing from already chosen
            too_close = any(abs(pos[0]-c[0]) + abs(pos[1]-c[1]) < 4 for c in chosen)
            if not too_close:
                chosen.append(pos)
            idx += 1
        # fallback
        while len(chosen) < n:
            chosen.append(possible.pop())
        return chosen

    def draw_grid(self):
        # draw walls and grid cells as rectangles
        for r in range(GRID_SIZE):
            for c in range(GRID_SIZE):
                x0 = c * CELL_SIZE
                y0 = r * CELL_SIZE
                x1 = x0 + CELL_SIZE
                y1 = y0 + CELL_SIZE
                if self.maze.grid[r][c] == 1:
                    rect = self.canvas.create_rectangle(x0, y0, x1, y1, fill=WALL_COLOR, outline=WALL_COLOR)
                    self.canvas_ids["walls"].append(rect)
                else:
                    # draw background path if desired
                    self.canvas.create_rectangle(x0, y0, x1, y1, fill=PATH_COLOR, outline="#eee", width=0)

    def draw_pellets(self):
        # remove old pellet markers
        for pid in list(self.canvas_ids["pellets"].values()):
            try:
                self.canvas.delete(pid)
            except Exception:
                pass
        self.canvas_ids["pellets"].clear()
        for (r, c), val in list(self.maze.pellets.items()):
            cx = c * CELL_SIZE + CELL_SIZE//2
            cy = r * CELL_SIZE + CELL_SIZE//2
            if val >= POWER_PELLET_VALUE:
                ov = self.canvas.create_oval(cx-6, cy-6, cx+6, cy+6, fill=POWER_PELLET_COLOR, outline="")
            else:
                ov = self.canvas.create_oval(cx-3, cy-3, cx+3, cy+3, fill=PELLET_COLOR, outline="")
            self.canvas_ids["pellets"][(r,c)] = ov

    def draw_corridors(self):
        # draw semi-transparent overlay for corridor cells
        for cid, cells in self.maze.corridor_map.items():
            for (r, c) in cells:
                x0 = c * CELL_SIZE
                y0 = r * CELL_SIZE
                x1 = x0 + CELL_SIZE
                y1 = y0 + CELL_SIZE
                rect = self.canvas.create_rectangle(x0+3, y0+3, x1-3, y1-3, outline="#888", dash=(2,2))
                self.canvas_ids["corridor_cells"].append(rect)

    def draw_agents(self):
        # initial drawing of agents
        for agent in self.agents:
            cx = agent.col * CELL_SIZE + CELL_SIZE//2
            cy = agent.row * CELL_SIZE + CELL_SIZE//2
            x0, y0 = cx - AGENT_SIZE//2, cy - AGENT_SIZE//2
            x1, y1 = cx + AGENT_SIZE//2, cy + AGENT_SIZE//2
            oid = self.canvas.create_oval(x0, y0, x1, y1, fill=agent.color, outline="#333")
            text_id = self.canvas.create_text(cx, cy, text=str(agent.id), fill="#111")
            self.canvas_ids["agents"][agent.id] = (oid, text_id)

    def update_agent_draw(self, agent: Agent):
        oid, tid = self.canvas_ids["agents"][agent.id]
        cx = agent.col * CELL_SIZE + CELL_SIZE//2
        cy = agent.row * CELL_SIZE + CELL_SIZE//2
        x0, y0 = cx - AGENT_SIZE//2, cy - AGENT_SIZE//2
        x1, y1 = cx + AGENT_SIZE//2, cy + AGENT_SIZE//2
        self.canvas.coords(oid, x0, y0, x1, y1)
        self.canvas.coords(tid, cx, cy)

    def tick(self):
        """
        Main simulation tick:
        1. For each alive agent: plan (BFS) to nearest pellet
        2. Determine desired next step for each agent
        3. If next step is corridor cell, agent requests corridor token
        4. CorridorManager resolves requests -> grant/deny
        5. Movement executed for granted moves (including non-corridor steps)
        6. Pellet collection, scoring, energy updates
        7. Metrics update and redraw
        """
        self.tick_count += 1
        # 1. plan
        occupied_cells = set((a.row, a.col) for a in self.agents if a.alive)
        for agent in self.agents:
            if not agent.alive:
                continue
            # if no target or pellet gone, replan
            if agent.target not in self.maze.pellets:
                agent.plan_to_nearest_pellet(occupied_cells)
            # if still no path, maybe wander randomly
            if not agent.path:
                # random adjacent move proposal to keep things moving
                # pick any adjacent path (not wall) even occupied (but we'll check later)
                nbrs = []
                for dr, dc in dirs:
                    nr, nc = agent.row+dr, agent.col+dc
                    if in_bounds(nr, nc) and self.maze.grid[nr][nc] == 0:
                        nbrs.append((nr, nc))
                if nbrs:
                    agent.path = [random.choice(nbrs)]

        # 2. determine desired steps
        desired_moves = {}  # agent -> (nr,nc)
        for agent in self.agents:
            if not agent.alive:
                continue
            nxt = agent.next_step()
            if nxt is not None:
                desired_moves[agent] = nxt

        # 3. corridor token requests
        # clear previous pending (corridor_mgr handles its own map)
        # check for agents whose next cell is corridor cell -> request
        for agent, nxt in desired_moves.items():
            if self.maze.corridor_id.get(nxt, None) is not None:
                cid = self.maze.corridor_id[nxt]
                self.corridor_mgr.request(agent, cid, nxt)

        # 4. resolve corridor requests
        negotiation_results = self.corridor_mgr.resolve_requests()
        # negotiation_results: agent -> (granted bool, reason)

        # 5. conflict handling for non-corridor collisions: if two agents want same cell
        dest_map = defaultdict(list)  # dest cell -> list(agent)
        for agent, nxt in desired_moves.items():
            dest_map[nxt].append(agent)

        # We'll mark which agents are allowed to move this tick
        allowed_to_move = set()

        # first handle corridor-granted agents
        for agent, nxt in desired_moves.items():
            if self.maze.corridor_id.get(nxt, None) is not None:
                cid = self.maze.corridor_id[nxt]
                # check if agent was granted token
                res = negotiation_results.get(agent, None)
                if res is None:
                    # no request result -> maybe corridor free and no request? (impossible)
                    # deny movement this tick
                    agent.record_wait(1)
                else:
                    granted, reason = res
                    if granted:
                        allowed_to_move.add(agent)
                        # they now hold token; corridor_mgr has assigned token_holder
                    else:
                        # denied: penalty or waiting
                        agent.record_wait(1)
                        agent.energy -= 1  # small energy cost for waiting
                        # if lost negotiation, apply penalty every few failures
                        if reason == "lost_negotiation":
                            agent.energy -= 0  # penalty deferred to movement conflict resolution
            else:
                # non-corridor: will resolve in dest handling below
                pass

        # handle non-corridor and general collisions
        for dest, agents_wanting in dest_map.items():
            if len(agents_wanting) == 1:
                agent = agents_wanting[0]
                # if not already set (corridor grant), allow
                if agent not in allowed_to_move:
                    allowed_to_move.add(agent)
            else:
                # multiple agents want same non-corridor cell -> conflict
                self.corridor_mgr.conflicts_detected += 1
                self.history_conflicts += 1
                # simple arbitration: random pick (but we give slight preference to lower score)
                agents_wanting_sorted = sorted(agents_wanting, key=lambda a: (a.score, a.id))
                min_score = agents_wanting_sorted[0].score
                candidates = [a for a in agents_wanting if a.score == min_score]
                winner = random.choice(candidates)
                # allow winner
                allowed_to_move.add(winner)
                # losers wait & get minor penalty
                for loser in agents_wanting:
                    if loser is not winner:
                        loser.record_wait(1)
                        loser.energy -= 2
                        loser.failed_negotiations += 1
                        loser.conflicts += 1

        # finalize moves: check that the destination is unoccupied by other agents who will also move there in same tick
        # Build a map of dest -> agent among allowed_to_move (resolve tie if any)
        final_dest_owner = {}
        for agent in list(allowed_to_move):
            dest = desired_moves.get(agent, (agent.row, agent.col))
            # confirm not moving into a currently occupied cell by an agent that won't move
            occupied_by = None
            for other in self.agents:
                if (other.row, other.col) == dest and other not in allowed_to_move:
                    occupied_by = other
                    break
            if occupied_by is not None:
                # cannot move into occupied cell; agent stalls
                agent.record_wait(1)
                agent.energy -= 1
                allowed_to_move.discard(agent)
                continue
            # if multiple allowed_to_move map to same dest, pick one via score/lottery (shouldn't happen due prior resolution)
            if dest in final_dest_owner:
                # conflict: pick lower score
                other_agent = final_dest_owner[dest]
                if agent.score < other_agent.score:
                    # agent wins, other loses
                    final_dest_owner[dest] = agent
                    other_agent.record_wait(1)
                    other_agent.energy -= 2
                    allowed_to_move.discard(other_agent)
                else:
                    # current agent loses
                    agent.record_wait(1)
                    agent.energy -= 2
                    allowed_to_move.discard(agent)
            else:
                final_dest_owner[dest] = agent

        # execute moves
        moved_agents = []
        for dest, agent in final_dest_owner.items():
            # move agent to dest
            agent.row, agent.col = dest
            agent.pop_step()
            moved_agents.append(agent)
            # release corridor tokens if agent left corridor (release by agent id)
            # If the previous cell was corridor and different corridor id than new cell, release
            # Note: corridor_mgr releases when leaving corridor cell (we'll check previous cell)
        # After moving, release corridor tokens for agents that left corridor cells
        for agent in moved_agents:
            # if agent no longer in corridor cell, release tokens for any corridor it held
            # find corridor id at agent position
            pos = (agent.row, agent.col)
            cid = self.maze.corridor_id.get(pos, None)
            # release tokens for corridors not containing the current pos but held by agent
            # simpler: if agent holds any tokens but is not currently inside them, release
            self.corridor_mgr.release_token_by_agent(agent.id)
            # If the destination is corridor cell, keep token assigned to this agent (corridor_mgr already set it)

            # collect pellet if any
            if pos in self.maze.pellets:
                # collect pellet
                agent.apply_pellet(pos)
                # small energy regain on pellet
                agent.energy = min(MAX_ENERGY, agent.energy + 2)

        # agents who did not move pay small energy drain for standing by
        for agent in self.agents:
            if not agent.alive:
                continue
            if agent not in moved_agents:
                # increased stall time if they had a desired move but were denied
                if agent.next_step():
                    agent.record_wait(1)
                    agent.energy -= 1
                else:
                    # idle energy drain
                    agent.energy -= 0.2

        # drop out logic
        for agent in self.agents:
            if agent.alive and agent.energy <= 0:
                agent.alive = False
                agent.dropdown = True
                # release any tokens held
                self.corridor_mgr.release_token_by_agent(agent.id)

        # update visual pellet markers
        self.draw_pellets()

        # update canvas agent positions
        for agent in self.agents:
            self.update_agent_draw(agent)

        # update stats display
        self.update_stats()

        # check termination: no pellets left or all agents dead
        if not self.maze.pellets or all(not a.alive for a in self.agents):
            self.end_simulation()
            return

        # schedule next tick
        self.root.after(TICK_MS, self.tick)

    def fairness_metric(self):
        # naive fairness: std dev of pellet counts or scores (lower is fairer)
        scores = [a.score for a in self.agents]
        if len(scores) <= 1:
            return 1.0
        mean = sum(scores)/len(scores)
        variance = sum((s-mean)**2 for s in scores)/len(scores)
        sd = math.sqrt(variance)
        fairness = 1 / (1 + sd)  # map to (0,1], higher => fairer
        return fairness

    def update_stats(self):
        self.stats_text.configure(state="normal")
        self.stats_text.delete("1.0", tk.END)
        lines = []
        lines.append(f"Tick: {self.tick_count}")
        lines.append(f"Pellets remaining: {len(self.maze.pellets)}")
        lines.append("")
        for agent in self.agents:
            lines.append(f"Agent {agent.id} (alive={agent.alive})")
            lines.append(f"  Score: {agent.score}   Energy: {int(agent.energy)}")
            lines.append(f"  Pos: ({agent.row},{agent.col})  Target: {agent.target}")
            lines.append(f"  Conflicts lost: {agent.failed_negotiations}  successes: {agent.successful_negotiations}")
            lines.append(f"  Avg wait: {agent.average_wait():.2f}  Total waits: {agent.wait_counts}")
            lines.append("")
        lines.append("Corridor manager stats:")
        lines.append(f"  Conflicts detected: {self.corridor_mgr.conflicts_detected}")
        lines.append(f"  Successful negotiations: {self.corridor_mgr.successful_negotiations}")
        lines.append(f"  History conflicts (non-corridor): {self.history_conflicts}")
        lines.append("")
        lines.append(f"Fairness metric (higher = fairer): {self.fairness_metric():.3f}")
        lines.append("")
        lines.append("Controls: The agents run autonomously.")
        self.stats_text.insert(tk.END, "\n".join(lines))
        self.stats_text.configure(state="disabled")

    def end_simulation(self):
        self.stats_text.configure(state="normal")
        self.stats_text.insert(tk.END, "\n\nSimulation ended.\nFinal scores:\n")
        for agent in sorted(self.agents, key=lambda a: -a.score):
            self.stats_text.insert(tk.END, f"Agent {agent.id}: score={agent.score}  alive={agent.alive}\n")
        self.stats_text.configure(state="disabled")
        # do not schedule more ticks


def main():
    root = tk.Tk()
    app = PacMenApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
