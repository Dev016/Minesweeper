import itertools
import random


class Minesweeper():
    """
    Minesweeper game representation
    """

    def __init__(self, height=8, width=8, mines=8):

        # Set initial width, height, and number of mines
        self.height = height
        self.width = width
        self.mines = set()

        # Initialize an empty field with no mines
        self.board = []
        for i in range(self.height):
            row = []
            for j in range(self.width):
                row.append(False)
            self.board.append(row)

        # Add mines randomly
        while len(self.mines) != mines:
            i = random.randrange(height)
            j = random.randrange(width)
            if not self.board[i][j]:
                self.mines.add((i, j))
                self.board[i][j] = True

        # At first, player has found no mines
        self.mines_found = set()

    def print(self):
        """
        Prints a text-based representation
        of where mines are located.
        """
        for i in range(self.height):
            print("--" * self.width + "-")
            for j in range(self.width):
                if self.board[i][j]:
                    print("|X", end="")
                else:
                    print("| ", end="")
            print("|")
        print("--" * self.width + "-")

    def is_mine(self, cell):
        i, j = cell
        return self.board[i][j]

    def nearby_mines(self, cell):
        """
        Returns the number of mines that are
        within one row and column of a given cell,
        not including the cell itself.
        """

        # Keep count of nearby mines
        count = 0

        # Loop over all cells within one row and column
        for i in range(cell[0] - 1, cell[0] + 2):
            for j in range(cell[1] - 1, cell[1] + 2):

                # Ignore the cell itself
                if (i, j) == cell:
                    continue

                # Update count if cell in bounds and is mine
                if 0 <= i < self.height and 0 <= j < self.width:
                    if self.board[i][j]:
                        count += 1

        return count

    def won(self):
        """
        Checks if all mines have been flagged.
        """
        return self.mines_found == self.mines


class Sentence():
    """
    Logical statement about a Minesweeper game
    A sentence consists of a set of board cells,
    and a count of the number of those cells which are mines.
    """

    def __init__(self, cells, count):
        self.cells = set(cells)
        self.count = count

    def __eq__(self, other):
        return self.cells == other.cells and self.count == other.count

    def __str__(self):
        return f"{self.cells} = {self.count}"

    def known_mines(self):
        """
        Returns the set of all cells in self.cells known to be mines.
        """
        known_mines = set()
        for cell in self.cells:
            if cell in MinesweeperAI.mines:
                known_mines.add(cell)
        return known_mines

    def known_safes(self):
        """
        Returns the set of all cells in self.cells known to be safe.
        """
        known_safes = set()
        for cell in self.cells:
            if cell in MinesweeperAI.safes:
                known_safes.add(cell)
        return known_safes

        
    def mark_mine(self, cell):
        """
        Updates internal knowledge representation given the fact that
        a cell is known to be a mine.
        """
        if cell in self.cells:
            self.cells.remove(cell)
            self.count -= 1
        

    def mark_safe(self, cell):
        """
        Updates internal knowledge representation given the fact that
        a cell is known to be safe.
        """
        if cell in self.cells:
            self.cells.remove(cell)
        

class MinesweeperAI():
    """
    Minesweeper game player
    """

    def __init__(self, height=8, width=8):

        # Set initial height and width
        self.height = height
        self.width = width

        # Keep track of which cells have been clicked on
        self.moves_made = set()

        # Keep track of cells known to be safe or mines
        self.mines = set()
        self.safes = set()

        # List of sentences about the game known to be true
        self.knowledge = []

    def mark_mine(self, cell):
        """
        Marks a cell as a mine, and updates all knowledge
        to mark that cell as a mine as well.
        """
        self.mines.add(cell)
        for sentence in self.knowledge:
            sentence.mark_mine(cell)

    def mark_safe(self, cell):
        """
        Marks a cell as safe, and updates all knowledge
        to mark that cell as safe as well.
        """
        self.safes.add(cell)
        for sentence in self.knowledge:
            sentence.mark_safe(cell)

    def add_knowledge(self, cell, count):
        """
        Called when the Minesweeper board tells us, for a given
        safe cell, how many neighboring cells have mines in them.
        """
        self.moves_made.add(cell)
        self.mark_safe(cell)
        neighbours = set()
        nearby_mines = 0
        for i in range(cell[0]-1, cell[0]+2, 1):
            for j in range(cell[1]-1, cell[1]+2, 1):
                if 0 <= i < 8 and 0 <= j < 8:
                    neighbour = (i, j)
                    if neighbour in self.mines:
                        nearby_mines += 1
                    if neighbour not in self.mines and neighbour not in self.safes:
                        neighbours.add(neighbour)
        self.knowledge.append(Sentence(neighbours, count - nearby_mines))
        while True:
            flag = True
            for sentence in self.knowledge:
                if len(sentence.cells) == sentence.count and sentence.count != 0:
                    cell_list = []
                    for cell in sentence.cells:
                        cell_list.append(cell)
                    
                    for cell in cell_list:
                        self.mark_mine(cell)

                    flag = False
                if sentence.count == 0 and len(sentence.cells) != 0:
                    cell_list = []
                    for cell in sentence.cells:
                        cell_list.append(cell)
                    for cell in cell_list:
                        self.mark_safe(cell)
                    flag = False
            for sentence in self.knowledge:
                if len(sentence.cells) == 0:
                    self.knowledge.remove(sentence)
            for i in self.knowledge:
                for j in self.knowledge:
                    if i.cells.issubset(j.cells):
                        remaining = j.cells.difference(i.cells)
                        if len(remaining) != 0:
                            new = Sentence(remaining, j.count - i.count)
                            if new not in self.knowledge:
                                self.knowledge.append(new)
                                flag = False
            if flag == True:
                break
       
    def make_safe_move(self):
        """
        Returns a safe cell to choose on the Minesweeper board.
        """
        for cell in self.safes:
            if cell not in self.moves_made:
                return cell
        return None

    def make_random_move(self):
        """
        Returns a move to make on the Minesweeper board.
        """
        for i in range(8):
            for j in range(8):
                cell = (i, j)
                if cell not in self.moves_made and cell not in self.mines:
                    return cell
            return None
