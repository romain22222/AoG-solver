from solver import Grid
from constraints.palisade import PalisadeConstraint, PalisadeSymbol, CycleType
from constraints.bricky import BrickyConstraint

palisade = {
	"constraints": [
		PalisadeConstraint([
			PalisadeSymbol((2, 0), CycleType.STRAIGHT),
			PalisadeSymbol((3, 1), CycleType.ANGLE),
			PalisadeSymbol((4, 0), CycleType.ANGLE),
			PalisadeSymbol((1, 2), CycleType.ONE),
			PalisadeSymbol((4, 2), CycleType.CELL),
			PalisadeSymbol((0, 1), CycleType.CELL),
			PalisadeSymbol((0, 3), CycleType.DEAD),
			PalisadeSymbol((1, 3), CycleType.STRAIGHT),
			PalisadeSymbol((3, 3), CycleType.EMPTY),
			PalisadeSymbol((4, 4), CycleType.ANGLE),
			PalisadeSymbol((1, 4), CycleType.ANGLE),
		]),
		BrickyConstraint()
	],
	"grid": Grid(5, 5),
	"holes": {(0, 0), (2, 2)}
}

