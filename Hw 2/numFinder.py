from time import time
import random
import sys


# function to create a list of numbers from a given file
def create_nums_file(file_path):
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


# function to check which sum is closer to the target value
def check_value(target, sum1, sum2):
    # since the target value is a 4 digit number, we ignore any new sum greater than 9999
    if sum2 > 9999:
        return sum1
    # check the absolute distance from the target value to see which sum to keep
    if abs(target - sum1) <= abs(target-sum2):
        return sum1
    else:
        return sum2


def create_random_operations():
    # list of operations in order to use
    operations = list()
    # populate the operations list with random operations
    for i in range(0, 99):
        op = random.randint(0, 3)
        operations.append(op)
    return operations


def hill_climb_step(target, input_nums):
    # best values recorded in a climb
    best = sys.maxsize
    best_operations = list()
    best_numbers = list()

    # random state of the input numbers shuffled
    values = input_nums.copy()
    random.shuffle(values)
    overall_val_temp = values.copy()

    operations = create_random_operations()
    overall_op_temp = operations.copy()

    # printing the starting state
    print("Starting operations: ", operations)
    print("Starting numbers: ", values)

    # starting distance to initiate the algorithm's loop
    previous_climb = best - 1

    # algorithm loop
    while abs(target - previous_climb) < abs(target - best):

        # set the best =  to the previous
        best = previous_climb

        # temporary list for numbers and ops
        temp_nums = values.copy()
        temp_ops = operations.copy()

        # find the best option from swapping values
        best_swap = sys.maxsize
        for i in range(len(values)):
            for ii in range(len(values)):
                swap(i, ii, temp_nums)

                # check the current value produced by the swapping
                curr = temp_nums[0]
                for iii in range(1, len(values) - 1):
                    curr = perform_op(operations[iii - 1], temp_nums, iii, curr)

                # record the best swap value and list
                temp = best_swap
                best_swap = check_value(target, best_swap, curr)
                if temp != best_swap:
                    best_numbers = temp_nums.copy()

                # reset temp_nums
                temp_nums = values.copy()

        # find the best option for changing operations
        best_change = sys.maxsize
        for i in range(len(operations)):
            change(i, temp_ops)

            # check the current value produced by the swapping
            curr = temp_ops[0]
            for ii in range(1, len(values) - 1):
                curr = perform_op(temp_ops[ii - 1], values, ii, curr)

            temp = best_change
            best_change = check_value(target, best_change, curr)
            if temp != best_change:
                best_operations = temp_ops.copy()

            # reset temp_ops
            temp_ops = operations.copy()

        # record the best move this iteration
        previous_climb = check_value(target, best_change, best_swap)

        # update the operations and values list
        if previous_climb == best_change:
            operations = best_operations.copy()
        elif previous_climb == best_swap:
            values = best_numbers.copy()
        # if there is no new best, reset the best_numbers and best_operations list
        else:
            best_numbers = values.copy()
            best_operations = operations.copy()

    # printing the current results
    print("Best sum:", best)
    print("Operations:", operations)
    print("Values:", values)
    print()

    return best, best_operations, best_numbers, overall_val_temp, overall_op_temp


# function to perform random restart hill climbing under a given time frame
def restart_hill_climb(target, input_nums, timeout):

    # start time to keep track of time out
    start_time = time()

    # stores the best data from all attempts of hill climbing
    overall_best = sys.maxsize
    overall_op = list()
    overall_num = list()
    best_start_num = list()
    best_start_op = list()

    # out loop to check for timeout
    while (time() - start_time) < timeout:
        temp1, temp2, temp3, temp4, temp5 = hill_climb_step(target, input_nums)
        if check_value(target, temp1, overall_best) != overall_best:
            overall_best = temp1
            overall_op = temp2.copy()
            overall_num = temp3.copy()
            best_start_num = temp4.copy()
            best_start_op = temp5.copy()

    # printing the best results
    print("Starting operations: ", best_start_op)
    print("Starting numbers: ", best_start_num)
    print("Best sum:", overall_best)
    print("Final Operations:", overall_op)
    print("Final Values:", overall_num)
    print()


def main():

    nums = create_nums_file("./nums.txt")
    restart_hill_climb(6937, nums, 10)
    print("done\n")

    restart_hill_climb(6937, nums, 50)
    print("done\n")

    restart_hill_climb(6937, nums, 100)
    print("done\n")


if __name__ == "__main__":
    main()