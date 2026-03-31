from enum import Enum


class Direction(Enum):
	N = 0
	S = 1
	E = 2
	W = 3


DIRS = [Direction.N, Direction.E, Direction.S, Direction.W]
OPPOSITE = {
	Direction.N: Direction.S,
	Direction.S: Direction.N,
	Direction.E: Direction.W,
	Direction.W: Direction.E
}
