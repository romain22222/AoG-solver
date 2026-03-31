from constraints import Constraint
from regionHelper import get_region_shapes, shapes_equal, regionSizeHelper


class MismatchShapeConstraint(Constraint):
    def __init__(self):
        super().__init__()
    
    def propagate(self, state) -> bool:
        shapes = get_region_shapes(state)
        shape_list = []

        for region_id, shape in shapes.items():
            size_range = regionSizeHelper(state, region_id)
            if size_range[0] == size_range[1]:
                shape_list.append(shape)

        for i, shape1 in enumerate(shape_list):
            for j, shape2 in enumerate(shape_list):
                if i != j and shapes_equal(shape1, shape2):
                    return False
        
        return True
