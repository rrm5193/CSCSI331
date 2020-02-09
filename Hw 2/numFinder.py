from time import time
import random
import sys


# function to create a list of numbers from a given file
def create_num_list(file_path):
    nums = list()
    file = open(file_path, 'r')
    for line in file:
        nums.append(float(line))
    return nums


# a function to swap two values at the given indices of numbers
def swap(n1, n2, numbers):
    while n1 == n2:
        n2 = random.randint(0, 99)
    temp = numbers[n1]
    numbers[n1] = numbers[n2]
    numbers[n2] = temp


# a function to randomly change the operation at the given index
def change(i, operators):
    temp = operators[i]
    new = random.randint(0, 4)
    while new == temp:
        new = random.randint(0, 4)
    operators[i] = new


# function to perform the operation specified, avoiding division by 0
def perform_op(op, nums, i, curr):
    if op == 0:
        return curr + nums[i]
    elif op == 1:
        return curr - nums[i]
    elif op == 2:
        return curr * nums[i]
    else:
        if nums[i] == 0:
            new_op = random.randint(0, 3)
            if new_op == 0:
                return curr + nums[i]
            elif new_op == 1:
                return curr - nums[i]
            else:
                return curr * nums[i]
        return curr / nums[i]


def check_value(target, sum1, sum2):
    # since the target value is a 4 digit number, we ignore any new sum greater than 9999
    if sum2 > 9999:
        return sum1
    # check the absolute distance from the target value to see which sum to keep
    if abs(target - sum1) <= abs(target-sum2):
        return sum1
    else:
        return sum2


def restart_hill_climb(target, values):
    # start time to keep track of time out
    start_time = time()

    best = sys.maxsize
    best_operations = list()
    best_numbers = list()

    # list of operations in order to use
    operations = list()

    # populate the operations list with random operations
    for i in range(0, 99):
        op = random.randint(0, 3)
        operations.append(op)

    # main algorithm loop to run before timeout
    while (time() - start_time) < 100:
        # check the current value produced by the algorithm
        curr = values[0]
        for i in range(1, 100):
            curr = perform_op(operations[i-1], values, i, curr)

        # check if the current total beats the best total recorded
        temp = best
        best = check_value(target, best, curr)
        if temp != best:

            # set the best operation and number list equal to the current
            best_operations = operations.copy()
            best_numbers = values.copy()
            print(best)
            print(best_operations)
            print(best_numbers)
        else:

            # set the current list equal to the best
            operations = best_operations.copy()
            values = best_numbers.copy()

        # determine the next step to takes
        transition = random.randint(0, 2)
        if transition:
            swap(random.randint(0, 99), random.randint(0, 99), values)
        else:
            change(random.randint(0, 98), operations)


def main():

    nums = create_num_list("./nums.txt")
    restart_hill_climb(6937, nums)
    print("done")

    nums = create_num_list("./nums2.txt")
    restart_hill_climb(6937, nums)
    print("done")


if __name__ == "__main__":
    main()