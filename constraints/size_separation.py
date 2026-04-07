from constraints import Constraint
from regionHelper import regionSizeHelper, joinRegions
from solver import State, checkOrDie


class SizeSeparationConstraint(Constraint):
	def __init__(self):
		super().__init__()

	def propagate(self, state, solutionState, matchesSolutionState) -> bool:
		for p in state.uf.parentList:
			targetRange = regionSizeHelper(state, p)
			if targetRange[0] != targetRange[1]:
				continue
			targetSize = targetRange[0]
			for q in state.uf.getAdjacent(p, state.grid):
				if q not in state.uf.parentList:
					continue
				if state.uf.size[q] == targetSize:
					connectables = state.uf.connectables[q]
					if len(connectables) == 0:
						checkOrDie(state, solutionState, matchesSolutionState)
						return False
					if len(connectables) == 1:
						if not joinRegions(state, q, connectables.pop()):
							checkOrDie(state, solutionState, matchesSolutionState)
							return False
		return True
