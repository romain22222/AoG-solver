from constraints.base import Constraint
from edges import EdgeState
from solver import checkOrDie


class BrickyConstraint(Constraint):
	def __init__(self):
		self.vertices = {}

	def set_vertices(self, vertices: dict):
		self.vertices = vertices

	def propagate(self, state, solutionState, matchesSolutionState) -> bool:
		for edges in self.vertices.values():
			vals = [state.edges[e] for e in edges]
			if vals.count(EdgeState.PRESENT) == 4:
				checkOrDie(state, solutionState, matchesSolutionState)
				return False
		return True

