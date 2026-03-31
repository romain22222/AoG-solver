from constraints import MaximumConstraint
from constraints.size_separation import SizeSeparationConstraint
from solver import Grid

size_separation = {
	"constraints": [
		SizeSeparationConstraint(),
		MaximumConstraint(3)
	],
	"grid": Grid(4, 3),
	"holes": {}
}

