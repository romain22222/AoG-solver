from enum import Enum

from direction import Direction
from position import Position

PartEdge = tuple[Position, Direction]
FullEdge = tuple[PartEdge, PartEdge]
Edge = FullEdge | PartEdge


class EdgeState(Enum):
	ABSENT = 0
	PRESENT = 1
	UNKNOWN = None
