from constraints.base import SymbolConstraint, VertexSymbol
from position import Position
from regionHelper import separateRegions, joinRegions
from solver import State


class WatchtowerSymbol(VertexSymbol):
	def __init__(self, position: Position, count: str) -> None:
		super().__init__(position)
		self.count = int(count)
		self.text = count

	def propagate(self, state) -> bool:
		# 1- get cells around vertex
		# 2- Check their parents
		# 3- If nb(parents) < self.count -> False, if nb(parents) == self.count, disjoint every pair of parents
		cells = state.cellsAroundVertex(self.position)
		parents = [state.uf.find(cell) for cell in cells]
		if self.count == 1:
			for p in parents[1:]:
				if not joinRegions(state, parents[0], p):
					return False
			return True
		unique_parents = set(parents)
		current = len(unique_parents)
		if current < self.count:
			return False
		elif current == self.count:
			for i in range(len(parents)):
				for j in range(i + 1, len(parents)):
					if parents[i] != parents[j]:
						if not separateRegions(state, parents[i], parents[j]):
							return False
		else:
			upList = list(unique_parents)
			pairs = []
			for i in range(len(upList)):
				for j in range(i + 1, len(upList)):
					if state.uf.canJoin(upList[i], upList[j]):
						pairs += [(upList[i], upList[j])]
			if current - len(pairs) > self.count:
				return False
			elif current - len(pairs) == self.count:
				for p in pairs:
					if not joinRegions(state, p[0], p[1]):
						return False
		return True


class WatchtowerConstraint(SymbolConstraint):
	def propagate(self, state: State) -> bool:
		for symbol in self.symbols:
			if not symbol.propagate(state):
				return False
		return True
