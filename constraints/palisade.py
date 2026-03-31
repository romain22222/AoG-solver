from enum import Enum
from edges import EdgeState
from constraints.base import Constraint, GridSymbol


class CycleType(Enum):
	EMPTY = "empty"
	ONE = "one"
	STRAIGHT = "straight"
	ANGLE = "angle"
	DEAD = "dead"
	CELL = "cell"


PalisadeCycle = tuple[int, int, int, int]

EMPTYCYCLE = [0, 0, 0, 0]
ONECYCLE = [1, 0, 0, 0]
STRAIGHTCYCLE = [1, 0, 1, 0]
ANGLECYCLE = [1, 1, 0, 0]
DEADCYCLE = [0, 1, 1, 1]
CELLCYCLE = [1, 1, 1, 1]

MAPCYCLE = {
	CycleType.EMPTY: EMPTYCYCLE,
	CycleType.ONE: ONECYCLE,
	CycleType.STRAIGHT: STRAIGHTCYCLE,
	CycleType.ANGLE: ANGLECYCLE,
	CycleType.DEAD: DEADCYCLE,
	CycleType.CELL: CELLCYCLE
}

ROTATEDMAPCYCLE = {
	CycleType.EMPTY: [EMPTYCYCLE, EMPTYCYCLE, EMPTYCYCLE, EMPTYCYCLE],
	CycleType.ONE: [ONECYCLE, [0, 1, 0, 0], [0, 0, 1, 0], [0, 0, 0, 1]],
	CycleType.STRAIGHT: [STRAIGHTCYCLE, [0, 1, 0, 1], STRAIGHTCYCLE, [0, 1, 0, 1]],
	CycleType.ANGLE: [ANGLECYCLE, [0, 1, 1, 0], [0, 0, 1, 1], [1, 0, 0, 1]],
	CycleType.DEAD: [DEADCYCLE, [1, 0, 1, 1], [1, 1, 0, 1], [1, 1, 1, 0]],
	CycleType.CELL: [CELLCYCLE, CELLCYCLE, CELLCYCLE, CELLCYCLE]
}

palisadeCellText = {
	CycleType.EMPTY: "E",
	CycleType.ONE: "1",
	CycleType.STRAIGHT: "S",
	CycleType.ANGLE: "A",
	CycleType.DEAD: "D",
	CycleType.CELL: "C"
}

class PalisadeSymbol(GridSymbol):
	def __init__(self, position, cycle: CycleType):
		super().__init__(position)
		self.cycle = cycle

	def propagate(self, state) -> bool:
		edges = state.cell_edges(self.position)
		vals = [state.edges[e] for e in edges]
		match self.cycle:
			case CycleType.EMPTY:
				return self.setRemainingEdges(state, edges)
			case CycleType.CELL:
				return self.setRemainingEdges(state, edges)
			case CycleType.ONE:
				# Si une arête est à 1 ou les 3 autres à 0, on peut forcer les autres à 0 ou 1
				if vals.count(EdgeState.PRESENT) > 0:
					offset = vals.index(EdgeState.PRESENT)
					return self.setRemainingEdges(state, edges, offset)
				if vals.count(EdgeState.ABSENT) == 3:
					offset = vals.index(EdgeState.UNKNOWN)
					return self.setRemainingEdges(state, edges, offset)
				if vals.count(EdgeState.ABSENT) == 4:
					return False
			case CycleType.STRAIGHT:
				# Si une arête est à 1 ou une arête à 0, on peut forcer les autres à 0 ou 1
				if vals.count(EdgeState.PRESENT) == 1:
					offset = vals.index(EdgeState.PRESENT)
					return self.setRemainingEdges(state, edges, offset)
				if vals.count(EdgeState.ABSENT) == 1:
					offset = vals.index(EdgeState.ABSENT) + 1
					return self.setRemainingEdges(state, edges, offset)
			case CycleType.DEAD:
				# Si une arête est à 0 ou les 3 autres à 1, on peut forcer les autres à 1 ou 0
				if vals.count(EdgeState.ABSENT) > 0:
					offset = vals.index(EdgeState.ABSENT)
					return self.setRemainingEdges(state, edges, offset)
				if vals.count(EdgeState.PRESENT) == 3:
					offset = vals.index(EdgeState.UNKNOWN)
					return self.setRemainingEdges(state, edges, offset)
				if vals.count(EdgeState.PRESENT) == 4:
					return False
			case CycleType.ANGLE:
				# Pour chaque arête fixée, on peut fixer l'arête opposée à la valeur opposée
				for i, v in enumerate(vals):
					if v is not EdgeState.UNKNOWN:
						toSet = EdgeState.PRESENT if v == EdgeState.ABSENT else EdgeState.ABSENT
						offset = i + 2
						if not state.set_edge(edges[offset % 4], toSet):
							return False
			case _:
				raise ValueError(f"Unknown cycle type: {self.cycle}")
		return True

	def setRemainingEdges(self, state, edges: list, offset=0, debug=0) -> bool:
		rotatedCycle = ROTATEDMAPCYCLE[self.cycle][offset % 4]
		if debug:
			print(rotatedCycle)
		for e, v in zip(edges, rotatedCycle):
			if v == 1:
				if not state.set_edge(e, EdgeState.PRESENT):
					return False
			else:
				if not state.set_edge(e, EdgeState.ABSENT):
					return False
		return True


class PalisadeConstraint(Constraint):
	def __init__(self, symbols: list[PalisadeSymbol]):
		self.symbols = symbols

	def propagate(self, state) -> bool:
		for symbol in self.symbols:
			if not symbol.propagate(state):
				return False
		return True

	def show(self, state, evenLines, oddLines) -> bool:
		for symbol in self.symbols:
			x, y = symbol.position
			oddLines[y] = oddLines[y][:2 * x + 1] + palisadeCellText[symbol.cycle] + oddLines[y][2 * x + 2:]


