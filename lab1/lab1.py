import queue
from PIL import Image
from PIL import ImageDraw
import enum
import sys
import math


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


class Constants(enum.Enum):
    xScale = 10.29
    yScale = 7.55


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
    # out of bounds - 0%
    else:
        return 0.0


# function to store elevation in a 2d array
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
def seasons(image, season, elevation, modifier):
    if season == "summer":
        return image
    draw = ImageDraw.Draw(image)

    visited = list()
    for i in range(395):
        temp = list()
        for ii in range(500):
            temp.append(False)
        visited.append(temp)

    reached_nodes = queue.Queue()

    for x in range(395):
        for y in range(500):
            if visited[x][y]:
                continue
            rgb = image.getpixel((x, y))
            if season == "winter":
                if not check_modifier(rgb) == 0.3:
                    new_node = Node(None, (x, y))
                    new_node.distance = 0
                    reached_nodes.put(new_node)
                    visited[x][y] = True
                    while not reached_nodes.empty():
                        s = reached_nodes.get()
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

                            if s.distance == 7:
                                continue

                            new_node = Node(None, (xPos, yPos))
                            new_node.distance = s.distance + 1
                            reached_nodes.put(new_node)
                            visited[xPos][yPos] = True
                            draw.point(new_node.position, fill=Terrain.Ice.value)

            elif season == "fall":
                if rgb == Terrain.Easy_Forest.value:
                    for new_position in [(-1, 0), (0, 1), (1, 0), (0, -1), (1, 1), (-1, -1), (-1, 1), (1, -1)]:

                        xPos = new_position[0] + x
                        if xPos < 0 or xPos >= 395:
                            continue

                        yPos = new_position[1] + y
                        if yPos < 0 or yPos >= 500:
                            continue

                        rgb = image.getpixel((xPos, yPos))
                        if rgb == Terrain.Easy_Forest.value:
                            continue

                        modifier[xPos][yPos] = 0.5

            elif season == "spring":
                if check_modifier(rgb) == 0.3:
                    new_node = Node(None, (x, y))
                    new_node.distance = 0
                    reached_nodes.put(new_node)
                    visited[x][y] = True
                    while not reached_nodes.empty():
                        s = reached_nodes.get()
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
                            if check_modifier(rgb) == 0.3 or rgb == Terrain.Out_of_Bounds.value:
                                continue

                            if s.distance == 15:
                                continue

                            if elevation[yPos][xPos] - elevation[s.position[1]][s.position[0]] > 1:
                                continue

                            new_node = Node(None, (xPos, yPos))
                            new_node.distance = s.distance + 1
                            reached_nodes.put(new_node)
                            visited[xPos][yPos] = True
                            draw.point(new_node.position, fill=Terrain.Mud.value)

    return image, modifier


# function to calculate the g cost for heuristic
def calculate_g_cost(image, point1, point2, elevation, modifier):
    rgb_one = image.getpixel((point1[0], point1[1]))
    rgb_two = image.getpixel((point2[0], point2[1]))
    mod1 = check_modifier(rgb_one) * modifier[point1[0]][point1[1]]
    mod2 = check_modifier(rgb_two) * modifier[point2[0]][point2[1]]

    deltaX = Constants.xScale.value ** 2
    deltaY = Constants.yScale.value ** 2
    deltaZ = (elevation[point2[1]][point2[0]] - elevation[point1[1]][point1[0]]) ** 2

    if point1[0] == point2[0]:
        temp = math.sqrt((deltaY + deltaZ)) / 2
        return (temp / mod1) + (temp / mod2)

    elif point1[1] == point2[1]:
        temp = math.sqrt((deltaX + deltaZ)) / 2
        return (temp / mod1) + (temp / mod2)

    else:
        temp = math.sqrt((deltaX + deltaY + deltaZ)) / 2
        return (temp / mod1) + (temp / mod2)


# function to calculate the h cost for heuristic
def calculate_h_cost(child, end):
    deltaX = (end[0] - child[0]) * Constants.xScale.value
    deltaY = (end[1] - child[1]) * Constants.yScale.value

    return math.sqrt((deltaX ** 2) + (deltaY ** 2))


def traversal_loop(image, waypoints, elevation, fileName, season):

    modifier = list()
    for j in range(395):
        temp = list()
        for k in range(500):
            temp.append(1.0)
        modifier.append(temp)

    ori = Image.open(image)
    ori, modifier = seasons(ori, season, elevation, modifier)
    im = ori.copy()
    draw = ImageDraw.Draw(im)

    open_nodes = queue.PriorityQueue()

    start = Node(None, (waypoints[0][0], waypoints[0][1]))
    start.f = start.g = start.h = 0
    waypoints.pop(0)

    open_nodes.put(start)

    for i in waypoints:
        points = list()
        for j in range(395):
            temp = list()
            for k in range(500):
                temp.append(False)
            points.append(temp)

        end = Node(None, i)

        current = start
        while not current == end:

            current = open_nodes.get()

            children = list()
            for new_position in [(-1, 0), (0, 1), (1, 0), (0, -1), (1, 1), (-1, -1), (1, -1), (-1, 1)]:

                xPos = new_position[0] + current.position[0]
                if xPos < 0 or xPos >= 395:
                    continue

                yPos = new_position[1] + current.position[1]
                if yPos < 0 or yPos >= 500:
                    continue

                if points[xPos][yPos]:
                    continue

                rgb = ori.getpixel((xPos, yPos))
                if check_modifier(rgb) == 0.0:
                    continue

                new_node = Node(current, (xPos, yPos))
                children.append(new_node)

            for child in children:

                child.g = calculate_g_cost(ori, current.position, child.position, elevation, modifier) + current.g
                child.h = calculate_h_cost(child.position, end.position)
                child.f = child.g + child.h

                open_nodes.put(child)
                points[child.position[0]][child.position[1]] = True

        start = Node(None, end.position)
        start.f = start.g = start.h = 0

        open_nodes = queue.PriorityQueue()
        open_nodes.put(start)

        while current is not None:
            draw.point(current.position, fill=(255, 0, 0, 255))
            current = current.parent
    im.save(fileName)
    im.show()


def main():

    elevation = store_elevation(sys.argv[2])
    waypoints = store_waypoints(sys.argv[3])

    traversal_loop(sys.argv[1], waypoints, elevation, sys.argv[5], sys.argv[4])


if __name__ == "__main__":
    main()



