import datetime
import pygame
import random


class MineSweeper():
    def __init__(self, width=30, height=16, bombCount=99):
        self.width = width
        self.height = height
        self.bombCount = bombCount

        # ALGORITHM
        self.grid = None
        self.clickedGrid = [
            [False for x in range(self.width)]
            for x in range(self.height)
        ]
        self.first_click = True
        self.gameFailed = False
        self.gameWon = False
        self.bombLeft = self.bombCount
        self.timer = 0
        self.startTime = None

        # UI/PYGAME
        self.margin = 10
        self.topBar = 32
        self.tileSize = 16
        self.border = 1
        self.faceSize = 26
        self.windowWidth = self.width * self.tileSize + self.margin * 2
        self.windowHeight = self.height * self.tileSize + self.margin * 3 + self.topBar
        self.windowSize = (self.windowWidth, self.windowHeight)
        self.window = pygame.display.set_mode(self.windowSize, 0, 32)
        self.clock = pygame.time.Clock()
        pygame.display.set_caption('Minesweeper')
        self.imageFolder = "img/"
        pygame.display.set_icon(
            pygame.image.load(self.imageFolder + "ico.png")
        )

        # IMAGES
        self.undiscoveredTile = self.imageFolder + "undiscovered_tile.png"
        self.discoveredTile = self.imageFolder + "discovered_tile.png"
        self.flag = self.imageFolder + "flag.png"
        self.bomb = self.imageFolder + "bomb.png"
        self.flagedBomb = self.imageFolder + "flaged_bomb.png"
        self.explodedBomb = self.imageFolder + "bomb_exploded.png"
        self.question = self.imageFolder + "question.png"
        self.background = self.imageFolder + "background.png"
        # tile numbers
        self.numberImageFolder = self.imageFolder + "tiles/"
        self.number = [0 for x in range(11)]
        for x in range(len(self.number)):
            self.number[x] = self.numberImageFolder + str(x) + ".png"
        # face images
        self.faceImageFolder = self.imageFolder + "faces/"
        self.faceHappy = self.faceImageFolder + "happy.png"
        self.faceDeath = self.faceImageFolder + "death.png"
        self.faceCool = self.faceImageFolder + "cool.png"
        # timer/flag counter images
        self.counterImageFolder = self.imageFolder + "counter/"
        self.counter = [0 for x in range(11)]
        for x in range(len(self.counter)):
            self.counter[x] = self.counterImageFolder + str(x) + ".png"

        # COLORS
        self.backgroundColor = (180, 180, 180)

    def game_loop(self):
        """
        Game loop with different actions based on user input type (right-left click)
        and click position (top-bar/grid)
        """
        pygame.init()
        self.init_display()
        while True:
            pygame.display.update()
            self.clock.tick(60)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    quit()
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    pos = pygame.mouse.get_pos()

                    # if the click is on the grid
                    if self.margin < pos[0] < self.windowWidth - self.margin and \
                         self.margin * 2 + self.topBar < pos[1] < self.windowHeight - self.margin and \
                         self.gameFailed is False and \
                         self.gameWon is False:
                        
                        x = int((pos[1] - self.margin * 2 - self.topBar) / self.tileSize)
                        y = int((pos[0] - self.margin) / self.tileSize)

                        if event.button == 1:
                            self.click_register(x, y)
                            if self.gameFailed is False:
                                self.display_tiles()
                        elif event.button == 3:
                            self.right_click_register(x, y)

                        self.win_test()

                    # if the click is on the top bar
                    elif self.margin < pos[0] < self.windowWidth - self.margin and \
                            self.margin < pos[1] < self.topBar + self.margin:

                        if self.windowWidth / 2 - self.faceSize / 2 < pos[0] < self.windowWidth / 2 - self.faceSize / 2 + self.faceSize and \
                             self.margin + self.topBar / 2 - self.faceSize / 2 < pos[1] < self.margin + self.topBar / 2 - self.faceSize / 2 + self.faceSize:

                            self.__init__(
                                width=self.width,
                                height=self.height,
                                bombCount=self.bombCount
                            )
                            self.game_loop()
                    self.display_top_bar()

            self.updateTimer()

    def init_display(self):
        """
        Initialize the display by updating background, tiles and top bar
        """
        self.display_background()
        self.display_tiles()
        self.display_top_bar()

    def display_background(self):
        """
        Update the background image
        """
        self.window.blit(
            pygame.image.load(self.background),
            (0, 0)
        )

    def display_face(self):
        """
        Update the face on the top bar
        """
        if self.gameFailed:
            face = self.faceDeath
        elif self.gameWon:
            face = self.faceCool
        else:
            face = self.faceHappy

        self.window.blit(
            pygame.image.load(face),
            (self.windowWidth / 2 - self.faceSize / 2,
             self.margin + self.topBar / 2 - self.faceSize / 2)
        )

    def display_bomb_counter(self):
        """
        Update the bomb counter
        """
        c = "000" + str(self.bombLeft)
        for x in range(3):
            n = c[-(3-x)]
            if n == '-':
                n = 10
            self.display_counter_digit(
                self.margin + 6 + 13 * x,
                self.margin + 4,
                n
            )

    def display_timer_counter(self):
        """
        Update the timer displayed
        """
        c = "000" + str(self.timer)
        for x in range(3):
            self.display_counter_digit(
                self.windowWidth - (self.margin + 6 + 13 * (3-x)),
                self.margin + 4,
                c[-(3-x)]
            )

    def display_counter_digit(self, x, y, digit):
        """
        Update a single digit of either the bomb counter or the timer
        """
        self.window.blit(
            pygame.image.load(self.counter[int(digit)]),
            (x, y)
        )

    def display_top_bar(self):
        """
        Update the top bar, with timer, bomb counter and face
        """
        # reset the top bar
        self.window.fill(
            self.backgroundColor,
            pygame.Rect((
                (self.margin, self.margin),
                (self.windowWidth - self.margin * 2, self.topBar)
            ))
        )

        self.display_face()
        self.display_bomb_counter()
        self.display_timer_counter()

    def updateTimer(self):
        """
        Update the timer displayed to the player
        """
        if self.startTime is not None and self.gameFailed is False and \
             self.gameWon is False:
            self.timer = int(
                (datetime.datetime.now() - self.startTime).total_seconds()
            )
        self.display_timer_counter()

    def tilePosition(self, x, y):
        """
        convert a grid position into gui position of a tile
        """
        gui_x = self.margin + self.tileSize * x
        gui_y = self.margin * 2 + self.tileSize * y + self.topBar
        return gui_x, gui_y

    def display_tiles(self):
        """
        Update the display of every tiles on the grid
        """
        for x in range(self.width):
            for y in range(self.height):
                self.display_one_tile(x, y)

    def display_one_tile(self, x, y):
        """
        Update the display of a single tile on the grid
        """
        if self.clickedGrid[y][x] is True:
            if isinstance(self.grid[y][x], int):
                # number tile
                self.window.blit(
                    pygame.image.load(self.number[self.grid[y][x]]),
                    self.tilePosition(x, y)
                )

            else:
                # empty tile
                self.window.blit(
                    pygame.image.load(self.discoveredTile),
                    self.tilePosition(x, y)
                )

        elif self.clickedGrid[y][x] == "F":
            # flagged tile
            self.window.blit(
                pygame.image.load(self.flag),
                self.tilePosition(x, y)
            )

        elif self.clickedGrid[y][x] == "?":
            # question tile
            self.window.blit(
                pygame.image.load(self.question),
                self.tilePosition(x, y)
            )

        else:
            # undiscovered tile
            self.window.blit(
                pygame.image.load(self.undiscoveredTile),
                self.tilePosition(x, y)
            )

    def show_bombs(self, exploded_x, exploded_y):
        """
        At the end of the game every bombs are shown to the player
        """
        for x in range(self.width):
            for y in range(self.height):
                if self.grid[y][x] == '*':
                    if self.clickedGrid[y][x] == 'F' or \
                         self.clickedGrid[y][x] == '?':
                        self.window.blit(
                            pygame.image.load(self.flagedBomb),
                            self.tilePosition(x, y)
                        )
                    else:
                        self.window.blit(
                            pygame.image.load(self.bomb),
                            self.tilePosition(x, y)
                        )

        self.window.blit(
            pygame.image.load(self.explodedBomb),
            self.tilePosition(exploded_y, exploded_x)
        )

    def click_register(self, x, y):
        """
        When a user left click on the tile at position x, y
        """
        # Bombs are placed after the first click, preventing the
        # player from clicking on a bomb at first click
        if self.first_click:
            self.first_click = False
            self.generateGrid()
            while self.grid[x][y] != ' ':
                self.generateGrid()
            self.startTime = datetime.datetime.now()

        if self.clickedGrid[x][y] is False:
            self.clickedGrid[x][y] = True
            if self.grid[x][y] == '*':
                self.gameFailed = True
                self.show_bombs(x, y)
            elif self.grid[x][y] == ' ':
                self.discover_tiles(x, y)

    def right_click_register(self, x, y):
        """
        When a user right click on the tile at position x, y
        """
        if self.clickedGrid[x][y] == 'F':
            self.clickedGrid[x][y] = '?'
            self.bombLeft += 1
        elif self.clickedGrid[x][y] == '?':
            self.clickedGrid[x][y] = False
        elif self.clickedGrid[x][y] is False:
            self.clickedGrid[x][y] = 'F'
            self.bombLeft -= 1
        self.display_one_tile(y, x)

    def discover_tiles(self, x, y):
        """
        Will pass on all 8 adjacent tiles and
        if they are either number or empty it will be recursive
        """
        for n in range(-1, 2):
            for m in range(-1, 2):
                u = x + n
                v = y + m
                if 0 <= u <= (self.height - 1) and 0 <= v <= (self.width - 1):
                    if self.grid[u][v] == ' ' or isinstance(self.grid[u][v], int):
                        self.click_register(u, v)

    def win_test(self):
        """
        Test if player has won the game or not
        and update self.gameWon
        """
        if self.grid is not None:
            for x in range(self.width):
                for y in range(self.height):
                    if (self.grid[y][x] == '*' and self.clickedGrid[y][x] != 'F') or \
                         (self.clickedGrid[y][x] == 'F' and self.grid[y][x] != '*') or \
                         (self.clickedGrid[y][x] is False and self.grid[y][x] != '*'):
                        return None
            self.gameWon = True

    def generateGrid(self):
        """
        Generate a random grid filled with bomb and with numbers
        """
        self.grid = [
            [' ' for x in range(self.width)]
            for x in range(self.height)
        ]
        self.placeBombs()
        self.attributeValue()

    def placeBombs(self):
        """
        Randomly place bombs on the grid
        """
        bombCount = 0
        while bombCount != self.bombCount:
            x = random.randint(0, self.height - 1)
            y = random.randint(0, self.width - 1)
            if self.grid[x][y] != '*':
                self.grid[x][y] = '*'
                bombCount += 1

    def attributeValue(self):
        """
        Place numbers on the grid based on the number of bomb in
        the 8 adjacents tiles
        """
        for x in range(len(self.grid)):
            for y in range(len(self.grid[x])):
                if self.grid[x][y] != '*':
                    c = 0
                    for n in range(-1, 2):
                        for m in range(-1, 2):
                            u = x+n
                            v = y+m
                            if 0 <= u and u <= (self.height - 1) and \
                                 0 <= v and v <= (self.width - 1):
                                if self.grid[u][v] == '*':
                                    c += 1
                    if c > 0:
                        self.grid[x][y] = c
                    else:
                        self.grid[x][y] = ' '


if __name__ == "__main__":
    MineSweeper().game_loop()
