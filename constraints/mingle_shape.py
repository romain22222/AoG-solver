from constraints import Constraint
from regionHelper import get_region_shapes, shapes_equal, regionSizeHelper


class MingleShapeConstraint(Constraint):
    def __init__(self):
        super().__init__()
    
    def propagate(self, state) -> bool:
        shapes = get_region_shapes(state)
        
        for region_id in state.uf.parentList:
            region_shape = shapes[region_id]
            
            for adjacent in state.uf.getAdjacent(region_id):
                adjacent_shape = shapes[adjacent]
                
                range1 = regionSizeHelper(state, region_id)
                closed1 = range1[0] == range1[1]

                range2 = regionSizeHelper(state, adjacent)
                closed2 = range2[0] == range2[1]
                
                if closed1 and closed2 and shapes_equal(region_shape, adjacent_shape):
                    return False
        
        return True
