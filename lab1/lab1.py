import queue
from PIL import Image
from PIL import ImageDraw
import enum
import sys
import time


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
    Ice_Mud = (217, 251, 255, 255)


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

    def __eq__(self, other):
        return self.position == other.position


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
    elif rgb_color == Terrain.Ice_Mud.value:
        return 0.45
    # out of bounds - 0%
    else:
        return 0.0


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


def store_waypoints(fp):
    wfile = open(fp, 'r')
    points = list()
    for line in wfile:
        temp = list()
        word = line[:-1]
        values = word.split()
        x = int(values[0])
        y = int(values[1])
        temp.append(x)
        temp.append(y)
        points.append(temp)
    return points


def calculate_g_cost(image, point1, point2, elevation):
    rgb_one = image.getpixel((point1[0], point1[1]))
    rgb_two = image.getpixel((point2[0], point2[1]))
    mod1 = check_modifier(rgb_one)
    mod2 = check_modifier(rgb_two)

    deltaX = Constants.xScale.value ** 2
    deltaY = Constants.yScale.value ** 2
    deltaZ = (elevation[point2[0]][point2[1]] - elevation[point1[0]][point1[1]]) ** 2

    if point1[0] == point2[0]:
        temp = (deltaY + deltaZ)/2
        return (temp / mod1) + (temp / mod2)

    elif point1[1] == point2[1]:
        temp = (deltaX + deltaZ) / 2
        return (temp / mod1) + (temp / mod2)

    else:
        temp = (deltaX + deltaY + deltaZ)/2
        return (temp / mod1) + (temp / mod2)


def calculate_h_cost(child, end):
    deltaX = (end[0] - child[0]) * Constants.xScale.value
    deltaY = (end[1] - child[1]) * Constants.yScale.value

    return (deltaX ** 2) + (deltaY ** 2)


def traversal_loop(image, waypoints, elevation, fileName):
    start_time = time.time()
    ori = Image.open(image)
    im = ori.copy()
    draw = ImageDraw.Draw(im)

    open_nodes = list()
    close_nodes = list()

    start = Node(None, [waypoints[0][0], waypoints[0][1]])
    start.f = start.g = start.h = 0
    waypoints.pop(0)

    open_nodes.append(start)

    for i in waypoints:
        end = Node(None, [i[0], i[1]])

        print(f"start: {start.position} end: {end.position}")

        while len(open_nodes) > 0 and (time.time() - start_time) < 75.0:
            current = open_nodes[0]
            curr_index = 0
            for index, item in enumerate(open_nodes):
                if item.f < current.f:
                    current = item
                    curr_index = index
            open_nodes.pop(curr_index)
            close_nodes.append(current)

            if current == end:
                break

            children = list()
            for new_position in [(-1, 0), (0, 1), (1, 0), (0, -1)]:

                xPos = new_position[0] + current.position[0]
                if xPos < 0 or xPos >= 395:
                    continue

                yPos = new_position[1] + current.position[1]
                if yPos < 0 or yPos >= 500:
                    continue

                rgb = ori.getpixel((xPos, yPos))
                if check_modifier(rgb) == 0.0:
                    continue

                new_node = Node(current, (xPos, yPos))
                children.append(new_node)

            for child in children:

                child.g = calculate_g_cost(ori, current.position, child.position, elevation) + current.g
                child.h = calculate_h_cost(child.position, end.position)
                child.f = child.g + child.h

                addChild = 1

                for seen in open_nodes:
                    if child == seen:
                        if seen.f < child.f:
                            addChild = 0
                        elif seen.f > child.f:
                            seen.f = child.f
                            seen.g = child.g
                            seen.parent = child.parent
                            addChild = 0

                for seen in close_nodes:
                    if child == seen:
                        if seen.f < child.f:
                            addChild = 0
                if addChild:
                    open_nodes.append(child)

        new_start = Node(None, end.position)
        new_start.f = new_start.g = new_start.h = 0
        open_nodes.clear()
        open_nodes.append(new_start)

        print(close_nodes)
        current = close_nodes.pop(-1)
        while current is not None:
            draw.point(current.position, fill=(255, 0, 0, 255))
            current = current.parent
        # close_nodes.clear()

    im.save(fileName)
    im.show()


def main():
    elevation = store_elevation(sys.argv[2])
    waypoints = store_waypoints(sys.argv[3])

    traversal_loop(sys.argv[1], waypoints, elevation, sys.argv[5])


if __name__ == "__main__":
    main()



