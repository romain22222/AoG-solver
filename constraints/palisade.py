from enum import Enum

from constraints.base import GridSymbol, SymbolConstraint
from edges import EdgeState
from solver import checkOrDie


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
		self.text = palisadeCellText[cycle]

	def propagate(self, state, solutionState, matchesSolutionState) -> bool:
		edges = state.cell_edges(self.position)
		vals = [state.edges[e] for e in edges]
		match self.cycle:
			case CycleType.EMPTY:
				res = self.setRemainingEdges(state, edges)
				if not res:
					checkOrDie(state, solutionState, matchesSolutionState)
				return res
			case CycleType.CELL:
				res = self.setRemainingEdges(state, edges)
				if not res:
					checkOrDie(state, solutionState, matchesSolutionState)
				return res
			case CycleType.ONE:
				# Si une arête est à 1 ou les 3 autres à 0, on peut forcer les autres à 0 ou 1
				if vals.count(EdgeState.PRESENT) > 0:
					offset = vals.index(EdgeState.PRESENT)
					res = self.setRemainingEdges(state, edges, offset)
					if not res:
						checkOrDie(state, solutionState, matchesSolutionState)
					return res
				if vals.count(EdgeState.ABSENT) == 3:
					offset = vals.index(EdgeState.UNKNOWN)
					res = self.setRemainingEdges(state, edges, offset)
					if not res:
						checkOrDie(state, solutionState, matchesSolutionState)
					return res
				if vals.count(EdgeState.ABSENT) == 4:
					checkOrDie(state, solutionState, matchesSolutionState)
					return False
			case CycleType.STRAIGHT:
				# Si une arête est à 1 ou une arête à 0, on peut forcer les autres à 0 ou 1
				if vals.count(EdgeState.PRESENT) == 1:
					offset = vals.index(EdgeState.PRESENT)
					res = self.setRemainingEdges(state, edges, offset)
					if not res:
						checkOrDie(state, solutionState, matchesSolutionState)
					return res
				if vals.count(EdgeState.ABSENT) == 1:
					offset = vals.index(EdgeState.ABSENT) + 1
					res = self.setRemainingEdges(state, edges, offset)
					if not res:
						checkOrDie(state, solutionState, matchesSolutionState)
					return res
			case CycleType.DEAD:
				# Si une arête est à 0 ou les 3 autres à 1, on peut forcer les autres à 1 ou 0
				if vals.count(EdgeState.ABSENT) > 0:
					offset = vals.index(EdgeState.ABSENT)
					res = self.setRemainingEdges(state, edges, offset)
					if not res:
						checkOrDie(state, solutionState, matchesSolutionState)
					return res
				if vals.count(EdgeState.PRESENT) == 3:
					offset = vals.index(EdgeState.UNKNOWN)
					res = self.setRemainingEdges(state, edges, offset)
					if not res:
						checkOrDie(state, solutionState, matchesSolutionState)
					return res
				if vals.count(EdgeState.PRESENT) == 4:
					checkOrDie(state, solutionState, matchesSolutionState)
					return False
			case CycleType.ANGLE:
				# Pour chaque arête fixée, on peut fixer l'arête opposée à la valeur opposée
				for i, v in enumerate(vals):
					if v is not EdgeState.UNKNOWN:
						toSet = EdgeState.PRESENT if v == EdgeState.ABSENT else EdgeState.ABSENT
						offset = i + 2
						if not state.set_edge(edges[offset % 4], toSet):
							checkOrDie(state, solutionState, matchesSolutionState)
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


class PalisadeConstraint(SymbolConstraint):
	def propagate(self, state, solutionState, matchesSolutionState) -> bool:
		for symbol in self.symbols:
			if not symbol.propagate(state, solutionState, matchesSolutionState):
				return False
		return True
