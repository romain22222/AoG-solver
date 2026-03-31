from typing import List

from constraints import Symbol, Constraint
from position import Position
from regionHelper import separateRegions, joinRegions
from solver import State


class WatchtowerSymbol(Symbol):
	def __init__(self, position: Position, count: int) -> None:
		super().__init__()
		self.count = count
		self.position = position

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


class WatchtowerConstraint(Constraint):
	def __init__(self, symbols: list[WatchtowerSymbol]) -> None:
		super().__init__()
		self.symbols = symbols

	def propagate(self, state: State) -> bool:
		for symbol in self.symbols:
			if not symbol.propagate(state):
				return False
		return True

	def show(self, state: State, evenLines: List[str], oddLines: List[str]) -> None:
		for symbol in self.symbols:
			x, y = symbol.position
			evenLines[y] = evenLines[y][:2 * x] + str(symbol.count) + evenLines[y][2 * x + 1:]
