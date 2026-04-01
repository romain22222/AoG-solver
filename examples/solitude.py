from constraints import SolitudeConstraint, PalisadeConstraint, PalisadeSymbol, CycleType
from solver import Grid

solitude = {
	"grid": Grid(6, 5),
	"constraints": [
		SolitudeConstraint(),
		PalisadeConstraint([
			PalisadeSymbol((1, 1), CycleType.EMPTY),
			PalisadeSymbol((3, 3), CycleType.EMPTY),
			PalisadeSymbol((4, 3), CycleType.STRAIGHT),
		])
	],
	"holes": {(2, 2)}
}
