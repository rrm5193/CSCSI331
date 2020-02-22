from PIL import Image
from _collections import defaultdict
import enum
import sys

class Terrain(enum.Enum):
    Open_Land: (248, 148, 18, 255)
    Rough_Meadow: (255, 192, 0, 255)
    Easy_Forest: (255, 255, 255, 255)
    Slow_Forest: (2, 208, 60, 255)
    Walk_Forest: (2, 136, 40, 255)
    Imapss_Veg: (5, 73, 24, 255)
    Lak_Swmp_Mrsh: (0, 0, 255, 255)
    Paved_Road: (71, 51, 3, 255)
    Foot_path: (0, 0, 0, 255)
    Out_of_Bounds: (205, 0, 101, 255)
    Ice_Mud: (217, 251, 255, 255)


# function to return the effect the terrain has on movement
def check_modifier(rgb_color):
    # Open Land - 90% movement
    if rgb_color == Terrain.Open_Land:
        return 0.9
    # moving shrubbery is long - 60%
    elif rgb_color == Terrain.Rough_Meadow:
        return 0.6
    # Need to watch for branches - 75%
    elif rgb_color == Terrain.Easy_Forest:
        return 0.75
    # Need to watch for more branches - 65%
    elif rgb_color == Terrain.Slow_Forest:
        return 0.65
    # It's walking time - 55%
    elif rgb_color == Terrain.Walk_Forest:
        return 0.55
    # you literally can't get through this - 0%
    elif rgb_color == Terrain.Imapss_Veg:
        return 0.0
    # Not ideal but can swim - 30%
    elif rgb_color == Terrain.Lak_Swmp_Mrsh:
        return 0.3
    # Paved road - 100% optimal movement
    elif rgb_color == Terrain.Paved_Road:
        return 1.0
    # it's pretty good terrain - 90%
    elif rgb_color == Terrain.Foot_path:
        return 0.9
    # you can run in this but like you're trying not to fall - 45%
    elif rgb_color == Terrain.Ice_Mud:
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
            x.append(i)
        elevation.append(x)
    return elevation


def store_waypoints(fp):
    wfile = open(fp, 'r')
    points = defaultdict(set)
    for line in wfile:
        word = line[:-1]
        values = word.split()
        x = int(values[0])
        y = int(values[1])
        points[x].add(y)
    return points


def a_star():
    print("whyyyy")


def traversal_loop(image, waypoints, elevation):
    im = Image.open(image)
    im2 = im.copy()
    for i in waypoints:
        start = i
        end = waypoints[i]


def main():
    elevation = store_elevation(sys.argv[2])
    for x in elevation:
        print(x)
    waypoints = store_waypoints(sys.argv[3])
    for i in waypoints:
        print("x: ")
        print(i)
        print("y: ")
        print(waypoints[i])


if __name__ == "__main__":
    main()



