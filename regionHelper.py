from typing import Set, Tuple

from edges import EdgeState
from position import Position

RangeSize = tuple[int, int]


def regionSizeHelper(state, p: Position) -> RangeSize:
	minR, maxR = state.uf.size[p], 0
	toCheck = [p]
	checked = set()
	while len(toCheck) > 0:
		currentTmp = toCheck.pop()
		currentR = state.uf.find(currentTmp)
		if currentR in checked or currentTmp in checked:
			continue
		maxR += state.uf.size[currentR]
		for c in state.uf.connectables[currentR]:
			if c in toCheck or c in checked or not state.uf.canJoin(p, c):
				continue
			toCheck.append(c)
		checked.add(currentR)
	return minR, maxR


def separateRegions(state, p: Position, q: Position) -> bool:
	for e in state.edges:
		if not isinstance(e[1], tuple):
			continue
		e1, e2 = e
		if (state.uf.find(e1[0]) == state.uf.find(p) and state.uf.find(e2[0]) == state.uf.find(q)) or (
				state.uf.find(e1[0]) == state.uf.find(q) and state.uf.find(e2[0]) == state.uf.find(p)):
			if not state.set_edge(e, EdgeState.PRESENT, False):
				return False
	state.uf.disjoint(p, q)
	return True


def joinRegions(state, p: Position, q: Position) -> bool:
	for e in state.edges:
		if not isinstance(e[1], tuple):
			continue
		e1, e2 = e
		if (state.uf.find(e1[0]) == state.uf.find(p) and state.uf.find(e2[0]) == state.uf.find(q)) or (
				state.uf.find(e1[0]) == state.uf.find(q) and state.uf.find(e2[0]) == state.uf.find(p)):
			if not state.set_edge(e, EdgeState.ABSENT, False):
				return False
	state.uf.union(p, q)
	return True


def closeRegion(state, p: Position, willTakeConnectables: bool) -> bool:
	tmp = set(state.uf.connectables[p])
	if willTakeConnectables:
		while len(tmp) > 0:
			for c in tmp:
				if not state.uf.union(p, c):
					return False
				mainR = state.uf.find(c)
				for e in state.edges:
					if not isinstance(e[1], tuple):
						continue
					e1, e2 = e
					if state.uf.find(e1[0]) == mainR and state.uf.find(e2[0]) == mainR:
						if not state.set_edge(e, EdgeState.ABSENT):
							return False
			del tmp
			tmp = set(state.uf.connectables[state.uf.find(p)])
	else:
		for c in tmp:
			separateRegions(state, p, c)
	return True


def get_region_cells(state, region_id: Position) -> Set[Position]:
	return set([cell for cell in state.grid.cells if state.uf.find(cell) == region_id])


def get_region_shape(state, region_id: Position) -> Tuple[Tuple[int, int], ...]:
	return get_region_shape_hard(get_region_cells(state, state.uf.find(region_id)))


def get_region_shape_hard(region_cells: Set[Position]) -> Tuple[Tuple[int, int], ...]:
	min_x = min(x for x, y in region_cells)
	min_y = min(y for x, y in region_cells)

	normalized = frozenset((x - min_x, y - min_y) for x, y in region_cells)
	all_variants = [normalized]

	rotated = frozenset((y, -x) for x, y in normalized)
	min_rx = min(x for x, y in rotated)
	min_ry = min(y for x, y in rotated)
	all_variants.append(frozenset((x - min_rx, y - min_ry) for x, y in rotated))

	rotated = frozenset((-x, -y) for x, y in normalized)
	min_rx = min(x for x, y in rotated)
	min_ry = min(y for x, y in rotated)
	all_variants.append(frozenset((x - min_rx, y - min_ry) for x, y in rotated))

	rotated = frozenset((-y, x) for x, y in normalized)
	min_rx = min(x for x, y in rotated)
	min_ry = min(y for x, y in rotated)
	all_variants.append(frozenset((x - min_rx, y - min_ry) for x, y in rotated))

	reflected = frozenset((-x, y) for x, y in normalized)
	min_rx = min(x for x, y in reflected)
	min_ry = min(y for x, y in reflected)
	all_variants.append(frozenset((x - min_rx, y - min_ry) for x, y in reflected))

	reflected = frozenset((x, -y) for x, y in normalized)
	min_rx = min(x for x, y in reflected)
	min_ry = min(y for x, y in reflected)
	all_variants.append(frozenset((x - min_rx, y - min_ry) for x, y in reflected))

	reflected = frozenset((y, x) for x, y in normalized)
	min_rx = min(x for x, y in reflected)
	min_ry = min(y for x, y in reflected)
	all_variants.append(frozenset((x - min_rx, y - min_ry) for x, y in reflected))

	reflected = frozenset((-y, -x) for x, y in normalized)
	min_rx = min(x for x, y in reflected)
	min_ry = min(y for x, y in reflected)
	all_variants.append(frozenset((x - min_rx, y - min_ry) for x, y in reflected))

	return tuple(sorted(min(all_variants)))


def is_rectangle(region_cells: Set[Position]) -> bool:
	min_x = min(x for x, y in region_cells)
	max_x = max(x for x, y in region_cells)
	min_y = min(y for x, y in region_cells)
	max_y = max(y for x, y in region_cells)

	width = max_x - min_x + 1
	height = max_y - min_y + 1

	return len(region_cells) == width * height


def shapes_equal(shape1: Tuple[Tuple[int, int], ...], shape2: Tuple[Tuple[int, int], ...]) -> bool:
	return shape1 == shape2


def get_region_shapes(state) -> dict[Position, Tuple[Tuple[int, int], ...]]:
	shapes = {}
	for region_id in state.uf.parentList:
		if len(state.uf.connectables[region_id]) == 0:
			cells = get_region_cells(state, region_id)
			shapes[region_id] = get_region_shape_hard(cells)
	return shapes
