from constraints import Constraint
from regionHelper import get_region_cells, is_rectangle
from solver import checkOrDie


class NonBoxyConstraint(Constraint):
    def __init__(self):
        super().__init__()

    def propagate(self, state, solutionState, matchesSolutionState) -> bool:
        for region_id in state.uf.parentList:
            if len(state.uf.connectables[region_id]) != 0:
                continue
            cells = get_region_cells(state, region_id)
            if is_rectangle(cells):
                checkOrDie(state, solutionState, matchesSolutionState)
                return False
        return True
