from constraints import EdgeSymbol
from constraints.base import SymbolConstraint
from edges import FullEdge
from regionHelper import get_region_shape, closeRegion


class DifferenceSymbol(EdgeSymbol):
	def __init__(self, edge: FullEdge, count: int):
		super().__init__(edge)
		self.count = count
		self.text = count

	def propagate(self, state) -> bool:
		if not super().propagate(state):
			return False
		r1, r2 = state.uf.find(self.edge[0][0]), state.uf.find(self.edge[1][0])
		r1Closed, r2Closed = len(state.uf.connectables[r1]) == 0, len(state.uf.connectables[r2]) == 0
		r1Size, r2Size = state.uf.size[r1], state.uf.size[r2]
		if r1Closed and r2Closed:
			return abs(r1Size - r2Size) == self.count
		return True


class DifferenceConstraint(SymbolConstraint):
	def propagate(self, state) -> bool:
		for s in self.symbols:
			if not s.propagate(state):
				return False
		return True
