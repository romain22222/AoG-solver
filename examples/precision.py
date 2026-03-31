from solver import Grid
from constraints.region import PrecisionConstraint

precision = {
	"constraints": [
		PrecisionConstraint(5)
	],
	"grid": Grid(6, 5),
	"holes": {(0, 0), (2, 1), (4, 2), (1, 3), (3, 4)}
}

