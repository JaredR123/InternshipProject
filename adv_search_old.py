import main as game

victory_bias = 500

def search(node_array):
    current_best = -2000  # alpha value
    best = 2000  # beta value
    iteration = 0  # leaf nodes are iterated through in sets of four
    min_arr = [0, 0, 0, 0]

    while iteration < 16:
        # Finds the max during the player state
        for i in range(4 * iteration, 4 + 4 * iteration):
            if current_best < node_array[i]:
                current_best = node_array[i]
        # Resets beta if a new set of leaf nodes is being iterated through to not mess up enemy state calculation
        if iteration % 4 == 0:
            best = 100
        best = min(current_best, best)  # Finds the min of the max nodes during the enemy state
        min_arr[int(iteration / 4)] = best  # Creates an array of the min nodes from the enemy state
        current_best = -100  # Resets alpha for next player state calculation
        iteration += 1

    a, b, c, d = min_arr
    node_value = max(a, b, c, d)  # Finds the max of the arrayed min nodes and returns them to the root node
    return node_value


def reward(x, y, width, height):
    reward_vertical = 0
    reward_left = 0
    reward_right = 0
    collision_penalty = 1000

    reward_vertical += height - y + victory_bias
    reward_left += x
    reward_right += width - x

    if game.main().will_hit()[0] and not game.main().will_hit()[2]:
        reward_vertical -= collision_penalty
    elif game.main().will_hit()[2]:
        if game.main().will_hit()[1]:
            reward_right -= collision_penalty
        else:
            reward_left -= collision_penalty

    return reward_vertical, reward_left, reward_right


def main():
    arr = \
        [6, 7, 5, 3, 9, 2, 5, 6, 3, 2, 4, 5, 7, 6, 9, 2, 1, 5, 9, 2, 3, 6, 3, 7,
         8, 6, 7, 5, 9, 4, 3, 1, 10, 15, 13, 20, 50, -50, 3, 7, -2, 3, 5, 6, -5,
         -3, -1, 0, -50, -30, -10, -20, -40, 0, 20, -10, 0, -50, 10, 12, -50, -20, -1, -5]
    print(search(arr))


main()
