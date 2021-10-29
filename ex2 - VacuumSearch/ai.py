from env import Env

class Agent:
    def __init__(self, perceive_func=None, agent_id=None):
        self.perceive_func = perceive_func
        self.my_id = agent_id

        ######### EDITABLE SECTION #########

        ######### END OF EDITABLE SECTION #########

    def act(self):
        sensor_data = self.perceive_func(self)

        ######### EDITABLE SECTION #########
        root_env = Env()
        import random
        action = random.choice(["right", "left", "up", "down", "suck"])

        ######### END OF EDITABLE SECTION #########

        return action

