from constraints import Constraint
from regionHelper import regionSizeHelper, joinRegions
from solver import State


class SizeSeparationConstraint(Constraint):
	def __init__(self):
		super().__init__()

	def propagate(self, state: State) -> bool:
		entry=0
		for p in state.uf.parentList:
			targetRange = regionSizeHelper(state, p)
			if targetRange[0] != targetRange[1]:
				continue
			targetSize = targetRange[0]
			for q in state.uf.getAdjacent(p):
				if q not in state.uf.parentList:
					# Fused with another region
					continue
				if state.uf.size[q] == targetSize:
					connectables = state.uf.connectables[q]
					if len(connectables) == 0:
						return False
					if len(connectables) == 1:
						if not joinRegions(state, q, connectables.pop()):
							return False
		return True
