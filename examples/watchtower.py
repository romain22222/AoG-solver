from constraints.watchtower import WatchtowerConstraint, WatchtowerSymbol
from solver import Grid

watchtower = {
	"constraints": [
		WatchtowerConstraint(
			[
				WatchtowerSymbol((1, 0), 2),
				WatchtowerSymbol((3, 0), 1),
				WatchtowerSymbol((5, 0), 2),
				WatchtowerSymbol((0, 1), 2),
				WatchtowerSymbol((2, 1), 4),
				WatchtowerSymbol((4, 1), 2),
				WatchtowerSymbol((1, 2), 2),
				WatchtowerSymbol((3, 2), 1),
				WatchtowerSymbol((5, 2), 2),
				WatchtowerSymbol((0, 3), 2),
				WatchtowerSymbol((2, 3), 2),
				WatchtowerSymbol((4, 3), 3),
				WatchtowerSymbol((1, 4), 1),
				WatchtowerSymbol((3, 4), 2),
				WatchtowerSymbol((5, 4), 2),
				WatchtowerSymbol((2, 4), 1),
				WatchtowerSymbol((4, 4), 1),
				WatchtowerSymbol((1, 1), 3),
				WatchtowerSymbol((1, 3), 3),
				WatchtowerSymbol((2, 2), 3),
				WatchtowerSymbol((6, 4), 1),
				WatchtowerSymbol((5, 3), 2),
				WatchtowerSymbol((6, 1), 1),
				WatchtowerSymbol((5, 1), 3),
			]
		)
	],
	"grid": Grid(6, 5),
	"holes": {(3, 4)}
}

