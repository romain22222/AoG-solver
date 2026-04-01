from constraints import Constraint
from regionHelper import get_region_cells, get_region_shape, shapes_equal, regionSizeHelper


class MatchConstraint(Constraint):
    def __init__(self):
        super().__init__()
        self.reference_shape = None
        self.allowed_sizes = []
    
    def propagate(self, state) -> bool:
        if len(self.allowed_sizes) == 0:
            amCells = len(state.grid.cells)
            for i in range(amCells):
                if amCells % (i + 1) == 0:
                    self.allowed_sizes.append(i + 1)
        if self.reference_shape is None:
            for region_id in state.uf.parentList:
                cells = get_region_cells(state, region_id)
                if len(state.uf.connectables[region_id]) == 0:
                    self.reference_shape = get_region_shape(cells)
                    if len(self.reference_shape) not in self.allowed_sizes:
                        return False
                    break
            else:
                return True
        
        for region_id in state.uf.parentList:
            cells = get_region_cells(state, region_id)
            actual_shape = get_region_shape(cells)
            
            size_range = regionSizeHelper(state, region_id)
            if len(state.uf.connectables[region_id]) == 0:
                if not shapes_equal(actual_shape, self.reference_shape):
                    return False
            else:
                if size_range[1] < len(self.reference_shape):
                    return False
                if size_range[0] > len(self.reference_shape):
                    return False
        
        return True
