from converter import readJson, translatePuzzle, Puzzle
from edges import EdgeState
from solver import State, Solver, get_vertices
from examples import puzzleList


def initPuzzle(p: Puzzle) -> tuple[Puzzle, State]:
	testedGrid = p["grid"]
	testedGrid.setHoles(p["holes"])
	testedVertices = get_vertices(p["grid"])
	testedConstraints = p["constraints"]

	for constraint in testedConstraints:
		hasattr(constraint, "vertices") and constraint.set_vertices(testedVertices)

	for constraint in testedConstraints:
		hasattr(constraint, "all_symbols") and constraint.set_symbols(testedVertices)

	state = State(testedGrid)
	for e in p["forcedEdges"]:
		if not state.set_edge(e, EdgeState.PRESENT):
			raise Exception("Invalid forced edge: " + str(e))

	testedGrid.setConstraints(testedConstraints)
	return p, state


if __name__ == "__main__":
	mode = "puzzleExtract"
	jsonPath = "./path/to/archive.json"
	pidStart = "PUZZLE_ID"
	if mode == "exampleRun":
		puzzle_name = "solitude"
		puzzle = puzzleList[puzzle_name]
	elif mode == "puzzleExtract":
		selectedPuzzle = pidStart

		jsonFile = readJson(jsonPath)
		puzzle = translatePuzzle(jsonFile[selectedPuzzle])
	elif mode == "puzzleSpeedrun":
		puzzles = readJson(jsonPath)

		skip = True
		for pid, p in puzzles.items():
			if pid == pidStart:
				skip = False
			if skip:
				continue
			try:
				puzzle = translatePuzzle(p)
			except Exception as e:
				print(f"Error translating : {e}")
				print(p)
				exit(0)
			puzzle, initialState = initPuzzle(puzzle)
			solver = Solver(puzzle["grid"], puzzle["constraints"])
			try:
				solver.solve(initialState)
			except Exception as e:
				print(f"Error solving : {e}")
				print(p)
				exit(0)

			if len(solver.solutions) != 1:
				# Somethings wrong, show it
				print("Puzzle:", p["id"])
				print("Solutions:")
				for solutionNumber, solution in enumerate(solver.solutions):
					print(f"Solution {solutionNumber + 1}:")
					solution.show(puzzle["constraints"], puzzle["holes"])
					print("---")
				exit(0)
		print("All good !")
		exit(0)

	else:
		print("Invalid mode")
		exit()

	puzzle, initialState = initPuzzle(puzzle)
	solver = Solver(puzzle["grid"], puzzle["constraints"])
	solver.solve(initialState)

	print(f"First solution: {solver.firstS}")
	print(f"Total: {solver.finalT}")
	print("Number of solutions found:", len(solver.solutions))
	for solutionNumber, solution in enumerate(solver.solutions):
		print(f"Solution {solutionNumber + 1}:")
		solution.show(puzzle["constraints"], puzzle["holes"])
		print("---")
