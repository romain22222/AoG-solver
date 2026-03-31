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
			separateRegions(p, c)
	return True
