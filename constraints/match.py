from constraints import Constraint
from regionHelper import get_region_cells, get_region_shape, shapes_equal, regionSizeHelper


class MatchConstraint(Constraint):
    def __init__(self):
        super().__init__()
        self.reference_shape = None
    
    def propagate(self, state) -> bool:
        if self.reference_shape is None:
            for region_id in state.uf.parentList:
                cells = get_region_cells(state, region_id)
                size_range = regionSizeHelper(state, region_id)
                if size_range[0] == size_range[1]:
                    self.reference_shape = get_region_shape(cells)
                    break
            else:
                return True
        
        for region_id in state.uf.parentList:
            cells = get_region_cells(state, region_id)
            actual_shape = get_region_shape(cells)
            
            size_range = regionSizeHelper(state, region_id)
            if size_range[0] == size_range[1]:
                if not shapes_equal(actual_shape, self.reference_shape):
                    return False
            else:
                if size_range[1] < len(self.reference_shape):
                    return False
                if size_range[0] > len(self.reference_shape):
                    return False
        
        return True
