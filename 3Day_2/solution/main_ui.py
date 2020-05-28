
# Coded by Soumonos Mukherjee


import arcade
from pathRouter import Astar
from constants import doorSprites, keySprites, keyDoorPairs

# Constants
fPath="../Maze2.txt"

# Load File 
def loadMaze(fPath):
    grid = []
    lines = open(fPath).read().splitlines()
    for line in lines:
        grid.append(line.split(" "))
    return grid

grid = loadMaze(fPath)

# Matrix dimensions
ROW_COUNT = len(grid)
COLUMN_COUNT = len(grid[0])

# Size of matrix based on sprite size
WIDTH = 50
HEIGHT = 50
MARGIN = 4

# Screen constants
SCREEN_WIDTH = (WIDTH + MARGIN) * COLUMN_COUNT + MARGIN
SCREEN_HEIGHT = (HEIGHT + MARGIN) * ROW_COUNT + MARGIN
SCREEN_TITLE = "MazeBot"


class MazeBot(arcade.Window):

    def __init__(self, width, height, title):

        super().__init__(width, height, title)
        self.grid = loadMaze(fPath)
        self.gridSize = len(self.grid)
        self.walls = []
        self.keys = []
        self.doors = []
        self.obstacle_loc = {}
        self.pinkCells = []

        self.openDoors= []
        self.directRoute = []
        self.keyLoc = []
        self.position = 0

        # Initialize Sprites
        self.wall_list = arcade.SpriteList()
        self.path_list = arcade.SpriteList()
        self.ghost_list = arcade.SpriteList()
        self.obstacle_list = arcade.SpriteList()
        self.reward_coord = arcade.SpriteList()
        self.pinkCells = arcade.SpriteList()
        
        # Player Sprite
        self.player_sprite = None

        # Physics engine for movement
        self.physics_engine = None

    def setup(self):

        pink_cell = []
        # Draw the grid
        for row in range(self.gridSize):
            for column in range(self.gridSize):
                
                cell = self.grid[row][column]
                cell_loc = (row,column)

                if str.isdigit(cell):
                    # Handle for Path, Walls and ghosts
                    if cell == '1':
                        self.walls.append(cell_loc)
                        self.addSprite("../sprites/block.png", self.wall_list, column, row)
                    elif cell == '0':
                        self.addSprite("../sprites/path.png", self.path_list, column, row)
                    else:
                        # Handle for ghost 
                        tempSprite = self.createSprite("../sprites/ghost.png",column, row)
                        self.ghost_list.append(tempSprite)
                        self.wall_list.append(tempSprite)
                        pink_cell = pink_cell + [(int(cell),cell_loc)]
                        # Generate Pink Cells
                        ## Get locations to valid paths in n spaces of ghost 
                        ## Add location to walls and walls_list
                        self.walls.append(cell_loc)
                else:

                    # Add location as valid path
                    self.addSprite("../sprites/path.png", self.path_list, column, row)

                    # Handle for reward and player
                    if cell == 'e':
                        self.end = cell_loc
                        self.addSprite("../sprites/reward.png", self.reward_coord, column, row)
                        
                    elif cell == 's':
                        self.start = cell_loc
                        self.player_sprite = self.createSprite("../sprites/pacman.png", column, row)

                    else:
                        self.obstacle_loc[cell] = cell_loc
                        # Handle doors and Keys
                        if cell in doorSprites:
                            self.doors.append(cell_loc)
                            tempSprite = self.createSprite(doorSprites[cell], column, row)
                        else:
                            self.keys.append(cell_loc)
                            tempSprite = self.createSprite(keySprites[cell], column, row)
                        self.obstacle_list.append(tempSprite)

        # self.getPinkCells(pink_cell)

        self.path_list.append(self.player_sprite)
        # Enable animation and collision physics
        self.physics_engine = arcade.PhysicsEngineSimple(self.player_sprite, self.wall_list)
        # Get Path and animate it
        targetsOnPath = self.findPath(self.start,self.end)
        self.path = self.generateCompletePath(targetsOnPath)
        print("Final Path :",self.path)

    def getPinkCells(self,pink_list):
        pinkPath = []
        for infectCount,location in pink_list:
            grid_outline = []
            for i in range(1,infectCount):
                # Generates x, y and diagonals
                grid_outline.append((location[0] - i, location[1]))
                grid_outline.append((location[0] + i, location[1]))
                grid_outline.append((location[0], location[1] - i))
                grid_outline.append((location[0], location[1] + i))
                grid_outline.append((location[0] - i, location[1] - i))
                grid_outline.append((location[0] + i, location[1] + i))
                grid_outline.append((location[0] - i, location[1] + i))
                grid_outline.append((location[0] + i, location[1] - i))
                # print(grid_outline)
            # Remove walls and objects from the list
            possible_path = [ loc for loc in grid_outline if loc not in self.walls and loc not in self.obstacle_loc.values()]
            
            # Generate paths and remoce those that are not in range
            # for target in possible_path:
            #     print("move",location,target)
            #     routeMarker = self.findPath(location,target)
            #     path = self.generateCompletePath(routeMarker)
            #     if len(path) <= infectCount:
            #         pinkPath.append(path)
        for location in possible_path:
            self.addSprite("../sprites/pink_cell.png", self.pinkCells, location[1], location[0])


    def on_draw(self):
        arcade.start_render()
        # Draw the Sprites
        self.wall_list.draw()
        self.path_list.draw()
        self.pinkCells.draw()
        self.ghost_list.draw()
        self.reward_coord.draw()
        self.obstacle_list.draw()
        self.player_sprite.draw()
        
    def addSprite(self,spritePath,spriteObj, column, row):
        sprite = self.createSprite(spritePath, column, row)
        spriteObj.append(sprite)

    def createSprite(self, spritePath, row, column):
        sprite = arcade.Sprite(spritePath)
        sprite.center_x = (MARGIN + HEIGHT) * row + MARGIN + HEIGHT // 2
        sprite.center_y = (MARGIN + WIDTH) * column + MARGIN + WIDTH // 2
        return sprite

    def on_update(self, delta_time: float = 2):
        self.physics_engine.update()
        hit_list = arcade.check_for_collision_with_list(self.player_sprite, self.obstacle_list)
        completionStat = arcade.check_for_collision_with_list(self.player_sprite, self.reward_coord)
        
        # Animate character on the generated path
        if self.position < len(self.path):
            self.animatePath(self.path,self.position)
            self.position = self.position + 1

        # Remove obstacle sprites on collision
        for obj in hit_list or completionStat:
            obj.remove_from_sprite_lists()
        
        arcade.pause(0.2)

    def findPath(self, start, end):
        directPath = self.findPathBetween(start,end)
        route = [start, end]
        # Check if doors exist on path
        obstaclesOnPath = list(set(directPath).intersection(self.doors))
        if len(obstaclesOnPath) != 0:
            # print(route, "has obstacles : ", obstaclesOnPath)
            # For each door, find key and get correspondig routes for each object
            for obstacle in obstaclesOnPath:
                if obstacle in self.doors and obstacle not in self.openDoors:
                    # Get the coord of corresponding Key
                    keyForObstacle = keyDoorPairs[grid[obstacle[0]][obstacle[1]]]
                    key_Loc = self.obstacle_loc[keyForObstacle]
                    # Set route
                    keyPath = self.findPath(start, key_Loc)
                    route = route[:-1] + keyPath[1:] + route[-1:]
                    # Mark the door as unlocked
                    self.openDoors.append(obstacle)

        # print("Route Landmarks:",route)
        return route

    def generateCompletePath(self,route):
        path = route[0:1] # All routes always have a start    
        for target in route[1:]:
            path = path + self.findPathBetween(path[-1],target)
        return path

    def animatePath(self,path, location):
        current = path[location]
        self.player_sprite.center_y = (MARGIN + HEIGHT) * current[0] + MARGIN + HEIGHT // 2
        self.player_sprite.center_x = (MARGIN + WIDTH) * current[1] + MARGIN + WIDTH // 2 
        self.player_sprite.update()
            
    def findPathBetween(self, start, end):
        a= Astar()
        a.maze(ROW_COUNT, COLUMN_COUNT, tuple(self.walls), start, end) 
        a.solve_maze()
        return a.find_path() 

def main():
    maze = MazeBot(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
    maze.setup()
    arcade.run()


if __name__ == "__main__":
    main()
