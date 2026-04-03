from direction import Direction
from edges import FullEdge, EdgeState
from position import Position


class Constraint:
	def propagate(self, state) -> bool:
		return True

	def set_vertices(self, vertices):
		pass

	def set_symbols(self, symbols):
		pass


class SymbolConstraint(Constraint):
	def __init__(self, symbols: list[Symbol]):
		super().__init__()
		self.symbols = symbols

	def show(self, state, evenLines, oddLines):
		for symbol in self.symbols:
			symbol.show(state, evenLines, oddLines)


class Symbol:
	def __init__(self):
		self.text = " "

	def propagate(self, state) -> bool:
		return True

	def show(self, state, evenLines, oddLines):
		pass


class GridSymbol(Symbol):
	def __init__(self, position: Position):
		super().__init__()
		self.position = position

	def show(self, state, evenLines, oddLines):
		x, y = self.position
		oddLines[y] = oddLines[y][:2 * x + 1] + self.text + oddLines[y][2 * x + 2:]


class EdgeSymbol(Symbol):
	def __init__(self, edge: FullEdge):
		super().__init__()
		self.edge = edge

	def propagate(self, state) -> bool:
		if not state.set_edge(self.edge, EdgeState.PRESENT):
			return False
		return True

	def show(self, state, evenLines, oddLines):
		if self.edge[0][1] in [Direction.N, Direction.S]:
			x, y = self.edge[0][0] if self.edge[0][1] == Direction.S else self.edge[1][0]
			evenLines[y] = evenLines[y][:2 * x + 1] + self.text + evenLines[y][2 * x + 2:]
		else:
			x, y = self.edge[0][0] if self.edge[0][1] == Direction.W else self.edge[1][0]
			oddLines[y] = oddLines[y][:2 * x] + self.text + oddLines[y][2 * x + 1:]


class VertexSymbol(Symbol):
	def __init__(self, position: Position):
		super().__init__()
		self.position = position

	def show(self, state, evenLines, oddLines):
		x, y = self.position
		evenLines[y] = evenLines[y][:2 * x] + self.text + evenLines[y][2 * x + 1:]
