from constraints import Constraint
from regionHelper import get_region_shape, joinRegions, shapes_equal, getTransforms, closeRegion


def makeRegionMatch(state, ra, targetShape):
    # initial check to see if it already matches
    shape = get_region_shape(state, ra)
    if shapes_equal(shape, targetShape):
        if not closeRegion(state, ra, False):
            return False
        return True

    successful_states = []
    successful_connected = []
    stack = [(state.clone(), ra, None, [])]
    shape_size = len(targetShape)

    while stack:
        test_state, region_id, region_to_merge, connected = stack.pop()
        if region_to_merge:
            if not joinRegions(test_state, ra, region_to_merge):
                continue
            region_id = test_state.uf.find(region_id)
            shape = get_region_shape(test_state, region_id)
            transforms = getTransforms(shape)
            size = test_state.uf.size[region_id]
            if not can_extend_to_shape(shape, targetShape, transforms, size):
                continue
            connected.append(region_to_merge)
        current_size = test_state.uf.size[region_id]
        if current_size == shape_size:
            # Check before adding in successful_states if one of the previous connected in the successfuls matches
            sconn = tuple(sorted(connected))
            if sconn in successful_connected:
                continue
            successful_states.append(test_state)
            successful_connected.append(sconn)
            if len(successful_states) > 1:
                return True
            continue
        for r in test_state.uf.connectables[region_id]:
            if r in connected:
                continue
            if test_state.uf.size[r] > shape_size - current_size:
                continue
            stack.append((test_state.clone(), region_id, r, connected.copy()))
    if len(successful_states) == 1:
        if not closeRegion(successful_states[0], successful_states[0].uf.find(ra), False):
            return False
        state.set(successful_states[0])
        return True
    return False


def can_extend_to_shape(shape, targetShape, transforms, size):
    if len(targetShape) == size:
        if shapes_equal(shape, targetShape):
            return True
    if len(targetShape) < size:
        return False
    tset = set(targetShape)
    max_x_S = max((x for x, y in targetShape), default=0)
    max_y_S = max((y for x, y in targetShape), default=0)
    for trans in transforms:
        max_x_T = max(x for x, y in trans)
        max_y_T = max(y for x, y in trans)
        for dx in range(max_x_S - max_x_T + 1):
            for dy in range(max_y_S - max_y_T + 1):
                if len(set((x + dx, y + dy) for x, y in trans).intersection(tset)) == size:
                    return True
    return False


class ShapeBankConstraint(Constraint):
    def __init__(self, allowed_shapes: list):
        super().__init__()
        self.allowed_shapes = allowed_shapes
        self.allowed_sizes = [len(allowed_shape) for allowed_shape in self.allowed_shapes]

    def propagate(self, state) -> bool:
        for ra in state.uf.parentList:
            ra = state.uf.find(ra)
            if state.uf.size[ra] > max(self.allowed_sizes):
                return False
            shape = get_region_shape(state, ra)
            check = self.checkShapeInShapes(shape)
            if len(state.uf.connectables[ra]) == 0:
                if not check:
                    return False
            else:
                possibles = self.extendables(shape)
                if len(possibles) == 0:
                    return False
                if len(possibles) == 1:
                    if not makeRegionMatch(state, ra, possibles[0]):
                        return False
                else:
                    if check:
                        continue
                    if len(state.uf.connectables[ra]) == 1:
                        if not joinRegions(state, ra, next(iter(state.uf.connectables[ra]))):
                            return False
                        return self.propagate(state)
        return True

    def checkShapeInShapes(self, shape) -> bool:
        for allowed_shape in self.allowed_shapes:
            if shapes_equal(shape, allowed_shape):
                return True
        return False

    def extendables(self, shape):
        current_size = len(shape)
        transforms = set(getTransforms(shape))
        possibles = []
        for S in self.allowed_shapes:
            if can_extend_to_shape(shape, S, transforms, current_size):
                possibles.append(S)
        return possibles

    def check(self, state) -> bool:
        for ra in state.uf.parentList:
            shape = get_region_shape(state, ra)
            if not self.checkShapeInShapes(shape):
                return False
        return True
