import random
from copy import deepcopy
from collections import deque
# from env import Env
# import json


class Agent:
    def __init__(self, perceive_func=None, agent_id=None):
        self.perceive_func = perceive_func
        self.my_id = agent_id

        ######### EDITABLE SECTION #########

        self.predicted_actions = []

        ######### END OF EDITABLE SECTION #########

    def act(self):
        sensor_data = self.perceive_func(self)
        # sensor_data['Current_Env']=Env([1],[1]).from_json(**json.loads(sensor_data['Current_Env'])['state'])

        ######### EDITABLE SECTION #########

        if self.predicted_actions==[]: self.predicted_actions=self.idfs(sensor_data['Current_Env'])
        action=self.predicted_actions.pop()

        ######### END OF EDITABLE SECTION #########

        return action

    ######### VV EDITABLE SECTION VV #########
    def idfs(self, root_env, jump_ite=3):
        def dls(game, limit):
            q = []
            q.append([game, []])

            actions_list = ['up', 'right', 'down', 'left']
            while q:
                # pop last element from queue
                node = q.pop()

                # goal test
                if node[0].goal_test():
                    return node[1]

                # randomize list to decrease chance of infinite loop
                # but also not too much so to prevent too much turning cost penalty
                if random.random() > 0.8:
                    random.shuffle(actions_list)

                # check if in limit
                if len(node[1])!=limit:
                    # add children to queue
                    for action in actions_list:
                        child_game = deepcopy(node[0])
                        if 'd' not in child_game.take_action(action, self.my_id):
                            q.append([child_game, [action] + node[1]])

        depth_limit = 0
        while True:
            depth_limit += jump_ite
            print("limited to depth of: ", depth_limit)
            result = dls(root_env, depth_limit)
            if type(result) is list:
                if jump_ite != 1:
                    depth_limit -= jump_ite
                    jump_ite = jump_ite // 2
                else:
                    return result

    def bfs(self, game):
        q = []
        q.append([game, []])

        depth = 1
        state_visited_count = 1
        actions_list=['up', 'right', 'down', 'left']
        while q:
            # print progress
            if state_visited_count == 0:
                state_visited_count = len(q)
                print("height: ", depth, ", state in ram: ", len(q))
                depth += 1
            state_visited_count -= 1

            # pop first element from queue
            node = q.pop(0)

            # goal test
            if node[0].goal_test():
                return node[1]

            # add children to queue
            random.shuffle(actions_list)
            for action in actions_list:
                child_game = deepcopy(node[0])
                if 'd' not in child_game.take_action(action, self.my_id):
                    q.append([child_game, [action] + node[1]])

    def dfs(self, game):
        q = deque()
        q.append([game, []])

        depth = 1
        actions_list=['up', 'right', 'down', 'left']
        while q:
            # print progress
            if depth % 5 == 0:
                print("height: ", depth, ", state in ram: ", len(q))
            depth += 1

            # pop last element from queue
            node = q.pop()

            # goal test
            if node[0].goal_test():
                return node[1]

            # randomize list to decrease chance of infinite loop
            # but also not too much so to prevent too much turning cost penalty
            if random.random() > 0.8:
                random.shuffle(actions_list)

            # add children to queue
            for action in actions_list:
                child_game = deepcopy(node[0])
                if 'd' not in child_game.take_action(action, self.my_id):
                    q.append([child_game, [action] + node[1]])
