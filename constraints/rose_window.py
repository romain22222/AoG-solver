from enum import Enum
from typing import List

from constraints import GridSymbol
from constraints.base import SymbolConstraint
from regionHelper import separateRegions, joinRegions
from solver import checkOrDie


class RoseWindowShape(Enum):
	HEXAGON = 0
	CIRCLE = 1
	SQUARE = 2
	TRIANGLE = 3
	ROMBUS = 4

"""
ROSEWINDOWTEXT = {
	RoseWindowShape.HEXAGON: "⬡",
	RoseWindowShape.CIRCLE: "○",
	RoseWindowShape.SQUARE: "□",
	RoseWindowShape.TRIANGLE: "△",
	RoseWindowShape.ROMBUS: "◇",
}
"""

ROSEWINDOWTEXT = {
	RoseWindowShape.HEXAGON: "h",
	RoseWindowShape.CIRCLE: "c",
	RoseWindowShape.SQUARE: "s",
	RoseWindowShape.TRIANGLE: "t",
	RoseWindowShape.ROMBUS: "r",
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

	def propagate(self, state, solutionState, matchesSolutionState) -> bool:
		if not self.canWork:
			checkOrDie(state, solutionState, matchesSolutionState)
			return False

		if self.firstPropagate:
			for sKind in self.presentShapes:
				for i in range(self.nbRegions):
					for j in range(i+1,self.nbRegions):
						if not separateRegions(state, state.uf.find(self.symbolsPositions[sKind][i]), state.uf.find(self.symbolsPositions[sKind][j])):
							checkOrDie(state, solutionState, matchesSolutionState)
							return False
			self.firstPropagate = False

		changed = True
		while changed:
			changed = False
			region_counts = {r: {shape: 0 for shape in self.presentShapes} for r in state.uf.parentList}
			for shape in self.presentShapes:
				for pos in self.symbolsPositions[shape]:
					region = state.uf.find(pos)
					region_counts[region][shape] += 1

			for region, counts in region_counts.items():
				if len(state.uf.connectables[region]) == 0:
					if not all(count == 1 for count in counts.values()):
						checkOrDie(state, solutionState, matchesSolutionState)
						return False

			for sKind in self.presentShapes:
				tmpSP = [state.uf.find(p) for p in self.symbolsPositions[sKind]]
				for r in state.uf.parentList:
					r = state.uf.find(r)
					if r not in tmpSP:
						if len(state.uf.connectables[r]) == 0:
							checkOrDie(state, solutionState, matchesSolutionState)
							return False
						elif len(state.uf.connectables[r]) == 1:
							target = next(iter(state.uf.connectables[r]))
							if not joinRegions(state, r, target):
								checkOrDie(state, solutionState, matchesSolutionState)
								return False
							tmpSP = [state.uf.find(p) for p in tmpSP]
							changed = True
		return True
