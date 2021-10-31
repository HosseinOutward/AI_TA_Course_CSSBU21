class MapLoader:
    def get_map(self):
        return [
            [1,3,5],
            [1,3,5],
        ]

    def get_chance_map(self):
        return [
            [1,0,1],
            [1,0,1],
        ]

    def get_inits(self):
        return {'foodGrid': self.get_map(), 'chance_map': self.get_chance_map(),
                "consume_tile": False, "turningCost": 0, "foodAddScore": 1,
                "foodScoreMulti": 2, "winScore": 35}