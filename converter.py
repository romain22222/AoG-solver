from typing import TypedDict, List

from constraints import Constraint, PrecisionConstraint, MingleShapeConstraint, MatchConstraint, \
	MismatchShapeConstraint, LoopyConstraint, MinimumConstraint, MaximumConstraint, SolitudeConstraint, BoxyConstraint, \
	NonBoxyConstraint, BrickyConstraint, GridSymbol, RoseWindowSymbol, RoseWindowShape, AreaNumberSymbol, \
	PalisadeSymbol, CycleType, CompassSymbol, ShapeBankConstraint
from constraints.size_separation import SizeSeparationConstraint
from constraints.watchtower import WatchtowerSymbol, WatchtowerConstraint
from direction import Direction
from position import Position
from regionHelper import get_region_shape_hard
from solver import Grid


class Puzzle(TypedDict):
	grid: Grid
	holes: set[Position]
	constraints: List[Constraint]


class JsonPuzzle(TypedDict):
	id: int
	dataPath: str
	cubeName: str
	worldPos: str
	zoneIndex: int
	myWindow: str
	unlockReq: str
	isMandatory: bool
	version: int
	puzzleVersion: int
	difficulty: int
	comment: str
	rows: int
	cols: int
	tileCount: int
	shapes: List[str]
	rules: List[str]
	puzzle: str
	solution: str


PALISADE_INT_TO_CYCLE = {
	"0": CycleType.EMPTY,
	"1": CycleType.ONE,
	"2": CycleType.STRAIGHT,
	"3": CycleType.DEAD,
	"4": CycleType.CELL,
	"7": CycleType.ANGLE
}


def getCompassDirections(tileText: str):
	# first get UDLR indexes
	north = tileText.index("U")
	south = tileText.index("D")
	west = tileText.index("L")
	east = tileText.index("R")
	nAm = int(tileText[north + 1:south]) if north+1 != south else None
	sAm = int(tileText[south + 1:west]) if south+1 != west else None
	wAm = int(tileText[west + 1:east]) if west+1 != east else None
	eAm = int(tileText[east + 1:]) if east+1 != len(tileText) else None
	return nAm, sAm, wAm, eAm


def getLineTilesAndEdges(line: str) -> Tuple[List[str], List[str]]:
	lineCpy = line
	tiles = []
	edges = []
	while len(lineCpy) > 1:
		maxLen = len(lineCpy)
		currentEdge = lineCpy[maxLen - 1]
		edges.append(currentEdge)
		if currentEdge == " ":
			tiles.append("  ")
			lineCpy = lineCpy[:maxLen-3]
			continue
		if "R" in lineCpy[maxLen-4:maxLen-2]:
			compassT = ""
			while lineCpy[len(lineCpy)-1] != "U":
				compassT = lineCpy[len(lineCpy)-1] + compassT
				lineCpy = lineCpy[:maxLen-1]
			compassT = lineCpy[len(lineCpy)-1] + compassT
			tiles.append(compassT)
		else:
			lineCpy = lineCpy[:maxLen-1]
			tiles.append(lineCpy[maxLen-2:maxLen])
			lineCpy = lineCpy[:maxLen-2]
	return list(reversed(tiles)), list(reversed(edges))


def translatePuzzle(jsonPuzzle) -> Puzzle:
	grid = Grid(jsonPuzzle['cols'], jsonPuzzle['rows'])
	holes = set()
	constraints = []
	gridSymbols = {}
	edgeSymbols = {}
	vertexSymbols = []
	puzzleLines = jsonPuzzle['puzzle'].split('/')
	shapeList = []

	if jsonPuzzle["shapes"] is not None:
		for shape in jsonPuzzle["shapes"]:
			shapeText = shape["text"].split('/')
			shapeList.append([])
			for y in range(len(shapeText)):
				for x in range(len(shapeText[y])):
					if shapeText[y][x] != " ":
						shapeList[len(shapeList) - 1].append(Position(x, y))

		for i in range(len(shapeList)):
			shapeList[i] = get_region_shape_hard(set(shapeList[i]))

	# grid symbols
	for y in range(jsonPuzzle['rows']):
		lineTiles, lineEdges = getLineTilesAndEdges(puzzleLines[y])
		for x in range(jsonPuzzle['cols']):
			tileText = lineTiles[x]
			if tileText == '  ':
				holes.add(Position(x, y))
			elif tileText != '..':
				if tileText[0] == "P":
					# Rose window
					if "roseWindow" not in gridSymbols.keys():
						gridSymbols["roseWindow"] = []
					gridSymbols["roseWindow"].append(RoseWindowSymbol(Position(x, y), RoseWindowShape(int(tileText[1]))))
				elif tileText[0] == "S":
					# TBD
					pass
				elif tileText[0] in "0123456789":
					# Area number
					if "area" not in gridSymbols.keys():
						gridSymbols["area"] = []
					gridSymbols["area"].append(AreaNumberSymbol(Position(x, y), int(tileText)))
				elif tileText[0] == "F":
					# Palisade
					if "palisade" not in gridSymbols.keys():
						gridSymbols["palisade"] = []
					gridSymbols["palisade"].append(PalisadeSymbol(Position(x, y), PALISADE_INT_TO_CYCLE[tileText[1]]))
				elif tileText[0] == "U":
					# Compass
					if "compass" not in gridSymbols.keys():
						gridSymbols["compass"] = []
					north, south, west, east = getCompassDirections(tileText)
					gridSymbols["compass"].append(CompassSymbol(Position(x, y), north, south, east, west))
		for x in range(len(lineEdges)-1):
			edgeEWText = lineEdges[x]
			if edgeEWText not in [" ", "|"]:
				edgeSymbols.append([[[Position(x, y), Direction.E], [Position(x + 1, y), Direction.W]], edgeEWText])

	# vertex symbols
	for y in range(jsonPuzzle['rows'] + 1):
		for x in range(jsonPuzzle['cols'] + 1):
			vertexText = puzzleLines[2 * y][3 * x]
			if vertexText not in [" ", "+"]:
				vertexSymbols.append(WatchtowerSymbol(Position(x, y), int(vertexText)))

	# edge symbols (N/S)
	for y in range(jsonPuzzle['rows'] - 1):
		for x in range(jsonPuzzle['cols']):
			edgeNSText = puzzleLines[2 * (y + 1)][3 * x + 1:3 * x + 2]
			if edgeNSText not in ["  ", "--"]:
				edgeSymbols.append([[[Position(x, y), Direction.S], [Position(x, y + 1), Direction.N]], edgeNSText])

	if vertexSymbols:
		constraints.append(WatchtowerConstraint(vertexSymbols))

	for rule in jsonPuzzle["rules"]:
		ruleInfos = rule.split(" ")
		match ruleInfos[0]:
			case "ALL_SHAPES_SAME":
				constraints.append(MatchConstraint())
			case "ALL_SHAPES_DIFFERENT":
				constraints.append(MismatchShapeConstraint())
			case "AREA_EQUALS":
				constraints.append(PrecisionConstraint(int(ruleInfos[1])))
			case "AREA_AT_LEAST":
				constraints.append(MinimumConstraint(int(ruleInfos[1])))
			case "AREA_AT_MOST":
				constraints.append(MaximumConstraint(int(ruleInfos[1])))
			case "ADJACENT_SHAPES_DIFFERENT":
				constraints.append(MingleShapeConstraint())
			case "ADJACENT_SIZES_DIFFERENT":
				constraints.append(SizeSeparationConstraint())
			case "ONE_SYMBOL_PER_REGION":
				constraints.append(SolitudeConstraint())
			case "ONLY_RECTANGLES":
				constraints.append(BoxyConstraint())
			case "NO_RECTANGLES":
				constraints.append(NonBoxyConstraint())
			case "NO_3_WAY_INTERSECTIONS":
				constraints.append(LoopyConstraint())
			case "NO_4_WAY_INTERSECTIONS":
				constraints.append(BrickyConstraint())
			case "SHAPE_BANK":
				constraints.append(ShapeBankConstraint([shapeList[int(i)-1] for i in ruleInfos[1:]]))
			case _:
				print("Can't recognize rule " + rule)
