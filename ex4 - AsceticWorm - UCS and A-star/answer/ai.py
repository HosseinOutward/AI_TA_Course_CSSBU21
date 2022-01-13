import random
from queue import PriorityQueue
import json
from modeled_env import ModeledEnv, set_constants
from time import time


class Agent:
    def __init__(self, perceive_func=None, agent_id=None, optimized=True, mode='ucs'):
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


    def ucs(self, root_game):
        class Node:
            def __init__(self, game, path):
                self.game_env=game
                self.path=path
            def __eq__(self, other):
                return self.game_env==other.game_env
            def __lt__(self, other): return isinstance(other, Node)

        frontier = PriorityQueue()
        frontier.put((0, Node(root_game,[])))  # (priority, node)
        explored = []

        depth = 1
        state_visited_count = 1
        while True:
            # print progress
            if state_visited_count == 0:
                state_visited_count = len(frontier.queue)
                print("height: ", depth, ", state in ram: ", len(frontier.queue))
                depth += 1
            state_visited_count -= 1

            if frontier.empty(): raise Exception("No way Exception")

            ucs_w, current_node = frontier.get()

            explored.append(current_node)

            if current_node.game_env.goal_test(): return current_node.path

            if random.random()<0.2: random.shuffle(self.actions_list)
            for action in self.actions_list:
                c_game = current_node.game_env.create_copy()
                if 'd' in c_game.take_action(action, self.my_id): continue

                child_node=Node(c_game,[action]+current_node.path)
                action_cost=1

                try: in_front=frontier.queue.index(child_node)
                except: in_front=False
                if in_front is False and child_node not in explored:
                    frontier.put((ucs_w + action_cost, child_node))
                if in_front is not False and len(frontier.queue[in_front].path)>ucs_w+action_cost:
                    frontier.put((ucs_w + action_cost, child_node))



    def heuristic(self, state):
        return 0

    def a_star(self, root_game):
        pass

