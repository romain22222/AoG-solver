from examples import puzzleList
from solver import State, Solver, get_vertices

puzzle_name = "size_separation"
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

print(f"Nombre de solutions trouvées : {len(solver.solutions)}")
for solutionNumber, solution in enumerate(solver.solutions):
	print(f"\n=== Solution {solutionNumber + 1} ===")
	solution.show(testedConstraints, puzzle["holes"])
	
	# Analyse des régions
	regions = {}
	for cell in solution.grid.cells:
		region_id = solution.uf.find(cell)
		if region_id not in regions:
			regions[region_id] = []
		regions[region_id].append(cell)
	
	print(f"Régions trouvées : {len(regions)}")
	for i, (region_id, cells) in enumerate(sorted(regions.items())):
		connectables = solution.uf.connectables.get(region_id, set())
		adjacents = solution.uf.getAdjacent(region_id)
		print(f"\nRégion {region_id}: taille={len(cells)}, cells={sorted(cells)}")
		print(f"  connectables[{region_id}] = {connectables}")
		print(f"  getAdjacent({region_id}) = {adjacents}")
		
		# Vérifier unjoinable
		unjoinable_pairs = [r for r in solution.uf.unjoinable if region_id in r]
		if unjoinable_pairs:
			print(f"  unjoinable pairs: {unjoinable_pairs}")
		
		# Vérifier si deux régions adjacentes ont la même taille
		for adj in adjacents:
			if solution.uf.size[region_id] == solution.uf.size[adj]:
				print(f"    ⚠️  VIOLATION: Région {region_id} (taille {solution.uf.size[region_id]}) adjacente à {adj} (taille {solution.uf.size[adj]})")
	
	print("---")



