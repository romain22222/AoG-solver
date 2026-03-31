from solver import State, Solver, get_vertices
from examples import puzzleList

if __name__ == "__main__":
	# You can change this to any puzzle name from the puzzleList dictionary
	puzzle_name = "watchtower"
	puzzle = puzzleList[puzzle_name]
	
	testedGrid = puzzle["grid"]
	testedGrid.setHoles(puzzle["holes"])
	testedVertices = get_vertices(puzzle["grid"])
	testedConstraints = puzzle["constraints"]

	for constraint in testedConstraints:
		hasattr(constraint, "vertices") and constraint.set_vertices(testedVertices)

	testedGrid.setConstraints(testedConstraints)

	solver = Solver(testedGrid, testedConstraints)
	initialState = State(testedGrid)

	solver.solve(initialState)

	print("Nombre de solutions trouvées :", len(solver.solutions))
	for solutionNumber, solution in enumerate(solver.solutions):
		print(f"Solution {solutionNumber + 1}:")
		solution.show(testedConstraints, puzzle["holes"])
		print("---")

