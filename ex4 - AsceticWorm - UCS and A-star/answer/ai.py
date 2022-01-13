import random
from queue import PriorityQueue
import json
from modeled_env import ModeledEnv, set_constants
from time import time


class Agent:
    def __init__(self, perceive_func=None, agent_id=None, optimized=True, mode='astar'):
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
        my_id=self.my_id
        class Node:
            def __init__(self, game, path):
                self.game_env=game
                self.path=path
            def generate_child(self, action):
                if self.game_env is None: return 'd'
                c_game = self.game_env.create_copy()
                if 'd' in c_game.take_action(action, my_id): return 'd'
                return Node(c_game,[action]+self.path)
            def __eq__(self, other):
                try: return self.game_env==other.game_env
                except AttributeError: return False
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
                child_node=current_node.generate_child(action)
                if child_node=='d': continue

                action_cost=1
                try: in_front=frontier.queue.index(child_node)
                except: in_front=False
                if in_front is False and child_node not in explored:
                    frontier.put((ucs_w + action_cost, child_node))
                if in_front is not False and len(frontier.queue[in_front].path)>ucs_w+action_cost:
                    frontier.queue[in_front].game_env=None
                    frontier.put((ucs_w + action_cost, child_node))

    def heuristic(self, game_env):
        snake = game_env.state.agent_list[self.my_id]
        game=game_env.state

        w, h = len(game.foodGrid), len(game.foodGrid[0])
        score, moves = game_env.state.get_team_score(self.my_id), 0
        x, y, energy = snake.body[0][0], snake.body[0][1], snake.shekam + len(snake.body)
        begin = 1
        while score < game.winScore:
            minPoint, minFood = 0, 10
            for r in range(begin, energy):
                for i in range(-r, r + 1):
                    if not (x + i >= w or y + r - abs(i) >= h or x + i < 0 or y + r - abs(i) < 0):
                        if minFood > game.foodGrid[x + i][y + r - abs(i)] or game.foodGrid[x + i][y + r - abs(i)] != 0:
                            minPoint = [x + i, y + r - abs(i)]
                            minFood = game.foodGrid[x + i][y + r - abs(i)]
                for i in range(-r + 1, r):
                    if not (x + i >= w or y + abs(i) - r >= h or x + i < 0 or y + abs(i) - r < 0):
                        if minFood > game.foodGrid[x + i][y + abs(i) - r] or game.foodGrid[x + i][y + abs(i) - r] != 0:
                            minPoint = [x + i, y + abs(i) - r]
                            minFood = game.foodGrid[x + i][y + abs(i) - r]

            if minPoint != 0:
                x, y = minPoint[0], minPoint[1]
                score += game.foodAddScore + game.foodScoreMulti * minFood
                moves += energy
                begin = 1
            else:
                begin = energy
                energy += 1
        return moves

    def astar(self, root_game):
        my_id=self.my_id
        class Node:
            action_cost=1
            def __init__(self, game, path, g):
                self.game_env=game
                self.path=path
                self.g=g
            def generate_child(self, action):
                if self.game_env is None: return 'd'
                c_game = self.game_env.create_copy()
                if 'd' in c_game.take_action(action, my_id): return 'd'
                return Node(c_game,[action]+self.path, self.g+self.action_cost)
            def __eq__(self, other):
                try: return self.game_env==other.game_env
                except AttributeError: return False
            def __lt__(self, other): return isinstance(other, Node)

        frontier = PriorityQueue()
        frontier.put((0, Node(root_game,[], 0)))  # (priority, node)
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
                child_node=current_node.generate_child(action)
                if child_node=='d': continue

                try: in_front=frontier.queue.index(child_node)
                except: in_front=False
                cost=lambda : child_node.g + self.heuristic(child_node.game_env)
                if in_front is False and child_node not in explored:
                    frontier.put((cost(), child_node))
                cost=cost()
                if in_front is not False and len(frontier.queue[in_front].path)>cost:
                    frontier.queue[in_front].game_env=None
                    frontier.put((cost, child_node))

    def rbfs(self, root_game):
        def rbfs_call(game_env, fTillNow, f_limit):
            if game_env.goal_test():
                return [True, [], f_limit]

            successors = []
            if random.random()<0.2: random.shuffle(self.actions_list)
            r = list(self.actions_list)
            for action in r:
                c_game = game_env.create_copy()
                if 'd' in c_game.take_action(action, self.my_id): continue
                successors.append([c_game, action, 0])

            if len(successors) == 0: return [False, random.randint(0, 3), 100000]

            for s in successors: s[2] = fTillNow + 1 + self.heuristic(s[0])

            while True:
                successors.sort(key=lambda x: x[2])
                best = successors[0]

                if best[2] > f_limit: return [False, best[1], best[2]]

                if len(successors) != 1: altF = successors[1][2]
                else: altF = best[2]

                result = rbfs_call(best[0], fTillNow + 1, min(f_limit, altF))
                best[2] = result[2]

                if result[0]:
                    return [True, [best[1]]+result[1], best[2]]
        result = rbfs_call(root_game, 0, 100000)
        return result[1]
