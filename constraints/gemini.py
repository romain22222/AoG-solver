from constraints import EdgeSymbol
from constraints.base import SymbolConstraint
from edges import FullEdge
from regionHelper import get_region_shape, closeRegion


class GeminiSymbol(EdgeSymbol):
	def __init__(self, edge: FullEdge):
		super().__init__(edge)
		self.text = "γ"

	def propagate(self, state) -> bool:
		if not super().propagate(state):
			return False
		r1, r2 = state.uf.find(self.edge[0][0]), state.uf.find(self.edge[1][0])
		r1Closed, r2Closed = len(state.uf.connectables[r1]) == 0, len(state.uf.connectables[r2]) == 0
		r1Shape, r2Shape = get_region_shape(state, r1), get_region_shape(state, r2)
		if not r1Closed and not r2Closed:
			return True
		if r1Shape == r2Shape:
			return closeRegion(state, r2) and closeRegion(state, r1)
		if r1Closed and state.uf.size[r1] <= state.uf.size[r2]:
			return False
		if r2Closed and state.uf.size[r2] <= state.uf.size[r1]:
			return False
		return True


class GeminiConstraint(SymbolConstraint):
	def propagate(self, state) -> bool:
		for s in self.symbols:
			if not s.propagate(state):
				return False
		return True
