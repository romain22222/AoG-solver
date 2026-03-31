from constraints import Constraint
from regionHelper import get_region_shapes, shapes_equal, regionSizeHelper


class MingleShapeConstraint(Constraint):
    def __init__(self):
        super().__init__()
    
    def propagate(self, state) -> bool:
        shapes = get_region_shapes(state)
        for region_id in state.uf.parentList:
            for adjacent in state.uf.getAdjacent(region_id):
                if len(state.uf.connectables[region_id]) and len(state.uf.connectables[adjacent]) and shapes_equal(
                        shapes[region_id], shapes[adjacent]):
                    return False
        return True
