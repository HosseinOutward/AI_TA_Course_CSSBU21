class Agent:
    def __init__(self, perceive_func):
        self.perceive_func = perceive_func

    def act(self):
        # currentData might be `None` while simulator is processing the world and/or agent actions.
        currentData = self.perceive_func()
        if currentData is None or ("status" in currentData and currentData["status"] == "victory"):
            return None


        # YOUR CODE HERE

        # Implement your solution here
        # You have access to the current state of the world via `currentData` object.
        # `currentData` includes: `status`, `location`, `score`, `cost`, `world`.
        # Eventually you will return a string representing your action (all possible actions are mentioned below)
        print(currentData)

        map = currentData["map"]
        loc_i, loc_j = currentData["location"]
        if map[loc_i][loc_j] == 1: return "suck"

        actionlist=[]
        if not (loc_i == 0 or map[max(0, loc_i - 1)][loc_j] == -1):actionlist.append("up")
        if not(loc_j == 0 or map[loc_i][max(0, loc_j - 1)] == -1):actionlist.append("left")
        if not(loc_i == len(map) - 1 or map[min(len(map) - 1, loc_i + 1)][loc_j] == -1):actionlist.append("down")
        if not(loc_j == len(map[0]) - 1 or map[loc_i][min(len(map[0]) - 1, loc_j + 1)] == -1):actionlist.append("right")

        import random
        action = random.choice(actionlist)

        return action
