from constraints import Constraint
from regionHelper import get_region_cells, get_region_shape_hard, shapes_equal, regionSizeHelper
from solver import checkOrDie


class MatchConstraint(Constraint):
    def __init__(self):
        super().__init__()
        self.allowed_sizes = []

    def propagate(self, state, solutionState, matchesSolutionState) -> bool:
        if len(self.allowed_sizes) == 0:
            amCells = len(state.grid.cells)
            for i in range(amCells):
                if amCells % (i + 1) == 0:
                    self.allowed_sizes.append(i + 1)
        for region_id in state.uf.parentList:
            cells = get_region_cells(state, region_id)
            if len(state.uf.connectables[region_id]) == 0:
                reference_shape = get_region_shape_hard(cells)
                if len(reference_shape) not in self.allowed_sizes:
                    checkOrDie(state, solutionState, matchesSolutionState)
                    return False
                break
        else:
            return True

        for region_id in state.uf.parentList:
            cells = get_region_cells(state, region_id)
            actual_shape = get_region_shape_hard(cells)
            
            size_range = regionSizeHelper(state, region_id)
            if len(state.uf.connectables[region_id]) == 0:
                if not shapes_equal(actual_shape, reference_shape):
                    checkOrDie(state, solutionState, matchesSolutionState)
                    return False
            else:
                if size_range[1] < len(reference_shape):
                    checkOrDie(state, solutionState, matchesSolutionState)
                    return False
                if size_range[0] > len(reference_shape):
                    checkOrDie(state, solutionState, matchesSolutionState)
                    return False
        
        return True
