from enum import Enum
from typing import List

from constraints import GridSymbol
from constraints.base import SymbolConstraint
from regionHelper import separateRegions, joinRegions


class RoseWindowShape(Enum):
	CIRCLE = 0
	SQUARE = 1
	ROMBUS = 2
	TRIANGLE = 3
	HEXAGON = 4


ROSEWINDOWTEXT = {
	RoseWindowShape.CIRCLE: "○",
	RoseWindowShape.SQUARE: "□",
	RoseWindowShape.ROMBUS: "◇",
	RoseWindowShape.TRIANGLE: "△",
	RoseWindowShape.HEXAGON: "⬡"
}


class RoseWindowSymbol(GridSymbol):
	def __init__(self, position, shape: RoseWindowShape):
		super().__init__(position)
		self.shape = shape
		self.text = ROSEWINDOWTEXT[shape]


class RoseWindowConstraint(SymbolConstraint):
	def __init__(self, symbols: List[RoseWindowSymbol]):
		super().__init__(symbols)
		self.presentShapes = {}
		self.symbolsPositions = {}
		for symbol in symbols:
			if symbol.shape not in self.presentShapes:
				self.presentShapes[symbol.shape] = 0
				self.symbolsPositions[symbol.shape] = []
			self.presentShapes[symbol.shape] += 1
			self.symbolsPositions[symbol.shape].append(symbol.position)
		self.canWork = len(set(self.presentShapes.values())) == 1
		self.nbRegions = self.presentShapes[symbols[0].shape]
		self.presentShapes = set(self.presentShapes.keys())
		self.firstPropagate = True

	def propagate(self, state) -> bool:
		if not self.canWork:
			return False

		if self.firstPropagate:
			for sKind in self.presentShapes:
				for i in range(self.nbRegions):
					for j in range(self.nbRegions):
						if not separateRegions(state, state.uf.find(self.symbolsPositions[sKind][i]), state.uf.find(self.symbolsPositions[sKind][j])):
							return False
			self.firstPropagate = False

		retryAllSymbols = False
		for sKind in self.presentShapes:
			self.symbolsPositions[sKind] = [state.uf.find(p) for p in self.symbolsPositions[sKind]]
			for r in state.uf.parentList:
				r = state.uf.find(r)
				if r not in self.symbolsPositions[sKind]:
					lastConnectables = len(state.uf.connectables[r])
					if lastConnectables == 0:
						return False
					elif lastConnectables == 1:
						if not joinRegions(state, r, next(iter(state.uf.connectables[r]))):
							return False
						self.symbolsPositions[sKind] = [state.uf.find(p) for p in self.symbolsPositions[sKind]]
						retryAllSymbols = True
		if retryAllSymbols:
			return self.propagate(state)
		return True
