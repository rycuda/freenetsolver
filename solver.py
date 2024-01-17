"""
A quick and hopefully simple attempt to use wavefunction collapse to solve freenet/pipedreams


coordinate system 0,0 top left, positive x is right, positive y is down
rotations are in 90 degree increments clockwise with 0 being left
"""

from itertools import chain
from functools import reduce
from random import choice
import logging

logger = logging.getLogger(__name__)


class Position:
    """
    Define a location in two dimensional space
    """

    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __key(self):
        return (self.x, self.y)

    def __hash__(self):
        return hash(self.__key())

    def __eq__(self, other):
        if isinstance(other, Position):
            return self.__key() == other.__key()
        return NotImplemented

    def __repr__(self):
        return f"Position({self.x},{self.y})"

    def move(self, direction):
        return Position(self.x + direction.x, self.y + direction.y)


class Direction:
    """
    Define a direction in 2D.
    This would probably be better called displacement...
    coordinate system 0,0 top left, positive x is right, positive y is down
    rotations are in 90 degree increments clockwise with 0 being left
    """

    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __key(self):
        return (self.x, self.y)

    def __hash__(self):
        return hash(self.__key())

    def __eq__(self, other):
        if isinstance(other, Direction):
            return self.__key() == other.__key()
        return NotImplemented

    def __str__(self):
        return self.__repr__()

    def __repr__(self):
        return f"Direction({self.x},{self.y})"

    def opposite(self):
        return Direction(self.x * -1, self.y * -1)

    def rotate(self, amount):
        amount = amount % 4
        if amount == 0:
            return self
        return Direction(-self.y, self.x).rotate(amount - 1)


class Shape:
    """
    represent the shapes that can be found in a freenet game
    connections are a set of Directions representing the points that the shape touches the edges of the tile
    character is an array of single character strings representing the printable form of the tile in rotation order
    """
    def __init__(self, connections, character):
        self.connections = set(connections)
        self.prints_as = character

    def rotate(self, rotation):
        return {connection.rotate(rotation) for connection in self.connections}


class Piece:
    """
    A piece on the freenet grid
    Has a Shape, a Position, a rotation
    in addition keeps track of the allowed rotations for that piece
    """
    def __init__(self, shape, position, rotation=0):
        self.shape = shape
        self.rotation = rotation
        self.position = position
        self.connections = self.shape.connections
        self.possible_rotations = list(range(0, 4))
        self.rotational_symmetry()

    def __str__(self):
        return self.prints_as()

    def prints_as(self):
        return self.shape.prints_as[self.rotation]

    def set_rotation(self, rotation):
        self.rotation = rotation % 4
        self.connections = self.shape.rotate(self.rotation)

    def canconnect(self, direction):
        if len(self.connections) == 0:
            return False
        for rotation in self.possible_rotations:
            if direction in self.shape.rotate(rotation):
                return True
        return False

    def mustconnect(self, direction):
        if all(
            [
                direction in self.shape.rotate(rotation)
                for rotation in self.possible_rotations
            ]
        ):
            return True
        return False

    def rotational_symmetry(self):
        logger.debug("testing rotational symmetry")
        connections_list = []
        valid_rotations = []
        for rotation in self.possible_rotations:
            connections = self.shape.rotate(rotation)
            if connections not in connections_list:
                connections_list.append(connections)
                valid_rotations.append(rotation)
        self.possible_rotations = valid_rotations


class Grid:
    """
    The freenet game grid
    """
    def __init__(self, description):
        # test description is a square array of arrays
        # test description is an array of array of strings
        self.grid = [
            [Piece(SHAPES[cell], Position(x, y)) for x, cell in enumerate(row)]
            for y, row in enumerate(description)
        ]
        self.x_max = len(self.grid[0])
        self.y_max = len(self.grid)

    def ingrid(self, position):
        x = position.x
        y = position.y
        return 0 <= x < self.x_max and 0 <= y < self.y_max

    def piece(self, position):
        if self.ingrid(position):
            return self.grid[position.y][position.x]
        return Piece(SHAPES["Edge"], position)

    def prints_as(self):
        return "\n".join(
            ["".join([cell.prints_as() for cell in row]) for row in self.grid]
        )

    def permutations(self):
        return reduce(
            lambda a, e: a * len(e.possible_rotations),
            chain.from_iterable(self.grid),
            1,
        )

    def neighbours(self, position):
        neighbours = set()
        for direction in DIRECTIONS:
            neighbours.add((direction, self.piece(position.move(direction))))
        return neighbours

    def collapse(self, focus):
        logger.debug(f"---=== collapsing {focus.position}")
        logger.debug(f"before: {focus}")
        valid_directions = set()
        mandatory_directions = set()
        for direction, neighbour in self.neighbours(focus.position):
            logger.debug(f"{direction}")
            logger.debug(f"{neighbour}")
            if neighbour.canconnect(direction.opposite()):
                valid_directions.add(direction)
                logger.debug("valid")
            if neighbour.mustconnect(direction.opposite()):
                mandatory_directions.add(direction)
                logger.debug("valid")
        valid_rotations = []
        for rotation in focus.possible_rotations:
            connections = focus.shape.rotate(rotation)
            logger.debug(f"rotation: {rotation},{connections}")
            if connections.issubset(valid_directions) and mandatory_directions.issubset(
                connections
            ):
                logger.debug("valid")
                valid_rotations.append(rotation)
        focus.possible_rotations = valid_rotations
        focus.set_rotation(choice(focus.possible_rotations))
        logger.debug(f"after: {focus}")


LEFT = Direction(-1, 0)
UP = LEFT.rotate(1)
RIGHT = LEFT.rotate(2)
DOWN = LEFT.rotate(3)

DIRECTIONS = [
    LEFT,
    UP,
    RIGHT,
    DOWN,
]

SHAPES = {
    "Corner": Shape(
        [LEFT, UP],
        [
            "\u2518",
            "\u2514",
            "\u250C",
            "\u2510",
        ],
    ),
    "Straight": Shape(
        [LEFT, RIGHT],
        [
            "\u2500",
            "\u2502",
            "\u2500",
            "\u2502",
        ],
    ),
    "Tee": Shape(
        [LEFT, UP, RIGHT],
        [
            "\u2534",
            "\u251C",
            "\u252C",
            "\u2524",
        ],
    ),
    "End": Shape(
        [LEFT],
        [
            "\u2574",
            "\u2575",
            "\u2576",
            "\u2577",
        ],
    ),
    "Edge": Shape([], ["", "", "", ""]),
}

TEST = [
    [
        "End",
        "End",
        "End",
        "End",
    ],
    [
        "Straight",
        "Straight",
        "Straight",
        "Straight",
    ],
    [
        "Corner",
        "Corner",
        "Corner",
        "Corner",
    ],
    [
        "Tee",
        "Tee",
        "Tee",
        "Tee",
    ],
]

SAMPLE = [
    ["Corner", "End", "End", "End"],
    ["Tee", "End", "Tee", "Tee"],
    ["Tee", "Corner", "Straight", "End"],
    ["End", "Corner", "Tee", "End"],
]


def main():
    grid = Grid(SAMPLE)
    previous_permutations = grid.permutations() + 1
    print(grid.permutations())
    print(grid.prints_as(), "\n")
    while grid.permutations() > 1 and previous_permutations != grid.permutations():
        [grid.collapse(cell) for row in grid.grid for cell in row]
        print(grid.permutations())
        print(grid.prints_as(), "\n")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    main()
