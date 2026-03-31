from edges import EdgeState
from constraints.base import Constraint


class LoopyConstraint(Constraint):
	def __init__(self):
		self.vertices = {}

	def set_vertices(self, vertices: dict):
		self.vertices = vertices

	def propagate(self, state) -> bool:
		for edges in self.vertices.values():
			vals = [state.edges[e] for e in edges]

			if vals.count(EdgeState.PRESENT) == 3:
				if len(edges) < 4:
					return False
				# forcer le reste à 1 (pour faire 4)
				for e in edges:
					if not state.set_edge(e, EdgeState.PRESENT):
						return False
		return True

