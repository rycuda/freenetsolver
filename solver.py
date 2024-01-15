from itertools import product,chain
from random import choice
import logging

logger=logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

# coordinate system 0,0 top left, positive x is right, positive y is down
# rotations are in 90 degree increments clockwise with 0 being left

class Position:
    def __init__(self,x,y):
        self.x = x
        self.y = y

    def __key(self):
        return((self.x,self.y))

    def __hash__(self):
        return hash(self.__key())

    def __eq__(self,other):
        if isinstance(other,Position):
            return self.__key() == other.__key()
        return NotImplemented

    def __repr__(self):
        return f'Position({self.x},{self.y})'

    def move(self,direction):
        return Position(
                self.x + direction.x,
                self.y + direction.y
                )

class Direction:
    def __init__(self,x,y):
        self.x = x
        self.y = y

    def __key(self):
        return((self.x,self.y))

    def __hash__(self):
        return hash(self.__key())

    def __eq__(self,other):
        if isinstance(other,Direction):
            return self.__key() == other.__key()
        return NotImplemented

    def __str__(self):
        return self.__repr__()
    
    def __repr__(self):
        return f'Direction({self.x},{self.y})'

    def opposite(self):
        return Direction(self.x*-1,self.y*-1)

    def rotate(self, amount):
        amount = amount%4
        if amount == 0:
            return self
        return Direction(
            - self.y,
            self.x
        ).rotate(amount -1)

class Shape:
    def __init__(self,connections,character):
        self.connections = connections
        self.prints_as = character

    def rotate(self,rotation):
        return [connection.rotate(rotation) for connection in self.connections]

class Piece:
    def __init__(self,shape,position,rotation=0):
        self.shape = shape
        self.rotation = rotation
        self.position = position
        self.connections = self.shape.connections
        self.possible_rotations = list(range(0,4))

    def __str__(self):
        return self.prints_as()

    def prints_as(self):
        return self.shape.prints_as[self.rotation]

    def set_rotation(self,rotation):
        self.rotation = rotation%4
        self.connections = self.shape.rotate(self.rotation)

class Grid:
    def __init__(self,description):
        #test description is a square array of arrays
        #test description is an array of array of strings
        self.grid = [[Piece(SHAPES[cell],Position(x,y)) for x,cell in enumerate(row)] for y,row in enumerate(description)]
        self.x_max = len(self.grid[0])
        self.y_max = len(self.grid)

    def ingrid(self,position):
        x=position.x
        y=position.y
        return x<self.x_max and x>=0 and y<self.y_max and y>=0

    def piece(self,position):
        if self.ingrid(position):
            return self.grid[position.y][position.x]
        return Piece(SHAPES['Edge'],position)

    def neighbours(self,cell):
        if self.ingrid(cell.position):
            return [self.piece(cell.position.move(direction)) for direction in DIRECTIONS]
        return None

    def prints_as(self):
        return '\n'.join([''.join([cell.prints_as() for cell in row]) for row in self.grid])

LEFT = Direction(-1,0)
RIGHT = Direction(1,0)
DOWN = Direction(0,1)
UP = Direction(0,-1)

DIRECTIONS = [
        LEFT,
        UP,
        RIGHT,
        DOWN,
        ]

SHAPES = {
        "Corner":Shape([LEFT,UP],[u'\u2518',u'\u2514',u'\u250C',u'\u2510',]),
        "Straight":Shape([LEFT,RIGHT],[u'\u2500',u'\u2502',u'\u2500',u'\u2502',]),
        "Tee":Shape([LEFT,UP,RIGHT],[u'\u2534',u'\u251C',u'\u252C',u'\u2524',]),
        "End":Shape([LEFT],[u'\u2574',u'\u2575',u'\u2576',u'\u2577',]),
        "Edge":Shape([],['','','',''])
        }

TEST = [
        ['End','End','End','End',],
        ['Straight','Straight','Straight','Straight',],
        ['Corner','Corner','Corner','Corner',],
        ['Tee','Tee','Tee','Tee',],
        ]

SAMPLE = [
        ['Corner','End','End','End'],
        ['Tee','End','Tee','Tee'],
        ['Tee','Corner','Straight','End'],
        ['End','Corner','Tee','End'],
        ]


def canconnect(focus,direction):
    if len(focus.connections) == 0 : return False
    for rotation in focus.possible_rotations:
        if direction in focus.shape.rotate(rotation):
            return True
    return False

def mustconnect(focus,direction):
    if all([direction in focus.shape.rotate(rotation) for rotation in focus.possible_rotations]):
        return True
    return False

def collapse(grid,focus):
    logger.debug(f'---=== collapsing {focus.position}')
    logger.debug(f"before: {focus}")
    valid_directions = set()
    mandatory_directions = set()
    for direction in DIRECTIONS:
        logger.debug(f"{direction}")
        neighbour = grid.piece(focus.position.move(direction))
        logger.debug(f"{neighbour}")
        if canconnect(neighbour,direction.opposite()):
            valid_directions.add(direction)
            logger.debug('valid')
        if mustconnect(neighbour,direction.opposite()):
            mandatory_directions.add(direction)
            logger.debug('valid')
    valid_rotations = []
    for rotation in focus.possible_rotations:
        connections = focus.shape.rotate(rotation)
        logger.debug(f"rotation: {rotation},{connections}")
        if set(connections).issubset(valid_directions) and mandatory_directions.issubset(set(connections)):
            logger.debug('valid')
            valid_rotations.append(rotation)
    focus.possible_rotations=valid_rotations
    focus.set_rotation(choice(focus.possible_rotations))
    logger.debug(f"after: {focus}")

def main():
    grid = Grid(SAMPLE)
    print(grid.prints_as(),'\n')
    for itter in range(0,2):
        for row in grid.grid:
            for cell in row:
                collapse(grid,cell)
        print(grid.prints_as(),'\n')
    print('\n'.join(['-'.join([f"{cell.rotation}-{cell.connections}" for cell in row]) for row in grid.grid]))

if __name__ == "__main__":
    main()
