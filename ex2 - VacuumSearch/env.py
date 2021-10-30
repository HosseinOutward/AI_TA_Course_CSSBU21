import random


class State:
    def __init__(self, map_builder, consume_tile=False, turningCost=0, foodAddScore=1, foodScoreMulti=1, winScore=200):
        self.consume_tile, self.winScore = consume_tile, winScore
        self.foodScoreMulti, self.foodAddScore, self.turningCost = foodScoreMulti, foodAddScore, turningCost
        self.foodGrid = map_builder.get_map()
        self.chance = map_builder.get_chance_map()
        self.agent_list=[]
        self.maxFoodScore=0

    def get_agent_index(self, agent):
        agent_idxs = [idx for idx, ad in enumerate(self.agent_list) if ad.agent_type == agent]
        if len(agent_idxs) == 0: print("agent not found"); return None
        else: return agent_idxs[0]

    def update(self, action, agent):
        agent_idx = agent if type(agent) is int else self.get_agent_index(agent)
        if agent_idx is None: return "invalid agent"
        if not self.validate_action(action): return "invalid action"
        snake = self.agent_list[agent_idx]

        if snake.body==[]: return snake.name+' has died'

        # move snake
        snake.move(action)

        # check if impacted
        impact=self.check_for_impact(agent_idx)
        if impact == 'exited map' or impact == 'hit its own body':
            snake.body=[]
            return snake.name+' has died'
        elif impact is not False: snake.foodScore -= 1

        # eat
        self.eat(agent_idx)

        # turning cost
        if snake.currentDir != action: snake.foodScore -= self.turningCost
        snake.currentDir = action

        return "success"

    def validate_action(self, action):
        if type(action) is not str or action.lower() not in ["up", "down", "right", "left"]:
            print("the action '%s' is invalid" % action)
            return False
        return True

    def check_for_impact(self, agent_idx):
        snake = self.agent_list[agent_idx]
        snake_head = snake.body[-1]
        if not (0 <= snake_head[0] <= len(self.foodGrid) - 1 and 0 <= snake_head[1] <= len(self.foodGrid[0]) - 1):
            return 'exited map'
        for part in snake.body[:-1]:
            if snake_head == part: return 'hit its own body'

        for other_snake in self.agent_list:
            for part in other_snake.body:
                if snake is other_snake: continue
                if snake_head == part: return "hit '%s' body" % other_snake.name
        return False

    def eat(self, agent_idx):
        snake = self.agent_list[agent_idx]
        snake_head = snake.body[-1]
        if random.random() > self.chance[snake_head[0]][snake_head[1]]: return "nothing happened (stochastic)"

        if len(snake.body) == 1 and snake.shekam == 0:
            snake.foodScore += self.foodAddScore + self.foodScoreMulti * self.foodGrid[snake_head[0]][snake_head[1]]
            snake.shekam += self.foodGrid[snake_head[0]][snake_head[1]]
            if self.get_team_score(agent_idx) > self.maxFoodScore:
                self.maxFoodScore = self.get_team_score(agent_idx)

            if self.consume_tile:
                self.foodGrid[snake_head[0]][snake_head[1]] = \
                    round(self.foodGrid[snake_head[0]][snake_head[1]] * random.uniform(0.1, 0.9))

    def get_team_score(self, agent_idx):
        snake = self.agent_list[agent_idx]
        score = 0
        for other_snake in self.agent_list:
            if other_snake.team == snake.team: score += other_snake.foodScore
        return score

    def __eq__(self, obj):
        return isinstance(obj, State) and \
               obj.map_array == self.map_array

    def __deepcopy__(self, memo):
        from copy import deepcopy
        id_self = id(self)  # memoization avoids unnecesary recursion
        _copy = memo.get(id_self)
        if _copy is None:
            _copy = type(self)(deepcopy(self.map_array, memo))

            _copy.players = []
            for snake in self.players: _copy.players.append(deepcopy(snake))
            _copy.numT = self.numT

            _copy.foodGrid = deepcopy(self.foodGrid)
            _copy.chance = deepcopy(self.chance)
            _copy.foodAddScore = deepcopy(self.foodAddScore)
            _copy.winScore = deepcopy(self.winScore)
            _copy.turnCost = deepcopy(self.turnCost)
            _copy.maxFoodScore = deepcopy(self.maxFoodScore)
            _copy.consume = deepcopy(self.consume)
            _copy.fScoreMulti = deepcopy(self.foodScoreMulti)

            _copy.agent_list=[]
            for i, ao in enumerate(self.agent_list):
                _copy.agent_list.append(
                    {key: deepcopy(value, memo) for key, value in ao.items() if key!="agent_obj"})
                _copy.agent_list[i]["agent_obj"]=self.agent_list[i]["agent_obj"]

            memo[id_self] = _copy
        return _copy


class Snake:
    def __init__(self, agent_type, head_pos, name=None, team=None, env=None):
        self.name = name if name is not None else "agent "+str(len(env.agent_list))
        self.team = team if team is not None else "team "+str(len(env.agent_list))

        self.agent_type = agent_type
        self.shekam = 0
        self.foodScore = 0
        self.realScore = 0
        self.currentDir=None

        self.body = [head_pos]

    def move(self, dir):
        delta_i, delta_j = {"up": (-1,0), "down": (+1,0), "right": (0,+1), "left": (0,-1)}[dir]
        self.body.append([self.body[-1][0]+delta_i, self.body[-1][1]+delta_j])

        if self.shekam == 0:
            del self.body[0]
            if len(self.body) != 1: del self.body[0]
        else: self.shekam -= 1

        self.realScore += 1

    def __eq__(self, obj):
        return isinstance(obj, self) and \
               obj.shekam == self.shekam and \
               obj.body == self.body and \
               obj.name == self.name and \
               obj.foodScore == self.foodScore and \
               obj.realScore == self.realScore and \
               obj.snake_type == self.agent_type and \
               obj.team == self.team and \
               obj.currentDir == self.currentDir

    def __deepcopy__(self, memo):
        from copy import deepcopy
        id_self = id(self)  # memoization avoids unnecesary recursion
        _copy = memo.get(id_self)
        if _copy is None:
            _copy = type(self)(self.agent_type, name=self.name,
                               team=self.team, init_body=False)

            _copy.shekam = deepcopy(self.shekam)
            _copy.body = deepcopy(self.body)
            _copy.name = deepcopy(self.name)
            _copy.foodScore = deepcopy(self.foodScore)
            _copy.realScore = deepcopy(self.realScore)
            _copy.snake_type = deepcopy(self.agent_type)
            _copy.team = deepcopy(self.team)
            _copy.currentDir = deepcopy(self.currentDir)

            memo[id_self] = _copy
        return _copy


class Env:
    def __init__(self, map_builder, **kwargs):
        self.state = State(map_builder, **kwargs)

    def add_agent(self, agent_class):
        ok=False
        while not ok:
            ok=True
            i = random.randint(0, len(self.state.foodGrid)-1)
            j = random.randint(0, len(self.state.foodGrid[0])-1)
            for other_snake in self.state.agent_list:
                if [i,j] in other_snake.body: ok = False

        self.state.agent_list.append(
            Snake(agent_class(self.perceive, len(self.state.agent_list)), [i,j], env=self.state)
        )

        return self.state.agent_list[-1].agent_type

    def take_action(self, action, agent):
        return self.state.update(action, agent)

    def perceive(self, agent):
        agent_data = self.state.agent_list[self.state.get_agent_index(agent)]
        return {
            "map": self.state.foodGrid,
            "chance map": self.state.chance,
            "agent loc": agent_data,
            "score": agent_data,
            "cost": agent_data,
            }
        
    def goal_test(self):
        for agent_idx in range(len(self.state.agent_list)):
            if self.state.get_team_score(agent_idx) >= self.state.winScore: return True
        return False

    def __eq__(self, obj):
        return isinstance(obj, Env) and \
               obj.state == self.state

    def __deepcopy__(self, memo):
        from copy import deepcopy
        id_self = id(self)  # memoization avoids unnecesary recursion
        _copy = memo.get(id_self)
        if _copy is None:
            _copy = type(self)(deepcopy(self.state.map_array, memo))
            _copy.state = deepcopy(self.state, memo)
        return _copy


# *********************************************************************************************************

class Arena:
    def loadPatternInit(self, pattern):
        for i in range(0, len(self.foodGrid)):
            for j in range(0, len(self.foodGrid[0])):
                self.foodGrid[i][j] = pattern[(i * len(pattern)) // len(self.foodGrid)][
                    (j * len(pattern[0])) // len(self.foodGrid[0])]
        self.initfoodGrid = [[a for a in collumn] for collumn in self.foodGrid]

    def stateTag(self, ID):
        width, height = len(self.foodGrid), len(self.foodGrid[0])
        head = self.players[ID].headPos()
        energy = len(self.players[ID].body) + self.players[ID].shekam
        return ((head[0] * width * height) + (head[1] * width) + energy) * 4 + self.players[ID].currentDir

    def nextTurn(self, ID, action):
        snake = self.players[ID]
        snake.move(int(action))
        impact = self.impact(snake.headPos(), ID)
        if impact == 'd':
            self.kill(snake)
            return 'd'
        elif impact:
            snake.foodScore -= 1
        self.eat(ID)
        if snake.currentDir != action:
            snake.foodScore -= self.turnCost
        snake.currentDir = action
        if self.getTeamScore(ID) >= self.winScore:
            return True
        return False

    def eat(self, ID):
        snake = self.players[ID]
        if random.uniform(0, 1) > self.chance[snake.headPos()[0]][snake.headPos()[1]]: return 0
        if snake.shekam + len(snake.body) == 1:
            snake.foodScore += 1 + self.fScoreMulti * self.foodGrid[snake.headPos()[0]][snake.headPos()[1]]
            snake.shekam += self.foodGrid[snake.headPos()[0]][snake.headPos()[1]]
            if self.getTeamScore(ID) > self.maxFoodScore:
                self.maxFoodScore = self.getTeamScore(ID)
            if self.consume:
                self.foodGrid[snake.headPos()[0]][snake.headPos()[1]] = round(
                    self.foodGrid[snake.headPos()[0]][snake.headPos()[1]] * random.uniform(0.1, 0.9))

    def getTeamScore(self, ID):
        snake = self.players[ID]
        score = 0
        for Othersnake in self.players:
            if Othersnake.team == snake.team:
                score += Othersnake.foodScore
        return score

    def impact(self, head_pos, ID):
        width, height = len(self.foodGrid), len(self.foodGrid[0])
        if head_pos[0] == width or head_pos[1] == height or head_pos[0] == -1 or head_pos[1] == -1: return 'hit wall'
        for part in self.players[ID].body[:-1]:
            if head_pos[0] == part[0] and head_pos[1] == part[1]: return 'hit your own body'

        i = 0
        for OtherSnake in self.players:
            for part in OtherSnake.body:
                if head_pos[0] == part[0] and head_pos[1] == part[1]: i += 1

        if i > 1:
            return True

        return False

    def kill(self, snake):
        self.players.remove(snake)

