from typing import Set, List

from constraints import Constraint
from direction import Direction, DIRS, OPPOSITE
from edges import PartEdge, FullEdge, Edge, EdgeState
from position import Position
from regionHelper import separateRegions, joinRegions


# =========================
# GRID
# =========================

class Grid:
	def __init__(self, width: int, height: int):
		self.width = width
		self.height = height
		self.cells = [
			(x, y)
			for x in range(width)
			for y in range(height)
		]
		self.holes = set()
		self.constraints = []

	def setHoles(self, holes: Set[Position]) -> None:
		for h in holes:
			self.cells.remove(h)
		self.holes = holes

	def setConstraints(self, constraints: List[PartEdge]) -> None:
		self.constraints = constraints

	def neighbor(self, cell: Position, d: Direction) -> Position | None:
		x, y = cell
		if d == Direction.N:
			y -= 1
		elif d == Direction.S:
			y += 1
		elif d == Direction.E:
			x += 1
		else:
			x -= 1

		return (x, y) if (x, y) in self.cells else None


# =========================
# EDGE CANONICALIZATION
# =========================

def canonical_edge(grid: Grid, cell: Position, d: Direction) -> Edge:
	n = grid.neighbor(cell, d)

	if n is None:
		return cell, d  # border

	other = (n, OPPOSITE[d])
	return tuple(sorted([(cell, d), other]))


# =========================
# UNION FIND
# =========================

def totalOrder(p: Position, q: Position) -> bool:
	if p[0] < q[0]:
		return True
	if p[0] > q[0]:
		return False
	return p[1] <= q[1]


def add(p: Position, q: Position) -> Position:
	return p[0] + q[0], p[1] + q[1]


class UnionFind:
	def __init__(self, elements):
		self.elements = elements
		self.parent = {e: e for e in elements}
		self.size = {e: 1 for e in elements}
		self.unjoinable = []
		self.parentList = [e for e in elements]
		self.connectables = {}
		for e in elements:
			self.connectables[e] = set()
		for e in elements:
			for delta in [[-1, 0], [1, 0], [0, 1], [0, -1]]:
				ed = add(e, delta)
				if ed in elements:
					self.connectables[e].add(ed)
					self.connectables[ed].add(e)

	def clone(self) -> 'UnionFind':
		c = UnionFind(self.elements)
		c.parent = self.parent.copy()
		c.size = self.size.copy()
		c.unjoinable = [pair.copy() for pair in self.unjoinable]  # Deep copy unjoinable pairs
		c.parentList = self.parentList.copy()
		c.connectables = {k: v.copy() for k, v in self.connectables.items()}
		return c

	def find(self, x):
		return self.parent[x]

	def union(self, a, b) -> bool:
		ra, rb = self.find(a), self.find(b)
		if not self.canJoin(ra, rb):
			return False

		if ra == rb:
			return True

		if self.size[ra] < self.size[rb]:
			ra, rb = rb, ra

		self.parent[rb] = ra
		# Update parent where parent is rb to ra
		for p in self.parent.keys():
			if self.parent[p] == rb:
				self.parent[p] = ra
		self.parentList.remove(rb)
		self.size[ra] += self.size[rb]
		del self.size[rb]
		for i in range(len(self.unjoinable)):
			if self.unjoinable[i][0] == rb:
				self.unjoinable[i][0] = ra
			if self.unjoinable[i][1] == rb:
				self.unjoinable[i][1] = ra
			# Re-normalize the pair order after replacement
			if totalOrder(self.unjoinable[i][1], self.unjoinable[i][0]):
				self.unjoinable[i][0], self.unjoinable[i][1] = self.unjoinable[i][1], self.unjoinable[i][0]

		# Remove duplicates in unjoinable after normalization
		seen = set()
		unique_unjoinable = []
		for pair in self.unjoinable:
			pair_tuple = (pair[0], pair[1])
			if pair_tuple not in seen:
				seen.add(pair_tuple)
				unique_unjoinable.append(pair)
		self.unjoinable = unique_unjoinable
		cpyconra = self.connectables[ra].copy()
		cpyconra.remove(rb)
		for v in self.connectables[ra]:
			if [rb, v] in self.unjoinable or [v, rb] in self.unjoinable:
				cpyconra.remove(v)
		toAdd = []
		for v in self.connectables[rb]:
			if v == ra:
				continue
			self.connectables[v].remove(rb)
			if not ([ra, v] in self.unjoinable or [v, ra] in self.unjoinable):
				toAdd.append(v)
				self.connectables[v].add(ra)
		cpyconra.update(toAdd)
		self.connectables[ra] = cpyconra
		del self.connectables[rb]
		return True

	def disjoint(self, a, b) -> bool:
		ra, rb = self.find(a), self.find(b)
		if ra == rb:
			return False
		# Normalize pair order for consistent storage
		if totalOrder(rb, ra):
			ra, rb = rb, ra
		if [ra, rb] in self.unjoinable:
			return True
		self.unjoinable.append([ra, rb])
		if rb in self.connectables[ra]:
			self.connectables[ra].remove(rb)
			self.connectables[rb].remove(ra)
		return True

	def canJoin(self, a, b) -> bool:
		ra, rb = self.find(a), self.find(b)
		if ra == rb:
			return True
		# Normalize pair order
		if totalOrder(rb, ra):
			ra, rb = rb, ra
		if [ra, rb] in self.unjoinable:
			return False
		return True

	def getAdjacent(self, a) -> Set:
		ra = self.find(a)
		unjoinable_pairs = [r for r in self.unjoinable if ra in r]
		# Normalize representatives after unions and filter out self-references
		adjacent_set = set()
		for r in unjoinable_pairs:
			neighbor = r[0] if r[1] == ra else r[1]
			neighbor = self.find(neighbor)
			if neighbor != ra:  # Don't include self-references
				adjacent_set.add(neighbor)
		adjacent_set.update(self.connectables[ra])
		return adjacent_set

	def getInsides(self, a) -> Set:
		ra = self.find(a)
		return set([e for e in self.elements if self.find(e) == ra])


# =========================
# STATE
# =========================

edgesText = {
	Direction.N: "-",
	Direction.S: "-",
	Direction.E: "|",
	Direction.W: "|"
}
edgeUnknownText = "."
edgeAbsent = " "
tileText = " "
cornerText = "+"
emptyCellText = " "
holeText = "~"


def edge_cells(edge: Edge) -> tuple[Position, Position | None]:
	if isinstance(edge[1], tuple):
		((c1, _), (c2, _)) = edge
		return c1, c2
	else:
		# bord
		return edge[0], None


class State:
	def __init__(self, grid: Grid):
		self.grid = grid
		self.edges = {}
		self.cache_cell_edges = {}
		self.cache_cell_vertex = {}
		self.calledSetEdge = False

		for c in grid.cells:
			for d in DIRS:
				key = canonical_edge(grid, c, d)
				self.edges[key] = EdgeState.UNKNOWN if isinstance(key[1], tuple) else EdgeState.PRESENT
		self.uf = UnionFind(self.grid.cells)

	def set(self, other: 'State') -> None:
		self.edges = other.edges.copy()
		self.cache_cell_edges = other.cache_cell_edges
		self.cache_cell_vertex = other.cache_cell_vertex
		self.uf = other.uf.clone()
		self.calledSetEdge = False

	def clone(self) -> 'State':
		s = State(self.grid)
		s.edges = self.edges.copy()
		s.cache_cell_edges = self.cache_cell_edges
		s.cache_cell_vertex = self.cache_cell_vertex
		s.uf = self.uf.clone()
		s.calledSetEdge = False
		return s

	def set_edge(self, edge: FullEdge, val: EdgeState, recursiveSplit=True) -> bool:
		if self.edges[edge] is not EdgeState.UNKNOWN:
			return self.edges[edge] == val

		# Forbid walls in same region
		a, b = edge_cells(edge)
		ra, rb = self.uf.find(a) if a else None, self.uf.find(b) if b else None
		if val == EdgeState.PRESENT and a and b and ra == rb:
			return False
		if val == EdgeState.ABSENT and a and b and ra != rb and (
				[ra, rb] in self.uf.unjoinable or [rb, ra] in self.uf.unjoinable):
			return False

		self.calledSetEdge = True
		self.edges[edge] = val
		if val == EdgeState.ABSENT and a and b:
			if recursiveSplit:
				if not joinRegions(self, a, b):
					return False
		elif val == EdgeState.PRESENT and a and b:
			if recursiveSplit:
				if not separateRegions(self, a, b):
					return False
		return True

	def cell_edges(self, cell: Position) -> list[Edge]:
		if cell in self.cache_cell_edges:
			return self.cache_cell_edges[cell]
		edges = []
		for d in DIRS:
			edge = canonical_edge(self.grid, cell, d)
			edges.append(edge)
		self.cache_cell_edges[cell] = edges
		return edges

	def cellsAroundVertex(self, vertex: Position) -> list[Position]:
		if vertex in self.cache_cell_vertex:
			return self.cache_cell_vertex[vertex]
		cells = []
		for d in [(-1, -1), (0, -1), (-1, 0), (0, 0)]:
			cell = add(vertex, d)
			if cell in self.grid.cells:
				cells.append(cell)
		self.cache_cell_vertex[vertex] = cells
		return cells

	def undecided_edges(self) -> list[FullEdge]:
		return [e for e, v in self.edges.items() if v is EdgeState.UNKNOWN]

	def show(self, constraints=None, holes=None) -> None:
		if constraints is None:
			constraints = []
		if holes is None:
			holes = set()
		evenLines = ["+ " * self.grid.width + "+" for _ in range(self.grid.height + 1)]
		oddLines = ["  " * self.grid.width + " " for _ in range(self.grid.height)]
		for h in holes:
			oddLines[h[1]] = oddLines[h[1]][:2 * h[0] + 1] + holeText + oddLines[h[1]][2 * h[0] + 2:]
		# For each cell, remove corresponding walls
		for edge, state in self.edges.items():
			e = edge if isinstance(edge[1], tuple) else (edge, None)
			replaceEdge = edgeUnknownText if self.edges[edge] is EdgeState.UNKNOWN else edgesText[e[0][1]]
			# if edge is PartEdge, take x,y from edge[0] and d from edge[1]
			# else take x,y from edge[0][0] and d from edge[0][1]
			((x, y), d) = e[0]
			if self.edges[edge] != EdgeState.ABSENT:
				if d == Direction.N:
					evenLines[y] = evenLines[y][:2 * x + 1] + replaceEdge + evenLines[y][2 * x + 2:]
				elif d == Direction.S:
					evenLines[y + 1] = evenLines[y + 1][:2 * x + 1] + replaceEdge + evenLines[y + 1][2 * x + 2:]
				elif d == Direction.E:
					oddLines[y] = oddLines[y][:2 * x + 2] + replaceEdge + oddLines[y][2 * x + 3:]
				elif d == Direction.W:
					oddLines[y] = oddLines[y][:2 * x] + replaceEdge + oddLines[y][2 * x + 1:]

		for c in constraints:
			hasattr(c, "show") and c.show(self, evenLines, oddLines)
		# Display result
		t = ""
		for i in range(self.grid.height * 2 + 1):
			if i % 2 == 0:
				t += evenLines[i // 2] + "\n"
			else:
				t += oddLines[i // 2] + "\n"
		print(t)

	def is_valid_partition(self) -> bool:
		for c in self.grid.constraints:
			if not c.check(self):
				return False
		for edge, val in self.edges.items():
			a, b = edge_cells(edge)

			if a and b:
				same = (self.uf.find(a) == self.uf.find(b))

				if same and val == EdgeState.PRESENT:
					return False

				if not same and val == EdgeState.ABSENT:
					return False

		return True


# =========================
# VERTICES
# =========================

def get_vertices(grid: Grid) -> dict[Position, set[Edge]]:
	vertices = {}

	for x in range(grid.width + 1):
		for y in range(grid.height + 1):
			edges = set()

			for dx, dy, d1, d2 in [
				(-1, -1, Direction.S, Direction.E), (0, -1, Direction.S, Direction.W),
				(-1, 0, Direction.N, Direction.E), (0, 0, Direction.N, Direction.W)
			]:
				cell = (x + dx, y + dy)
				if cell in grid.cells:
					edge = canonical_edge(grid, cell, d1)
					edges.add(edge)
					edge = canonical_edge(grid, cell, d2)
					edges.add(edge)

			if edges:
				vertices[(x, y)] = edges

	return vertices


# =========================
# SOLVER
# =========================

def choose_edge(solver: Solver, state: State) -> FullEdge:
	return state.undecided_edges()[0]
	# undecided = state.undecided_edges()
	# if not undecided:
	# 	return None
	# return max(undecided, key=lambda e: solver.failed_edges.get(e, 0))


def checkConnectables(uf: UnionFind) -> List[tuple[Position, Position]]:
	wrongs = []
	for a in uf.parentList:
		for b in uf.getAdjacent(a):
			aInB = a in uf.connectables[b]
			bInA = b in uf.connectables[a]
			if aInB != bInA:
				wrongs.append((a, b))
	return wrongs


class Solver:
	def __init__(self, grid: Grid, constraints: list[Constraint]):
		self.grid = grid
		self.constraints = constraints
		self.solutions = []
		self.max_solutions = 2

	def propagate_all(self, state: State) -> bool:
		shouldRepeat = True
		s = state.clone()
		while shouldRepeat:
			s.calledSetEdge = False
			for c in self.constraints:
				if not c.propagate(s):
					return False
			shouldRepeat = s.calledSetEdge

		state.set(s)
		return True

	def solve(self, state: State) -> None:
		stack = [(state, None, None)]  # Stack to simulate recursion, storing (state, edge, value)
		wrongStates = []
		while stack:
			current_state, edge, val = stack.pop()
			if current_state in wrongStates:
				continue

			tmpCurrentState = current_state.clone()

			if edge is not None and val is not EdgeState.UNKNOWN:
				if not current_state.set_edge(edge, val):
					wrongStates.append(tmpCurrentState)
					continue

			if not self.propagate_all(current_state):
				wrongStates.append(tmpCurrentState)
				continue

			if not current_state.undecided_edges():
				if current_state.is_valid_partition():
					# Check if solution already is in self.solutions
					if any([all([s.edges[e] == v for e, v in current_state.edges.items()]) for s in self.solutions]):
						continue
					self.solutions.append(current_state)
				continue
			# current_state.show(self.constraints, self.grid.holes)
			print(len(stack))
			next_edge = choose_edge(self, current_state)
			stack.append((current_state.clone(), next_edge, EdgeState.PRESENT))
			stack.append((current_state.clone(), next_edge, EdgeState.ABSENT))
