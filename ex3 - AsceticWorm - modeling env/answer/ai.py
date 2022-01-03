import random
from collections import deque
import json
from time import time


class Agent:
    def __init__(self, perceive_func=None, agent_id=None, optimized=True, mode='idfs'):
        self.perceive_func = perceive_func
        self.my_id = agent_id

        self.predicted_actions = []
        self.actions_list = ['u', 'r', 'd', 'l']
        random.shuffle(self.actions_list)

        self.optimized = optimized
        self.alg = eval('self.' + mode)
        print('running ' + mode)

    def act(self):
        sensor_data = self.perceive_func(self)
        map_action = {'u': 'up', 'r': 'right', 'd': 'down', 'l': 'left'}
        if self.optimized:
            from modeled_env import ModeledEnv, set_constants
            set_constants(json.loads(sensor_data['Current_Env'])['state'])
            sensor_data['Current_Env'] = ModeledEnv()
        else:
            from env import Env
            self.actions_list = ['up', 'right', 'down', 'left']
            random.shuffle(self.actions_list)
            sensor_data['Current_Env'] = Env([1], [1]).from_json(**json.loads(sensor_data['Current_Env'])['state'])

        if self.predicted_actions == []:
            t0 = time()
            self.predicted_actions = self.alg(sensor_data['Current_Env'])
            self.predicted_actions = [map_action[a] if a in map_action.keys() else a
                                      for a in self.predicted_actions]
            print(time() - t0)

        action = self.predicted_actions.pop()

        return action

    def idfs(self, root_env, jump_ite=3):
        def dls(game, limit):
            q = deque([])
            q.append([game, []])

            while q:
                # pop last element from queue
                node = q.pop()

                # shuffle to prevent loops but not too often to help with speed
                if random.random() < 0.2: random.shuffle(self.actions_list)

                # check if in limit
                if len(node[1]) == limit: continue

                # add children to queue
                for action in self.actions_list:
                    child_game = node[0].create_copy()
                    if 'd' not in child_game.take_action(action, self.my_id):
                        q.append([child_game, [action] + node[1]])

                        # goal test
                        if child_game.goal_test(): return [action] + node[1]

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
        q = deque([])
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

            # shuffle to prevent loops but not too often to help with speed
            if random.random() < 0.2: random.shuffle(self.actions_list)

            # add children to queue
            for action in self.actions_list:
                child_game = node[0].create_copy()
                if 'd' not in child_game.take_action(action, self.my_id):
                    q.append([child_game, [action] + node[1]])

                    # goal test
                    if child_game.goal_test(): return [action] + node[1]

    def dfs(self, game):
        q = deque([])
        q.append([game, []])

        depth = 1
        while q:
            # print progress
            if depth % 5 == 0:
                print("height: ", depth, ", state in ram: ", len(q))
            depth += 1

            # pop last element from queue
            node = q.pop()

            # shuffle to prevent loops but not too often to help with speed
            if random.random() < 0.2: random.shuffle(self.actions_list)

            # add children to queue
            for action in self.actions_list:
                child_game = node[0].create_copy()
                if 'd' not in child_game.take_action(action, self.my_id):
                    q.append([child_game, [action] + node[1]])

                    # goal test
                    if child_game.goal_test(): return [action] + node[1]
