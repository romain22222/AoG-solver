from constraints import Constraint
from regionHelper import get_region_shapes, shapes_equal, regionSizeHelper


class ShapeBankConstraint(Constraint):
    def __init__(self, allowed_shapes: list):
        super().__init__()
        self.allowed_shapes = allowed_shapes
    
    def propagate(self, state) -> bool:
        shapes = get_region_shapes(state)
        for region_id, shape in shapes.items():
            size_range = regionSizeHelper(state, region_id)
            if size_range[0] == size_range[1]:
                if not any(shapes_equal(shape, allowed) for allowed in self.allowed_shapes):
                    return False
            else:
                allowed_sizes = [len(allowed_shape) for allowed_shape in self.allowed_shapes]
                if not any(size_range[0] <= size <= size_range[1] for size in allowed_sizes):
                    return False
        return True
