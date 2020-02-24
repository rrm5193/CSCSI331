import queue
from PIL import Image, ImageDraw
import enum
import sys
import math


# class of enums for terrain rgb values
class Terrain(enum.Enum):
    Open_Land = (248, 148, 18, 255)
    Rough_Meadow = (255, 192, 0, 255)
    Easy_Forest = (255, 255, 255, 255)
    Slow_Forest = (2, 208, 60, 255)
    Walk_Forest = (2, 136, 40, 255)
    Imapss_Veg = (5, 73, 24, 255)
    Lak_Swmp_Mrsh = (0, 0, 255, 255)
    Paved_Road = (71, 51, 3, 255)
    Foot_path = (0, 0, 0, 255)
    Out_of_Bounds = (205, 0, 101, 255)
    Ice = (217, 251, 255, 255)
    Mud = (173, 127, 0, 255)
    Leaf_Trail = (122, 122, 122, 255)
    Leaf_Road = (65, 65, 65, 255)


# class of enums for constants used in the program
class Constants(enum.Enum):
    xScale = 10.29
    yScale = 7.55
    IceLimit = 7
    MudLimit = 15


# class Node for A* and BFS searching
class Node:

    def __init__(self, parent=None, position=None):
        self.parent = parent
        self.position = position
        self.g = 0
        self.h = 0
        self.f = 0
        self.distance = 0

    def __eq__(self, other):
        return self.position == other.position

    def __lt__(self, other):
        return self.f < other.f


# function to return the effect the terrain has on movement
def check_modifier(rgb_color):
    # Open Land - 90% movement
    if rgb_color == Terrain.Open_Land.value:
        return 0.9
    # moving shrubbery is long - 60%
    elif rgb_color == Terrain.Rough_Meadow.value:
        return 0.6
    # Need to watch for branches - 75%
    elif rgb_color == Terrain.Easy_Forest.value:
        return 0.75
    # Need to watch for more branches - 65%
    elif rgb_color == Terrain.Slow_Forest.value:
        return 0.65
    # It's walking time - 55%
    elif rgb_color == Terrain.Walk_Forest.value:
        return 0.55
    # you literally can't get through this - 0%
    elif rgb_color == Terrain.Imapss_Veg.value:
        return 0.0
    # Not ideal but can swim - 30%
    elif rgb_color == Terrain.Lak_Swmp_Mrsh.value:
        return 0.3
    # Paved road - 100% optimal movement
    elif rgb_color == Terrain.Paved_Road.value:
        return 1.0
    # it's pretty good terrain - 90%
    elif rgb_color == Terrain.Foot_path.value:
        return 0.9
    # you can run in this but like you're trying not to fall - 45%
    elif rgb_color == Terrain.Ice.value:
        return 0.45
    # same as ice
    elif rgb_color == Terrain.Mud.value:
        return 0.45
    # there's annoying leaves on the road - 90%
    elif rgb_color == Terrain.Leaf_Road.value:
        return 0.9
    # there's annoying leaves on the footpath - 80%
    elif rgb_color == Terrain.Leaf_Trail.value:
        return 0.8
    # out of bounds - 0%
    else:
        return 0.0


# function to store elevation in a 2d array
# stored in YX orientation
def store_elevation(fp):
    wfile = open(fp, 'r')
    elevation = list()
    for line in wfile:
        x = list()
        word = line[:-1]
        value = word.split()
        for i in value:
            x.append(float(i))
        elevation.append(x)
    return elevation


# function to store the points to visit
def store_waypoints(fp):
    wfile = open(fp, 'r')
    points = list()
    for line in wfile:
        word = line[:-1]
        values = word.split()
        x = int(values[0])
        y = int(values[1])
        points.append((x,y))
    return points


# function to add altercations to the map based on season
def seasons(image, season, elevation):
    # no change for summer
    if season == "summer":
        return image

    # draw module for the image
    draw = ImageDraw.Draw(image)

    # 2d array of visited cells for BFS
    visited = list()
    for i in range(395):
        temp = list()
        for ii in range(500):
            temp.append(False)
        visited.append(temp)

    # queue for BFS
    reached_nodes = queue.Queue()

    # check every pixel
    for x in range(395):
        for y in range(500):
            # if encountered, skip
            if visited[x][y]:
                continue

            rgb = image.getpixel((x, y))

            # winter BFS, search for land and find all water within 7 units
            if season == "winter":
                if not check_modifier(rgb) == 0.3:
                    new_node = Node(None, (x, y))
                    new_node.distance = 0
                    reached_nodes.put(new_node)
                    visited[x][y] = True
                    # Winter BFS
                    while not reached_nodes.empty():
                        s = reached_nodes.get()
                        # check all possible children
                        for new_position in [(-1, 0), (0, 1), (1, 0), (0, -1)]:

                            xPos = new_position[0] + s.position[0]
                            if xPos < 0 or xPos >= 395:
                                continue

                            yPos = new_position[1] + s.position[1]
                            if yPos < 0 or yPos >= 500:
                                continue

                            if visited[xPos][yPos]:
                                continue

                            rgb = image.getpixel((xPos, yPos))
                            if not check_modifier(rgb) == 0.3 or rgb == Terrain.Out_of_Bounds.value:
                                continue

                            if s.distance == Constants.IceLimit.value:
                                continue

                            new_node = Node(None, (xPos, yPos))
                            new_node.distance = s.distance + 1
                            reached_nodes.put(new_node)
                            visited[xPos][yPos] = True
                            draw.point(new_node.position, fill=Terrain.Ice.value)
            # During fall, find all path adjacent to easy forest and change it to leaf trail
            elif season == "fall":
                if rgb == Terrain.Easy_Forest.value:
                    for new_position in [(-1, 0), (0, 1), (1, 0), (0, -1), (1, 1), (-1, -1), (-1, 1), (1, -1)]:
                        # check x positions
                        xPos = new_position[0] + x
                        if xPos < 0 or xPos >= 395:
                            continue
                        # check y positions
                        yPos = new_position[1] + y
                        if yPos < 0 or yPos >= 500:
                            continue
                        # check if it is just another easy forest
                        rgb = image.getpixel((xPos, yPos))
                        if rgb == Terrain.Easy_Forest.value:
                            continue
                        # adjust the terrain for fallen leaves
                        if rgb == Terrain.Foot_path.value:
                            draw.point((xPos, yPos), fill=Terrain.Leaf_Trail.value)
                        elif rgb == Terrain.Paved_Road.value:
                            draw.point((xPos, yPos), fill=Terrain.Leaf_Road.value)
            # spring BFS, search for water and find all land within 15 units with only a 1 in change of elevation
            elif season == "spring":
                if check_modifier(rgb) == 0.3:
                    new_node = Node(None, (x, y))
                    new_node.distance = 0
                    reached_nodes.put(new_node)
                    visited[x][y] = True
                    # spring BFS
                    while not reached_nodes.empty():
                        s = reached_nodes.get()
                        for new_position in [(-1, 0), (0, 1), (1, 0), (0, -1)]:
                            # x bound check
                            xPos = new_position[0] + s.position[0]
                            if xPos < 0 or xPos >= 395:
                                continue
                            # y bound check
                            yPos = new_position[1] + s.position[1]
                            if yPos < 0 or yPos >= 500:
                                continue
                            # visited check
                            if visited[xPos][yPos]:
                                continue
                            # check for water or terrain
                            rgb = image.getpixel((xPos, yPos))
                            if check_modifier(rgb) == 0.3 or rgb == Terrain.Out_of_Bounds.value:
                                continue
                            # check for max distance
                            if s.distance == Constants.MudLimit.value:
                                continue
                            # check for change in elevation
                            if elevation[yPos][xPos] - elevation[s.position[1]][s.position[0]] > 1:
                                continue

                            # add cell to the queue and set it to mud
                            new_node = Node(None, (xPos, yPos))
                            new_node.distance = s.distance + 1
                            reached_nodes.put(new_node)
                            visited[xPos][yPos] = True
                            draw.point(new_node.position, fill=Terrain.Mud.value)

    return image


# function to calculate the g cost for heuristic
def calculate_g_cost(image, point1, point2, elevation):
    # terrain modifiers
    rgb_one = image.getpixel((point1[0], point1[1]))
    rgb_two = image.getpixel((point2[0], point2[1]))
    mod1 = check_modifier(rgb_one)
    mod2 = check_modifier(rgb_two)

    # change in x and y
    deltaX = (Constants.xScale.value ** 2)
    deltaY = (Constants.yScale.value ** 2)
    temp = (elevation[point2[1]][point2[0]] - elevation[point1[1]][point1[0]])

    # hill climbing scale, uphill or downhill change has a 20% effect on cost
    hill_scale = 1.0
    if temp < 0:
        hill_scale = 1.2
    elif temp > 0:
        hill_scale = 0.8

    # change in z
    deltaZ = temp ** 2

    if point1[0] == point2[0]:
        temp = math.sqrt((deltaY + deltaZ)) / 2
        return ((temp / mod1) + (temp / mod2)) / hill_scale

    elif point1[1] == point2[1]:
        temp = math.sqrt((deltaX + deltaZ)) / 2
        return ((temp / mod1) + (temp / mod2)) / hill_scale

    else:
        temp = math.sqrt((deltaX + deltaY + deltaZ)) / 2
        return ((temp / mod1) + (temp / mod2)) / hill_scale


# function to calculate the h cost for heuristic
def calculate_h_cost(child, end):
    deltaX = (end[0] - child[0]) * Constants.xScale.value
    deltaY = (end[1] - child[1]) * Constants.yScale.value

    return math.sqrt((deltaX ** 2) + (deltaY ** 2))


# function to perform the A* algorithm to find the path between points
def traversal_loop(image, waypoints, elevation, fileName, season):
    # adjust the original image for seasons
    ori = Image.open(image)
    ori = seasons(ori, season, elevation)
    # make a copy to save the alterations and path
    im = ori.copy()
    draw = ImageDraw.Draw(im)

    # priority queue for a*
    open_nodes = queue.PriorityQueue()

    # make the first node at the first waypoint
    start = Node(None, (waypoints[0][0], waypoints[0][1]))
    start.f = start.g = start.h = 0
    # remove the first waypoint
    waypoints.pop(0)

    # move the starting node to the queue
    open_nodes.put(start)

    # draw the first waypoint
    shape = [start.position, (100, 10)]
    draw.ellipse(shape, fill=(122, 122, 255, 255))

    # while there are waypoints perform an A* search to the next one
    for i in waypoints:
        # visited array
        points = list()
        for j in range(395):
            temp = list()
            for k in range(500):
                temp.append(False)
            points.append(temp)

        # end node created and drawn
        end = Node(None, i)
        shape = [(end.position[0]-1, end.position[1]-1), (end.position[0]+1, end.position[1]+1)]
        draw.ellipse(shape, fill=(122, 122, 255, 255))

        # set current = to start and begin a* until you find the end node
        current = start
        while not current == end:
            # set current to smallest f cost node in the queue
            current = open_nodes.get()

            # create possible children for the current node
            for new_position in [(-1, 0), (0, 1), (1, 0), (0, -1), (1, 1), (-1, -1), (1, -1), (-1, 1)]:
                # x bound check
                xPos = new_position[0] + current.position[0]
                if xPos < 0 or xPos >= 395:
                    continue
                # y bound check
                yPos = new_position[1] + current.position[1]
                if yPos < 0 or yPos >= 500:
                    continue
                # visited check
                if points[xPos][yPos]:
                    continue
                # out of bound or impassable check
                rgb = ori.getpixel((xPos, yPos))
                if check_modifier(rgb) == 0.0:
                    continue
                # create new node at current position + offset
                new_node = Node(current, (xPos, yPos))

                # computes its values
                new_node.g = calculate_g_cost(ori, current.position, new_node.position, elevation) + current.g
                new_node.h = calculate_h_cost(new_node.position, end.position)
                new_node.f = new_node.g + new_node.h

                # add child nodes to open_nodes and set it's position to visited
                open_nodes.put(new_node)
                points[new_node.position[0]][new_node.position[1]] = True

        # create a new start node at the end waypoint for the next iteration
        start = Node(None, end.position)
        start.f = start.g = start.h = 0

        # reset the queue and add the new start
        open_nodes = queue.PriorityQueue()
        open_nodes.put(start)

        # follow the lineage of the current node and draw a line along the positions
        while current is not None:
            draw.point(current.position, fill=(255, 0, 0, 255))
            current = current.parent

    # save the altered image and show
    im.save(fileName)
    im.show()


def main():

    elevation = store_elevation(sys.argv[2])
    waypoints = store_waypoints(sys.argv[3])

    traversal_loop(sys.argv[1], waypoints, elevation, sys.argv[5], sys.argv[4])


if __name__ == "__main__":
    main()



