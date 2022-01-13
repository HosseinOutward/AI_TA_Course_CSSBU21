import random


def set_constants(c_json):
    global constant_dict
    constant_dict = c_json


class ModeledEnv:
    def __init__(self, copy=False):
        if not copy:
            self.state = ModeledState()

    def take_action(self, action, agent):
        return self.state.update(action, agent)

    def goal_test(self):
        for agent_idx in range(len(self.state.agent_list)):
            if self.state.get_team_score(agent_idx) >= self.state.winScore:
                return True
        return False

    def create_copy(self):
        _copy = type(self)(copy=True)
        _copy.state = self.state.create_copy()
        return _copy

    def __eq__(self, obj):
        return obj.state == self.state


class ModeledState:
    def __init__(self, copy=False):
        if not copy:
            self.agent_list = [ModeledSnake(snake_idx) for snake_idx in range(len(constant_dict["agent_list"]))]

    def __getattr__(self, item):
        global constant_dict
        return constant_dict[item]

    def get_agent_index(self, agent):
        agent_idxs = [idx for idx, ad in enumerate(self.agent_list) if ad.agent_type == agent]
        if len(agent_idxs) == 0:
            print("agent not found");
            return None
        else:
            return agent_idxs[0]

    def update(self, action, agent):
        action=action[:1]
        agent_idx = agent if type(agent) is int else self.get_agent_index(agent)
        if agent_idx is None: return "invalid agent"
        if not self.validate_action(action): return "invalid action"
        snake = self.agent_list[agent_idx]

        if snake.body == []: return 'd'  # died

        # move snake
        snake.move(action.lower())

        # check if impacted
        impact = self.check_for_impact(agent_idx)
        if impact == 'e' or impact == 'h':
            snake.body = []
            return 'd'  # died
        elif impact is not False:
            snake.foodScore -= 1

        # eat
        self.eat(agent_idx)

        # turning cost
        if snake.currentDir != action: snake.foodScore = max(snake.foodScore-self.turningCost, 0)
        snake.currentDir = action

        return "success"

    def validate_action(self, action):
        if type(action) is not str or action.lower() not in ["u", "d", "r", "l"]:
            print("the action '%s' is invalid" % action)
            return False
        return True

    def check_for_impact(self, agent_idx):
        snake = self.agent_list[agent_idx]
        snake_head = snake.body[-1]
        if snake_head[0] // len(self.foodGrid) != 0 or snake_head[1] // len(self.foodGrid[0]) != 0:
            return 'e'  # exited map
        if snake_head in snake.body[:-1]:
            return 'h'  # hit its own body

        for other_snake in self.agent_list:
            if snake is other_snake: continue
            if snake_head in other_snake.body: return "o"  # hit '%s' body" % other_snake.name
        return False

    def eat(self, agent_idx):
        snake = self.agent_list[agent_idx]
        snake_head = snake.body[-1]

        if random.random() > self.chance_map[snake_head[0]][snake_head[1]]: return "nothing happened (stochastic)"

        tile=self.foodGrid[snake_head[0]][snake_head[1]]
        if len(snake.body)+snake.shekam == 1 and tile!=0:
            snake.foodScore += self.foodAddScore + self.foodScoreMulti * tile
            snake.shekam += tile

            if self.consume_tile:
                self.foodGrid[snake_head[0]][snake_head[1]] = \
                    round(tile * random.uniform(0.1, 0.9))

    def get_team_score(self, agent_idx):
        snake = self.agent_list[agent_idx]
        score = 0
        for other_snake in self.agent_list:
            if other_snake.team == snake.team:
                score += other_snake.foodScore
        return score

    def create_copy(self):
        _copy = type(self)(copy=True)

        _copy.agent_list = [snake.create_copy() for snake in self.agent_list]

        return _copy

    def __eq__(self, obj):
        return obj.agent_list == self.agent_list


class ModeledSnake:
    def __init__(self, snake_idx, copy=False):
        self.snake_idx = snake_idx
        if not copy:
            global constant_dict
            self.shekam = constant_dict['agent_list'][self.snake_idx]['shekam']
            self.foodScore = constant_dict['agent_list'][self.snake_idx]['foodScore']
            self.currentDir = constant_dict['agent_list'][self.snake_idx]['currentDir']
            self.body = constant_dict['agent_list'][self.snake_idx]['body']

    def __getattr__(self, item):
        global constant_dict
        return constant_dict['agent_list'][self.snake_idx][item]

    def move(self, action):
        delta_i, delta_j = {"u": (-1, 0), "d": (+1, 0), "r": (0, +1), "l": (0, -1)}[action]
        self.body.append([self.body[-1][0] + delta_i, self.body[-1][1] + delta_j])

        if self.shekam == 0:
            del self.body[0]
            if len(self.body) != 1: del self.body[0]
        else:
            self.shekam -= 1

        self.realCost += 1

    def create_copy(self):
        _copy = type(self)(self.snake_idx, copy=True)
        _copy.body, _copy.shekam, _copy.foodScore, _copy.realCost, _copy.currentDir = \
            [*self.body], self.shekam, self.foodScore, self.realCost, self.currentDir

        return _copy

    def __eq__(self, obj):
        return obj.shekam == self.shekam and \
               obj.body == self.body and \
               obj.foodScore == self.foodScore and \
               obj.realCost == self.realCost and \
               obj.currentDir == self.currentDir
