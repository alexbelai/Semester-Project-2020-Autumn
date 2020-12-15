class Node():
    """Node class used to represent tiles of the map for pathfinding."""
    def __init__(self, state, parent, action):
        self.state = state
        self.parent = parent
        self.action = action

class NodeQueue():
    """FCFS (first come first serve) queue-like object with the ability to remove nodes automatically when reading them from queue."""
    def __init__ (self):
        self.frontier = []
    
    def add(self, node):
        """Adds given node to the end of the queue"""
        self.frontier.append(node)
    
    def contains_state(self, state):
        """Returns true if queue already contains a given state, False otherwise"""
        return any(node.state == state for node in self.frontier)

    def empty(self):
        """Returns True if queue is empty, False otherwise"""
        if len(self.frontier) == 0:
            return True
        else:
            return False

    def get(self):
        """Returns the first node in queue"""
        if self.empty():
            raise Exception("Empty frontier")
        else:
            node = self.frontier[0]
            self.frontier = self.frontier[1:]
            return node
class Map():
    """
    Class that holds 2D Coordinate logic for robot to follow with RFID stickers.
    Has to be initialized with a text file of a map and current coordinates of robot on startup with the form (y, x)
    If a given tile is traversible, it is stored as a "1".
    If it has an RFID sticker associated with it, it is stored as a letter from "a" to "z"
    Otherwise, it is stored as a "0".

    Map file format: 
    "a" to "z" - RFID sticker
    "#" - Traversible tile
    "-" - Empty tile
    """
    def __init__ (self, mapfile, start):
        
        # Interpret map file
        with open(mapfile) as file:
            data = file.read().splitlines()
            self.height = len(data)
            self.width = max(len(line) for line in data)

            # Loop over rows and columns
            self.coordinates = []
            for i in range(self.height):
                row = []
                for j in range(self.width):
                    if j >= len(data[i]): # If row shorter than longest row
                        row.append("0")
                    elif data[i][j] == "#": # If possible paths encountered
                        row.append("1")
                    elif data[i][j].isalpha(): # If junction with sticker encountered
                        row.append(data[i][j])
                    else:
                        row.append("0") # Everything else
                self.coordinates.append(row)

        # Set current coords of robot on initialization
        self.set_current_coords(start)

    def print(self):
        """Prints current map assignment to terminal."""
        for i in range(self.height):
            for j in range(self.width):
                letter = self.coordinates[i][j]
                if letter != "0":
                    if letter.isalpha():
                        print(letter, end="")
                    else:
                        print("#", end="")
                else:
                    print(" ", end="")
            print()

    def connections(self, coords):
        """
        Returns a set of connections to any given tile with the input coordinates (y, x).
        Each element in the set is a set itself, consisting of two elements: (coordinates of neighbor, action required to reach it).
        """
        i, j = coords
        connections = set()
        if i >= 1:
            if self.coordinates[i - 1][j] != "0":
                connections.add(((i - 1, j), "up"))
        if i <= (self.height - 2):
            if self.coordinates[i + 1][j] != "0":
                connections.add(((i + 1, j), "down"))
        if j >= 1:
            if self.coordinates[i][j - 1] != "0":
                connections.add(((i, j - 1), "left"))
        if j <= (self.width - 2):
            if self.coordinates[i][j + 1] != "0":
                connections.add(((i, j + 1), "right"))

        return connections

    def get_coords_of_sticker(self, sticker):
        """Returns coordinates of given sticker based on its letter representation, returns None if invalid sticker"""
        for y in range(self.height):
            for x in range(self.width):
                if self.coordinates[y][x] == sticker:
                    return (y, x) 
        
        return None

    def is_sticker(self, coords):
        """
        Checks whether a given tile with the formula (y, x) has an RFID sticker associated with it.
        Returns sticker letter from "a" to "z" if it does, False if it does not.
        """
        if self.is_valid_tile(coords):
            y, x = coords
            letter = self.coordinates[y][x]
            if letter.isalpha():
                return letter

        return None

    def set_current_coords(self, coords):
        """Sets given coordinates to be current stored coordinates in map class"""
        if self.is_valid_tile(coords):
            self.current = coords
            return
        else:
            raise Exception("Coordinates outside of map limits")

    def is_valid_tile(self, coords):
        """Checks whether input tile is traversible. Returns True if it is, False if it is out of bounds."""
        y, x = coords

        # NOTE: self.height and self.width are a number 1 larger than the available indexes in the coordinate list
        if y <= (self.height - 1) and x <= (self.width - 1) and self.coordinates[y][x] != "0":
            return True
        else:
            return False

    def find_path(self, sticker):
        """
        Finds the shortest path from current node to an end sticker by the use of a BFS pathfinding algorithm.
        Returns an ordered list of elements with the format [coordinates, movement direction reqired to reach tile].
        """
        # Check whether desired end sticker exists
        end = self.get_coords_of_sticker(sticker)
        if end is None:
            raise Exception(f"'{sticker}' is not a valid sticker")
            
        # Create a start node and add it to queue for inspection
        start = Node(state = self.current, parent = None, action = None)
        queue = NodeQueue()
        queue.add(start)
        
        # Initialize empty set of explored tiles
        explored = set()

        # Loop runs until either solution is found, or all options were explored
        while True:

            if queue.empty():
                return None
            
            # Pick oldest node in queue, set it to explored and get its neighboring nodes
            node = queue.get()
            explored.add(node)
            neighbors = self.connections(node.state)

            # Unpack all neighbors
            for coords, direction in neighbors:

                # If neighboring node is the requested destination
                if coords == end:
                    
                    # Initialize empty lists to store solution
                    path = []
                    coordinateList = []
                    moveList = []

                    # Add the newest node (the goal) to the solution first
                    coordinateList.append(coords)
                    moveList.append(direction)

                    # Start going back parent-by-parent, appending each state and move to the lists
                    while node.parent != None:
                        coordinateList.append(node.state)
                        moveList.append(node.action)
                        node = node.parent
                    
                    # Reverse list of solutions so they go from beginning-to-end instead of from end-to-beginning
                    coordinateList.reverse()
                    moveList.reverse()

                    # Add list of coordinates and moves to solution and return it
                    for i in range(len(coordinateList)):
                        path.append([])
                        path[i] = [coordinateList[i], moveList[i]]
                    return path

                # If neighboring node is not in queue yet, and is unexplored, add it to queue
                elif not queue.contains_state(coords) and coords not in explored:
                    child = Node(state = coords, parent = node, action = direction)
                    queue.add(child)

samplemap = Map("map1.txt", (2,5))
print(samplemap.find_path("g"))