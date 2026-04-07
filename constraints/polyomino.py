from constraints.base import GridSymbol, SymbolConstraint
from regionHelper import get_region_cells, get_region_shape_hard, shapes_equal, regionSizeHelper, closeRegion
from solver import checkOrDie


class PolyominoSymbol(GridSymbol):
	def __init__(self, position, shape):
		super().__init__(position)
		self.shape = shape
		self.text = "P"

	def propagate(self, state, solutionState, matchesSolutionState) -> bool:
		region_id = state.uf.find(self.position)
		cells = get_region_cells(state, region_id)
		size_range = regionSizeHelper(state, region_id)
		min_size, max_size = size_range

		if len(state.uf.connectables[region_id]) == 0:
			actual_shape = get_region_shape_hard(cells)
			res = shapes_equal(actual_shape, self.shape)
			if not res:
				checkOrDie(state, solutionState, matchesSolutionState)
			return res
		else:
			required_size = len(self.shape)
			if max_size < required_size:
				checkOrDie(state, solutionState, matchesSolutionState)
				return False
			if min_size > required_size:
				checkOrDie(state, solutionState, matchesSolutionState)
				return False
			elif min_size == required_size:
				if not closeRegion(state, region_id):
					checkOrDie(state, solutionState, matchesSolutionState)
					return False
				actual_shape = get_region_shape_hard(cells)
				res = shapes_equal(actual_shape, self.shape)
				if not res:
					checkOrDie(state, solutionState, matchesSolutionState)
				return res
			return True


class PolyominoConstraint(SymbolConstraint):
	def propagate(self, state, solutionState, matchesSolutionState) -> bool:
		for symbol in self.symbols:
			if not symbol.propagate(state, solutionState, matchesSolutionState):
				return False
		return True
