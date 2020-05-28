# Team 10
# Vasanth MOHAN
# Soumonos Mukherjee
# Gaurav Nepal

import heapq

class Cell(object):
    def __init__(self,x,y,accesible):
        self.accesible= accesible
        self.x= x
        self.y= y
        self.parent= None
        self.cost= 0
        self.hcost=0
        self.agg= 0
    def __lt__(self, other):
        return self.agg < other.agg
        
class Astar(object):
    def __init__(self):
        self.open=[]
        heapq.heapify(self.open)
        self.traversed= set()
        self.cells=[]
        self.height= None
        self.width= None
             
    def maze(self,height,width,obstacles,start,goal):
        self.maze_height= height
        self.maze_width= width
        for x in range(self.maze_width):
            for y in range(self.maze_height):
                if (x,y) in obstacles:
                    accesible=False
                else:
                    accesible= True
                self.cells.append(Cell(x,y,accesible))
        self.start= self.get_cells(*start)
        self.goal= self.get_cells(*goal)
        
    def heuristics(self,cell):
        return 10* (abs(self.goal.x- cell.x)+abs(self.goal.y-cell.y))
    def get_cells(self,x,y):
        return self.cells[x*self.maze_height+y]
    def neighbors (self,cell):
       # print(cell)
        cells=[]
        if cell.x < self.maze_width-1:
            cells.append(self.get_cells(cell.x+1,cell.y))
        if cell.x > 0:
            cells.append(self.get_cells(cell.x-1,cell.y))
        if cell.y > 0:
            cells.append(self.get_cells(cell.x,cell.y-1))
        if cell.y < self.maze_height-1:
            cells.append(self.get_cells(cell.x,cell.y+1))
        return cells
    
    def find_path(self):
        cell= self.goal
        path= [(cell.x,cell.y)]
        while True:
            cell=cell.parent
            path.append((cell.x,cell.y))
            if cell.parent is self.start:
                break
        path.append((self.start.x,self.start.y))
        path.reverse()
        return path
    
    def step_update(self, neighbor, cell):
        neighbor.cost= cell.cost+10
        neighbor.hcost= self.heuristics(neighbor)
        neighbor.parent=cell
        neighbor.agg= neighbor.cost+neighbor.hcost

    def solve_maze(self):
        heapq.heappush(self.open,(self.start.agg,self.start))
        while len(self.open):
            agg, cell= heapq.heappop(self.open)
            self.traversed.add(cell)
            if cell is self.goal:
                return self.find_path()
            neighbor_cells= self.neighbors(cell)
            for i in neighbor_cells:
                if i.accesible and i not in self.traversed:
                    if (i.agg,i) in self.open:
                        if i.cost > cell.cost+ 10:
                            self.step_update(i,cell)
                    else:
                        self.step_update(i,cell)
                        heapq.heappush(self.open, (i.agg,i))

## Test ##
# obstacles1=  ((0, 5), (1, 0), (1, 1), (1, 5), (2, 3),(3, 1), (3, 2), (3, 5), (4, 1), (4, 4), (5, 1)) 
# a= Astar()
# a.maze(6, 6, obstacles1, (0, 0), (5, 5)) 
# a.solve_maze()
# path= a.find_path()  
# print(path)