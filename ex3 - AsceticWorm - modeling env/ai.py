import random
from collections import deque
import json
from modeled_env import ModeledEnv, set_constants
from time import time


class Agent:
    def __init__(self, perceive_func=None, agent_id=None, optimized=True, mode='idfs'):
        self.perceive_func = perceive_func
        self.my_id = agent_id

        self.predicted_actions = []
        self.actions_list = ['up', 'right', 'down', 'left']

        self.optimized = optimized
        self.alg = eval('self.'+mode)
        print('running '+mode)

    def act(self):
        sensor_data = self.perceive_func(self)
        if self.optimized:
            set_constants(json.loads(sensor_data['Current_Env'])['state'])
            sensor_data['Current_Env'] = ModeledEnv()
        else:
            from env import Env
            sensor_data['Current_Env'] = Env([1], [1]).from_json(**json.loads(sensor_data['Current_Env'])['state'])

        if self.predicted_actions == []:
            t0=time()
            self.predicted_actions = self.alg(sensor_data['Current_Env'])
            print(time()-t0)

        action = self.predicted_actions.pop()

        return action

    def idfs(self, root_env, jump_ite=3):
        def dls(game, limit):
            q = deque()
            q.append([game, []])

            while q:
                # pop first element from queue
                node = q.pop()

                # goal test
                if node[0].goal_test():
                    return node[1]

                # randomize list to decrease chance of infinite loop
                # but also not too much so to prevent too much turning cost penalty
                if random.random() > 0.8:
                    random.shuffle(self.actions_list)

                # check if in limit
                if len(node[1])!=limit:
                    # add children to queue
                    for action in self.actions_list:
                        child_game = node[0].create_copy()
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
        q = deque()
        q.append([game, []])

        depth = 1
        state_visited_count = 1
        while q:
            # print progress
            if state_visited_count == 0:
                state_visited_count = len(q)
                print("height: ", depth, ", state in ram: ", len(q))
                depth += 1
            state_visited_count -= 1

            # pop first element from queue
            node = q.popleft()

            # goal test
            if node[0].goal_test():
                return node[1]

            # add children to queue
            random.shuffle(self.actions_list)
            for action in self.actions_list:
                child_game = node[0].create_copy()
                if 'd' not in child_game.take_action(action, self.my_id):
                    q.append([child_game, [action] + node[1]])

    def dfs(self, game):
        q = deque()
        q.append([game, []])

        depth = 1
        while q:
            # print progress
            if depth % 5 == 0:
                print("height: ", depth, ", state in ram: ", len(q))
            depth += 1

            # pop first element from queue
            node = q.pop()

            # goal test
            if node[0].goal_test():
                return node[1]

            # randomize list to decrease chance of infinite loop
            # but also not too much so to prevent too much turning cost penalty
            if random.random() > 0.8:
                random.shuffle(self.actions_list)

            # add children to queue
            for action in self.actions_list:
                child_game = node[0].create_copy()
                if 'd' not in child_game.take_action(action, self.my_id):
                    q.append([child_game, [action] + node[1]])
