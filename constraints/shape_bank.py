from constraints import Constraint
from regionHelper import get_region_shape, joinRegions, shapes_equal, get_region_cells, get_region_shape_hard, \
    getTransforms


class ShapeBankConstraint(Constraint):
    def __init__(self, allowed_shapes: list):
        super().__init__()
        self.allowed_shapes = allowed_shapes
        self.allowed_sizes = [len(allowed_shape) for allowed_shape in self.allowed_shapes]

    def propagate(self, state) -> bool:
        for ra in state.uf.parentList:
            if ra not in state.uf.parentList:
                continue
            if state.uf.size[ra] > max(self.allowed_sizes):
                return False
            shape = get_region_shape(state, ra)
            check = self.checkShapeInShapes(shape)
            if len(state.uf.connectables[ra]) == 0:
                if not check:
                    return False
            else:
                if not self.can_extend_to_any_shape(shape):
                    return False
                if check:
                    continue
                if len(state.uf.connectables[ra]) == 1:
                    if not joinRegions(state, ra, next(iter(state.uf.connectables[ra]))):
                        return False
                    if not self.can_extend_to_any_shape(shape):
                        return False
        return True

    def checkShapeInShapes(self, shape) -> bool:
        for allowed_shape in self.allowed_shapes:
            if shapes_equal(shape, allowed_shape):
                return True
        return False

    def can_extend_to_any_shape(self, shape):
        current_size = len(shape)
        transforms = getTransforms(shape)
        for S in self.allowed_shapes:
            if len(S) == current_size:
                if shapes_equal(shape, S):
                    return True
            if len(S) < current_size:
                continue
            S_set = set(S)
            max_x_S = max((x for x, y in S), default=0)
            max_y_S = max((y for x, y in S), default=0)
            for trans in transforms:
                max_x_T = max(x for x, y in trans)
                max_y_T = max(y for x, y in trans)
                for dx in range(max_x_S - max_x_T + 1):
                    for dy in range(max_y_S - max_y_T + 1):
                        translated = set((x + dx, y + dy) for x, y in trans)
                        if translated <= S_set:
                            return True
        return False
