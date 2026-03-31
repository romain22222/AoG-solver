from constraints.base import Constraint, GridSymbol
from regionHelper import get_region_cells, get_region_shape, shapes_equal, regionSizeHelper, closeRegion


class PolyominoSymbol(GridSymbol):
    def __init__(self, position, shape):
        super().__init__(position)
        self.shape = shape
    
    def propagate(self, state) -> bool:
        region_id = state.uf.find(self.position)
        cells = get_region_cells(state, region_id)
        size_range = regionSizeHelper(state, region_id)
        min_size, max_size = size_range
        
        if len(state.uf.connectables[region_id]) == 0:
            actual_shape = get_region_shape(cells)
            return shapes_equal(actual_shape, self.shape)
        else:
            required_size = len(self.shape)
            if max_size < required_size:
                return False
            if min_size > required_size:
                return False
            elif min_size == required_size:
                if not closeRegion(state, region_id):
                    return False
                actual_shape = get_region_shape(cells)
                return shapes_equal(actual_shape, self.shape)
            return True


class PolyominoConstraint(Constraint):
    def __init__(self, symbols: list[PolyominoSymbol]):
        self.symbols = symbols
    
    def propagate(self, state) -> bool:
        for symbol in self.symbols:
            if not symbol.propagate(state):
                return False
        return True
