from constraints import Constraint
from regionHelper import get_region_cells, is_rectangle
from solver import checkOrDie


class BoxyConstraint(Constraint):
    def __init__(self):
        super().__init__()

    def propagate(self, state, solutionState, matchesSolutionState) -> bool:
        for region_id in state.uf.parentList:
            cells = get_region_cells(state, region_id)
            if is_rectangle(cells):
                continue
            
            min_x = min(x for x, y in cells)
            max_x = max(x for x, y in cells)
            min_y = min(y for x, y in cells)
            max_y = max(y for x, y in cells)

            missing_cells = []
            for x in range(min_x, max_x + 1):
                for y in range(min_y, max_y + 1):
                    if (x, y) not in cells:
                        missing_cells.append((x, y))
            
            if not missing_cells:
                checkOrDie(state, solutionState, matchesSolutionState)
                return False
            
            for m in missing_cells:
                if not state.uf.union(region_id, m):
                    checkOrDie(state, solutionState, matchesSolutionState)
                    return False
            else:
                res = self.propagate(state)
                if not res:
                    checkOrDie(state, solutionState, matchesSolutionState)
                return res
        return True
