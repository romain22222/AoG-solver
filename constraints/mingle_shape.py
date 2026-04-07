from constraints import Constraint
from regionHelper import get_region_shapes, shapes_equal
from solver import checkOrDie


class MingleShapeConstraint(Constraint):
    def __init__(self):
        super().__init__()

    def propagate(self, state, solutionState, matchesSolutionState) -> bool:
        shapes = get_region_shapes(state)
        for region_id in state.uf.parentList:
            for adjacent in state.uf.getAdjacent(region_id, state.grid):
                if len(state.uf.connectables[region_id]) and len(state.uf.connectables[adjacent]) and shapes_equal(
                        shapes[region_id], shapes[adjacent]):
                    checkOrDie(state, solutionState, matchesSolutionState)
                    return False
        return True
