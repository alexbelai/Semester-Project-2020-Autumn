class Map():
    """
    Class that holds 2D Coordinate logic for robot to follow with RFID stickers.
    """
    def __init__ (self, mapfile):
        
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
        Returns a set of connections to any given tile with the formula (height, width).
        """
        i, j = coords
        connections = set()
        if i >= 1:
            if self.coordinates[i - 1][j] != "0":
                connections.add((i - 1, j))
        if i <= (self.height - 1):
            if self.coordinates[i + 1][j] != "0":
                connections.add((i + 1, j))
        if j >= 1:
            if self.coordinates[i][j - 1] != "0":
                connections.add((i, j - 1))
        if j <= (self.width - 1):
            if self.coordinates[i][j + 1] != "0":
                connections.add((i, j + 1))

        return connections

    def junction(self, coords):
        """
        Checks whether a given tile with the formula (height, width) has an RFID sticker associated with it.
        Returns #ID sticker if it does, False if it does not.
        """
        i, j = coords
        letter = self.coordinates[i][j]
        if letter != "0":
            if letter.isalpha():
                return letter

        return False

structure = Map("map1.txt")
structure.print()
neighbors = structure.connections((1, 3))
print(neighbors)
