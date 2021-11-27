import random
from copy import deepcopy


class Agent:
    def __init__(self, perceive_func=None, agent_id=None):
        self.perceive_func = perceive_func
        self.my_id = agent_id

        ######### EDITABLE SECTION #########

        self.predicted_actions = []

        ######### END OF EDITABLE SECTION #########

    def act(self):
        sensor_data = self.perceive_func(self)

        ######### EDITABLE SECTION #########

        if self.predicted_actions==[]: self.predicted_actions=self.idfs(sensor_data['Current_Env'])
        action=self.predicted_actions.pop()

        ######### END OF EDITABLE SECTION #########

        return action

    ######### VV EDITABLE SECTION VV #########
    def idfs(self, root_env):
        def dls(game, limit):  # returns [success, action]
            if game.goal_test():
                return [True, "found the goal"]
            elif limit == 0:
                return [False, "reached limit"]

            actions_list = ["right", "left", "up", "down"]
            random.shuffle(actions_list)
            for action in actions_list:
                child_game = deepcopy(game)
                game_result = child_game.take_action(action, self.my_id)
                if 'has died' not in game_result:
                    dls_result = dls(child_game, limit - 1)
                    actions_taken = deepcopy(dls_result[1]) if type(dls_result[1]) is list else []
                    actions_taken.append(action)
                    if dls_result[0]:
                        return [True, actions_taken]

            return [False, "no good action found"]

        depth = 1
        while True:
            print("limited to depth of: ", depth)
            result = dls(root_env, depth)
            if result[0]:
                return result[1]
            snake=root_env.state.agent_list[self.my_id]
            depth += snake.shekam + len(snake.body)

    def bfs(self, game):
        pass

    def dfs(self, game):
        pass

