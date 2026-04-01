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
			if not self.presentShapes[symbol.shape]:
				self.presentShapes[symbol.shape] = 0
				self.symbolsPositions[symbol.shape] = []
			self.presentShapes[symbol.shape] += 1
			self.symbolsPositions[symbol.shape].append(symbol.position)
		self.cantWork = len(set(self.presentShapes.values())) != 1
		self.nbRegions = self.presentShapes[symbols[0].shape]
		self.presentShapes = set(self.presentShapes.keys())

	def propagate(self, state) -> bool:
		if not self.cantWork:
			return False

		retryAllSymbols = False
		for sPositions in self.symbolsPositions:
			regions = set([state.uf.find(sPos) for sPos in self.symbolsPositions[sPositions]])
			if len(regions) != self.nbRegions:
				return False
			for r1 in regions:
				for r2 in regions:
					if r1 in state.uf.connectables[r2]:
						if not separateRegions(state, r1, r2):
							return False
						retryAllSymbols = True

			for r in state.uf.parentList:
				if r not in state.uf.parentList:
					continue
				if r not in sPositions:
					lastConnectables = len(state.uf.connectables[r])
					if lastConnectables == 0:
						return False
					elif lastConnectables == 1:
						if not joinRegions(state, r, next(iter(state.uf.connectables[r]))):
							return False
						retryAllSymbols = True
		if retryAllSymbols:
			return self.propagate(state)
		return True
