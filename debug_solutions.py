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

print(f"Number of solutions found: {len(solver.solutions)}")
for solutionNumber, solution in enumerate(solver.solutions):
	print(f"\n=== Solution {solutionNumber + 1} ===")
	solution.show(testedConstraints, puzzle["holes"])
	
	# Analyze regions
	regions = {}
	for cell in solution.grid.cells:
		region_id = solution.uf.find(cell)
		if region_id not in regions:
			regions[region_id] = []
		regions[region_id].append(cell)
	
	print(f"Regions found: {len(regions)}")
	for i, (region_id, cells) in enumerate(sorted(regions.items())):
		connectables = solution.uf.connectables.get(region_id, set())
		adjacents = solution.uf.getAdjacent(region_id)
		print(f"\nRegion {region_id}: size={len(cells)}, cells={sorted(cells)}")
		print(f"  connectables[{region_id}] = {connectables}")
		print(f"  getAdjacent({region_id}) = {adjacents}")
		
		# Check unjoinable
		unjoinable_pairs = [r for r in solution.uf.unjoinable if region_id in r]
		if unjoinable_pairs:
			print(f"  unjoinable pairs: {unjoinable_pairs}")
		
		# Check if two adjacent regions have the same size
		for adj in adjacents:
			if solution.uf.size[region_id] == solution.uf.size[adj]:
				print(f"    ⚠️  VIOLATION: Region {region_id} (size {solution.uf.size[region_id]}) adjacent to {adj} (size {solution.uf.size[adj]})")
	
	print("---")



