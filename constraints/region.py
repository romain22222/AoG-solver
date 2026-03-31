from constraints.base import Constraint
from regionHelper import regionSizeHelper, closeRegion


class PrecisionConstraint(Constraint):
	def __init__(self, size: int):
		self.size = size

	def propagate(self, state) -> bool:
		uf = state.uf
		for p in uf.parentList:
			minR, maxR = regionSizeHelper(state, p)
			if minR > self.size or maxR < self.size:
				return False
			if maxR == self.size or minR == self.size:
				if not closeRegion(state, p, maxR == self.size):
					return False
		return True


class MinimumConstraint(Constraint):
	def __init__(self, size: int):
		self.size = size

	def propagate(self, state) -> bool:
		uf = state.uf
		for p in uf.parentList:
			minR, maxR = regionSizeHelper(state, p)
			if maxR < self.size:
				return False
			if maxR == self.size:
				if not closeRegion(state, p, True):
					return False
		return True


class MaximumConstraint(Constraint):
	def __init__(self, size: int):
		self.size = size

	def propagate(self, state) -> bool:
		uf = state.uf
		for p in uf.parentList:
			minR = uf.size[uf.find(p)]
			if minR > self.size:
				return False
			if minR == self.size:
				if not closeRegion(state, p, False):
					return False
		return True
