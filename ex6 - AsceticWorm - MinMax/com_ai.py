import random
from collections import deque
import json
from modeled_env import ModeledEnv, set_constants
from time import time


class Agent:
    def __init__(self, perceive_func=None, agent_id=None, optimized=False, mode='bfs'):
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

    def bfs(self, root_game):
        q = []
        q.append([root_game, []])

        while q:
            # pop first element from queue
            node = q.pop(0)

            if random.random()<0.2: random.shuffle(self.actions_list)
            for action in self.actions_list:
                # add children to queue
                child_game = node[0].create_copy()
                if 'd' not in child_game.take_action(action, self.my_id):
                    q.append([child_game, [action] + node[1]])
                # goal test
                if child_game.goal_test(): return [action] + node[1]

    def heuristic(self, state):
        return 0

    def minimax(self, root_game):
        result=self.minimax_agent(root_game)
        return result[1]

    def minimax_agent(self, game, limit=10):
        state=game.get_current_state()
        if not state['whose_alive'][self.my_id] or limit==0:
            return -1,[]
        elif game.goal_test(): return 1,[]

        isMaxTurn=state['whose_turn']==self.my_id

        results = []
        if random.random()<0.2: random.shuffle(self.actions_list)
        for move in self.actions_list:
            child=game.create_copy()
            child.take_action(move, state['whose_turn'])
            current_result=self.minimax_agent(child, limit=limit-1)
            results.append((current_result[0], current_result[1]+[move]))

        return max(results, key=lambda r: r[0]) if isMaxTurn else min(results, key=lambda r: r[0])

    def alpha_beta(self):
        pass

