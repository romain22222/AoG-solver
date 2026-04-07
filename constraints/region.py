from constraints.base import Constraint
from regionHelper import regionSizeHelper, closeRegion
from solver import checkOrDie


class PrecisionConstraint(Constraint):
	def __init__(self, size: int):
		self.size = size

	def propagate(self, state, solutionState, matchesSolutionState) -> bool:
		for p in state.uf.parentList:
			minR, maxR = regionSizeHelper(state, p)
			if minR > self.size or maxR < self.size:
				checkOrDie(state, solutionState, matchesSolutionState)
				return False
			if maxR == self.size or minR == self.size:
				if not closeRegion(state, p, maxR == self.size):
					checkOrDie(state, solutionState, matchesSolutionState)
					return False
		return True


class MinimumConstraint(Constraint):
	def __init__(self, size: int):
		self.size = size

	def propagate(self, state, solutionState, matchesSolutionState) -> bool:
		for p in state.uf.parentList:
			minR, maxR = regionSizeHelper(state, p)
			if maxR < self.size:
				checkOrDie(state, solutionState, matchesSolutionState)
				return False
			if maxR == self.size:
				if not closeRegion(state, p, True):
					checkOrDie(state, solutionState, matchesSolutionState)
					return False
		return True


class MaximumConstraint(Constraint):
	def __init__(self, size: int):
		self.size = size

	def propagate(self, state, solutionState, matchesSolutionState) -> bool:
		for p in state.uf.parentList:
			minR = state.uf.size[state.uf.find(p)]
			if minR > self.size:
				checkOrDie(state, solutionState, matchesSolutionState)
				return False
			if minR == self.size:
				if not closeRegion(state, p, False):
					checkOrDie(state, solutionState, matchesSolutionState)
					return False
		return True
