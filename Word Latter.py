from collections import defaultdict


def create_graph(words):
    # holds a list for every combination of words omitting one letter
    node = defaultdict(list)
    # holds a graph where each word is a vertex that connects
    # to words that only differ by one letter
    graph = defaultdict(set)
    # open the file passed in and read each line to create the graph
    wfile = open(words,'r')
    for line in wfile:
        # removes the new line character at the end
        word = line[:-1]
        # checks each combinations of letters in the word removing one at a time
        for i in range(len(word)):
            # new letter combo to add
            newNode = '{}_{}'.format(word[:i],word[i+1:])
            # if this is not a combo then add this vertex to the graph and form its edges
            if len(node[newNode]) != 0:
                for ii in node[newNode]:
                    graph[word].add(ii)
                    graph[ii].add(word)
            node[newNode].append(word)

    # prints the words in graph and their connections
    # for word1 in graph:
    #     print('starting: ' + word1)
    #     for word2 in graph[word1]:
    #         print(' ')
    #         print(word2)
    #     print('\n')

    # loop to print the list of words in node
    # for bucket in node:
    #     print(bucket)
    #     for word1 in node[bucket]:
    #         print(word1)
    #         print('\n')
    #     print('\n')
    return graph


def traverse(start,end,graph):
    print()


def main():
    create_graph("./test.txt")


if __name__ == "__main__":
    main()