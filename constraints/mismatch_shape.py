from constraints import Constraint
from regionHelper import get_region_shapes, shapes_equal
from solver import checkOrDie


class MismatchShapeConstraint(Constraint):
	def __init__(self):
		super().__init__()

	def propagate(self, state, solutionState, matchesSolutionState) -> bool:
		shapes = get_region_shapes(state)
		for i, shape1 in enumerate(shapes):
			for j, shape2 in enumerate(shapes):
				if i != j and shapes_equal(shape1, shape2):
					checkOrDie(state, solutionState, matchesSolutionState)
					return False

		return True
