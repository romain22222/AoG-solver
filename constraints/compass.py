from typing import List

from constraints.base import GridSymbol, SymbolConstraint
from direction import Direction, OPPOSITE
from edges import EdgeState
from position import Position
from regionHelper import get_region_cells


def northCheck(compassP: Position, cellP: Position) -> bool:
	return compassP[1] > cellP[1]


def eastCheck(compassP: Position, cellP: Position) -> bool:
	return compassP[0] < cellP[0]


def southCheck(compassP: Position, cellP: Position) -> bool:
	return compassP[0] > cellP[0]


def westCheck(compassP: Position, cellP: Position) -> bool:
	return compassP[0] < cellP[0]


def deltaDir(compassP: Position, cellP: Position, direction: Direction) -> int:
	if direction == Direction.N:
		return compassP[1] - cellP[1]
	elif direction == Direction.E:
		return cellP[0] - compassP[0]
	elif direction == Direction.S:
		return cellP[1] - compassP[1]
	else:
		return compassP[0] - cellP[0]


def generalClosure(compassP: Position, validCells: List[Position], sameCoordsCells: List[Position], state,
				   direction: Direction) -> bool:
	opposite = OPPOSITE[direction]
	for cell in validCells:
		edges = state.cell_edges(cell)
		for edge in edges:
			if isinstance(edge[1], tuple):
				if not [cell, opposite] in edge:
					if state.edges[edge] != EdgeState.ABSENT:
						if not state.set_edge(edge, EdgeState.PRESENT):
							return False
				elif deltaDir(compassP, cell, direction) > 1:
					if not state.set_edge(edge, EdgeState.PRESENT):
						return False
	for cell in sameCoordsCells:
		edges = state.cell_edges(cell)
		toCheckEdge = [e for e in edges if [cell, direction] in e][0]
		if state.edges[toCheckEdge] != EdgeState.ABSENT:
			if not state.set_edge(toCheckEdge, EdgeState.PRESENT):
				return False
	return True


class CompassSymbol(GridSymbol):
	def __init__(self, position, north=None, south=None, east=None, west=None):
		super().__init__(position)
		self.directionAmounts = [north, east, south, west]
		self.text = "C"

	def propagate(self, state) -> bool:
		region_id = state.uf.find(self.position)
		nbConnectables = len(state.uf.connectables[region_id])
		cells = get_region_cells(state, region_id)
		x, y = self.position
		for comparisonCheck, sameCoordsCheck, amount, direction in zip(
				[northCheck, eastCheck, southCheck, westCheck],
				[lambda c: c[0] == x, lambda c: c[1] == y, lambda c: c[0] == x, lambda c: c[1] == y],
				self.directionAmounts,
				[Direction.N, Direction.E, Direction.S, Direction.W]
		):
			if amount is None:
				continue
			valid_cells = [c for c in cells if comparisonCheck(self.position, c)]
			count = len(valid_cells)
			if count == amount:
				generalClosure(self.position, valid_cells, [c for c in cells if sameCoordsCheck(c)], state, direction)
			elif count > amount:
				return False
		return True


class CompassConstraint(SymbolConstraint):
	def propagate(self, state) -> bool:
		for symbol in self.symbols:
			if not symbol.propagate(state):
				return False
		return True
