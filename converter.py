import json
from typing import TypedDict, List

from constraints import *
from direction import Direction
from edges import FullEdge
from position import Position
from regionHelper import get_region_shape_hard
from solver import Grid


class Puzzle(TypedDict):
	grid: Grid
	holes: set[Position]
	constraints: List[Constraint]
	forcedEdges: List[FullEdge]
	solution: tuple[List[FullEdge], List[FullEdge]]


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
	shapes: dict[str, str]
	rules: List[str]
	puzzle: str
	solution: str
	shapeBank: List[int]


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
	nAm = int(tileText[north + 1:south]) if north + 1 != south else None
	sAm = int(tileText[south + 1:west]) if south + 1 != west else None
	wAm = int(tileText[west + 1:east]) if west + 1 != east else None
	eAm = int(tileText[east + 1:]) if east + 1 != len(tileText) else None
	return nAm, sAm, wAm, eAm


def getLineTilesAndEdges(line: str) -> tuple[List[str], List[str]]:
	lineCpy = line
	tiles = []
	edges = []
	while len(lineCpy) > 1:
		maxLen = len(lineCpy)
		currentEdge = lineCpy[maxLen - 1]
		edges.append(currentEdge)
		if currentEdge == " ":
			tiles.append("  ")
			lineCpy = lineCpy[:maxLen - 3]
			continue
		if "R" in lineCpy[maxLen - 4:maxLen - 2]:
			compassT = ""
			while lineCpy[len(lineCpy) - 1] != "U":
				compassT = lineCpy[len(lineCpy) - 1] + compassT
				lineCpy = lineCpy[:maxLen - 1]
			compassT = lineCpy[len(lineCpy) - 1] + compassT
			tiles.append(compassT)
			lineCpy = lineCpy[:maxLen - 1]
		elif "S" in lineCpy[maxLen - 4:maxLen - 3]:
			polyominoT = ""
			while lineCpy[len(lineCpy) - 1] != "S":
				polyominoT = lineCpy[len(lineCpy) - 1] + polyominoT
				lineCpy = lineCpy[:maxLen - 1]
			polyominoT = lineCpy[len(lineCpy) - 1] + polyominoT
			tiles.append(polyominoT)
			lineCpy = lineCpy[:maxLen - 1]
		else:
			lineCpy = lineCpy[:maxLen - 1]
			tiles.append(lineCpy[maxLen - 3:maxLen-1])
			lineCpy = lineCpy[:maxLen - 3]
	return list(reversed(tiles)), list(reversed(edges))


def translatePuzzle(jsonPuzzle: JsonPuzzle) -> Puzzle:
	grid = Grid(jsonPuzzle['cols'], jsonPuzzle['rows'])
	holes = set()
	constraints = []
	gridSymbols = {}
	edgeSymbols = {}
	vertexSymbols = []
	puzzleLines = jsonPuzzle['puzzle'].split('/')
	shapeList = []
	forcedEdges = []

	if jsonPuzzle["shapes"]:
		for shape in jsonPuzzle["shapes"].values():
			shapeText = shape.split('/')
			shapeList.append([])
			for y in range(len(shapeText)):
				for x in range(len(shapeText[y])):
					if shapeText[y][x] != " ":
						shapeList[len(shapeList) - 1].append((x, y))

	for i in range(len(shapeList)):
		shapeList[i] = get_region_shape_hard(set(shapeList[i]))

	# grid symbols + edges E/W
	for y in range(jsonPuzzle['rows']):
		lineTiles, lineEdges = getLineTilesAndEdges(puzzleLines[2*y+1])
		for x in range(jsonPuzzle['cols']):
			tileText = lineTiles[x]
			if tileText == '  ':
				holes.add((x, y))
			elif tileText != '..':
				if tileText[0] == "P":
					# Rose window
					if "roseWindow" not in gridSymbols.keys():
						gridSymbols["roseWindow"] = []
					gridSymbols["roseWindow"].append(
						RoseWindowSymbol((x, y), RoseWindowShape(int(tileText[1]))))
				elif tileText[0] == "S":
					if "polyomino" not in gridSymbols.keys():
						gridSymbols["polyomino"] = []
					gridSymbols["polyomino"].append(PolyominoSymbol((x, y), shapeList[int(tileText[1:]) - 1]))
				elif tileText[0] in "0123456789":
					# Area number
					if "area" not in gridSymbols.keys():
						gridSymbols["area"] = []
					gridSymbols["area"].append(AreaNumberSymbol((x, y), int(tileText)))
				elif tileText[0] == "F":
					# Palisade
					if "palisade" not in gridSymbols.keys():
						gridSymbols["palisade"] = []
					gridSymbols["palisade"].append(PalisadeSymbol((x, y), PALISADE_INT_TO_CYCLE[tileText[1]]))
				elif tileText[0] == "U":
					# Compass
					if "compass" not in gridSymbols.keys():
						gridSymbols["compass"] = []
					north, south, west, east = getCompassDirections(tileText)
					gridSymbols["compass"].append(CompassSymbol((x, y), north, south, east, west))
		for x in range(len(lineEdges) - 1):
			edgeEWText = lineEdges[x]
			edge = ((x, y), Direction.E), ((x + 1, y), Direction.W)
			if edgeEWText in " |":
				continue
			if edgeEWText == "=":
				if "gemini" not in gridSymbols.keys():
					gridSymbols["gemini"] = []
				gridSymbols["gemini"].append(GeminiSymbol(edge))
			elif edgeEWText == "!":
				if "delta" not in gridSymbols.keys():
					gridSymbols["delta"] = []
				gridSymbols["delta"].append(DeltaSymbol(edge))
			elif edgeEWText in "0123456789":
				if "difference" not in gridSymbols.keys():
					gridSymbols["difference"] = []
				gridSymbols["difference"].append(DifferenceSymbol(edge, int(edgeEWText)))
			elif edgeEWText in "<>":
				if "inequality" not in gridSymbols.keys():
					gridSymbols["inequality"] = []
				orientation = Direction.E if edgeEWText == ">" else Direction.W
				gridSymbols["inequality"].append(InequalitySymbol(edge, orientation))
			elif edgeEWText == "#":
				forcedEdges.append(edge)
			else:
				print("Untreated edge symbol " + edgeEWText)
				print(lineEdges)
				exit()

	# vertex symbols
	for y in range(jsonPuzzle['rows'] + 1):
		for x in range(jsonPuzzle['cols'] + 1):
			vertexText = puzzleLines[2 * y][3 * x]
			if vertexText not in [" ", "+"]:
				vertexSymbols.append(WatchtowerSymbol((x, y), vertexText))

	# edge symbols (N/S)
	for y in range(jsonPuzzle['rows'] - 1):
		for x in range(jsonPuzzle['cols']):
			edgeNSText = puzzleLines[2 * (y + 1)][3 * x + 1:3 * x + 3]
			edge = ((x, y), Direction.S), ((x, y + 1), Direction.N)
			if edgeNSText in ["--", "  "]:
				continue
			if edgeNSText == "==":
				if "gemini" not in gridSymbols.keys():
					gridSymbols["gemini"] = []
				gridSymbols["gemini"].append(GeminiSymbol(edge))
			elif edgeNSText == "!!":
				if "delta" not in gridSymbols.keys():
					gridSymbols["delta"] = []
				gridSymbols["delta"].append(DeltaSymbol(edge))
			elif edgeNSText[1] in "0123456789":
				if "difference" not in gridSymbols.keys():
					gridSymbols["difference"] = []
				gridSymbols["difference"].append(DifferenceSymbol(edge, int(edgeNSText[1])))
			elif edgeNSText in "v^":
				if "inequality" not in gridSymbols.keys():
					gridSymbols["inequality"] = []
				orientation = Direction.S if edgeNSText == "v" else Direction.N
				gridSymbols["inequality"].append(InequalitySymbol(edge, orientation))
			elif edgeNSText == "##":
				forcedEdges.append(edge)
			else:
				print("Untreated edge symbol " + edgeNSText + "'" + puzzleLines[2 * (y + 1)] + "'")

	if vertexSymbols:
		constraints.append(WatchtowerConstraint(vertexSymbols))

	if "roseWindow" in gridSymbols.keys():
		constraints.append(RoseWindowConstraint(gridSymbols["roseWindow"]))
	if "area" in gridSymbols.keys():
		constraints.append(AreaNumberConstraint(gridSymbols["area"]))
	if "palisade" in gridSymbols.keys():
		constraints.append(PalisadeConstraint(gridSymbols["palisade"]))
	if "compass" in gridSymbols.keys():
		constraints.append(CompassConstraint(gridSymbols["compass"]))
	if "polyomino" in gridSymbols.keys():
		constraints.append(PolyominoConstraint(gridSymbols["polyomino"]))

	if "delta" in edgeSymbols.keys():
		constraints.append(DeltaSymbol(edgeSymbols["delta"]))
	if "gemini" in edgeSymbols.keys():
		constraints.append(GeminiSymbol(edgeSymbols["gemini"]))
	if "difference" in edgeSymbols.keys():
		constraints.append(DifferenceSymbol(edgeSymbols["difference"]))
	if "inequality" in edgeSymbols.keys():
		constraints.append(InequalitySymbol(edgeSymbols["inequality"]))

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
			case _:
				print("Can't recognize rule " + rule)

	if jsonPuzzle["shapeBank"]:
		constraints.append(ShapeBankConstraint([shapeList[int(i) - 1] for i in jsonPuzzle["shapeBank"]]))

	solutionPresent = []
	solutionAbsent = []
	for i, line in enumerate(jsonPuzzle["solution"].split("/")):
		if i % 2 == 0:
			for j in range(len(line)//3):
				if line[3*j+1] == "#":
					toAddIn = solutionPresent.append
				else:
					toAddIn = solutionAbsent.append
				toAddIn((((j, i//2-1), Direction.S), ((j, i//2), Direction.N)))
		else:
			for j in range(len(line)//3+1):
				if line[3 * j] == "#":
					toAddIn = solutionPresent.append
				else:
					toAddIn = solutionAbsent.append
				toAddIn((((j-1, i//2), Direction.E), ((j, i//2), Direction.W)))
	return {
		"grid": grid,
		"holes": holes,
		"constraints": constraints,
		"forcedEdges": forcedEdges,
		"solution": [solutionPresent, solutionAbsent]
	}


def readJson(jsonPath) -> dict[str, JsonPuzzle]:
	with open(jsonPath, "r") as jsonFile:
		jsonData = json.load(jsonFile)
		return jsonData
