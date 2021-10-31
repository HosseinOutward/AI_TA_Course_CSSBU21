from env import Env
from ai import Agent
from gui import Graphics
from maploader import MapLoader


if __name__ == "__main__":
    sim = Env(**MapLoader().get_inits())
    agent1 = sim.add_agent(agent_class=Agent)
    gui = Graphics(30, game=sim.state, delay=50)

    print("initial map")
    gui.redrawPage(sim.state)
    while not (sim.goal_test()):
        result=""

        snake=sim.state.agent_list[agent1.my_id]
        gui.drawTextLog(snake.name+" (of team "+snake.team.upper()+") individual Score is: " + str(snake.foodScore),
                        color=agent1.my_id)
        while result != "success" and 'has died' not in result:
            action=agent1.act()
            print("attempting", action)
            result=sim.take_action(action, agent1)
            print(action, result)
        gui.redrawPage(sim.state)
        gui.drawScores(sim.state)
        gui.drawTextLog(snake.name+" (of team "+snake.team.upper()+") individual Score is: " + str(snake.foodScore),
                        color=agent1.my_id)
        print("\n")

    # if winner:
    #     gui.drawTextLog("Winner, Winner, Chicken Dinner. ", (255, 215, 0), 3000)
    #     gui.drawTextLog("Team " + str(alphabeta[arena.players[playerID].team]).upper() + " won.", (255, 215, 0), 3000)
    # else:
    #     gui.drawTextLog("GAME OVER", (255, 255, 255), 3000)
    #     for snake in arena.players:
    #         gui.drawTextLog(str(snake.realScore) + " moves by " + str(snake.name), arena.players[playerID].color, 1000)

    print(
        "\n\nпобеда!!!",
        "\nyour cost (number of valid actions):", sim.perceive(agent1)["cost"],
        "\nyour score (number of cleared tiles):", sim.perceive(agent1)["score"]
    )

#**********************************************************************************************************

def getInit(a):
    ai = 0
    if a == 'L':
        n = str(input("Level Number: "))
        arena = pickle.load(open("SavedStates/" + n + "-Arena.pickle", "rb"))
        ai = pickle.load(open("SavedStates/" + n + "-Q_AI.pickle", "rb"))

        # needs more input***
        cubeSize = 30
        g = Simulator.Arena(len(arena.foodGrid), len(arena.foodGrid[0]), True, 1, 5, 10, 200, 2,
                            ["Q_agent1", "MinMax1", "Q_agent2", "MinMax2"],
                            ["Q-LEARNING", "MINMAX", "Q-LEARNING", "MINMAX"], True)
        # ***

        arena.copyPlayers(g)
        gui = GUI.Graphics(len(arena.foodGrid), len(arena.foodGrid[0]), cubeSize, arena)

    elif a == 'N':
        fScoreAdd = int(input("fScore Add "))
        fScoreMulti = int(input("fScore Multi "))
        width = int(input("Width "))
        height = int(input("Height "))

        consumeMode = input("Consume mode (B or A) ")
        if consumeMode != "B" or "b":
            consumeMode = False
        else:
            consumeMode = True

        stochastic = input("stochastic (Y or N) ")
        if stochastic != "Y" or "y":
            stochastic = False
        else:
            stochastic = True

        numT = int(input("number of teams (one for solo) "))
        numP = int(input("number of players per team"))

        PlayerNames, PlayersType = [], []
        for i in range(numP * numT):
            PlayerNames.append(str(input("name of player from team " + (i % numT + 1) + ": ")))
            PlayersType.append(str(input("whats Type of" + PlayerNames[i] +
                        "(type EXACTLY: IDS, MinMax, RBFS, Q-learning (will need training) or Human )")).upper())
            if PlayersType[-1] == "Q-LEARNING":
                ai = True

        winScore = int(input("Score to Win "))
        trnCost = float(input("Turning Penalty "))
        cubeSize = int(input("Window Size (ex. 30 for FHD)"))

        arena = Simulator.Arena(width, height, consumeMode, trnCost, fScoreAdd, fScoreMulti, winScore, numT,
                                PlayerNames, PlayersType, stochastic)
        gui = GUI.Graphics(width, height, cubeSize, arena)

        if ai == True:
            ai = AI.AI_Q_LEARNING()
            ai.train(arena, 20000)

        if str(input("save this World? Y/N")).upper() == 'Y':
            dill.dump(arena, file=open("arena.pickle", "wb"))
            if ai is AI.AI_Q_LEARNING:
                dill.dump(ai, file=open("Q_AI.pickle", "wb"))


    elif a == 'P':
        # needs more input***
        cubeSize = 30
        arena = Simulator.Arena(8, 8, True, 1, 5, 10, 200, 2, ["Q_agent1", "MinMax1", "Q_agent2", "MinMax2"],
                                ["Q-LEARNING", "MINMAX", "Q-LEARNING", "MINMAX"], True)
        # ***

        n = str(input("Pattern Number: "))
        pattern = dill.load(open("Patterns/" + n + ".pickle", "rb"))
        arena.loadPatternInit(pattern)
        gui = GUI.Graphics(len(arena.foodGrid), len(arena.foodGrid[0]), cubeSize, arena)

    else:
        arena = Simulator.Arena(10, 5, True, 1, 5, 10, 200, 22, ["Q_agent1", "MinMax1", "Q_agent2", "MinMax2"],
                                ["Q-LEARNING", "MINMAX", "Q-LEARNING", "MINMAX"], True)
        gui = GUI.Graphics(10, 5, 30, arena)
        ai = AI.AI_Q_LEARNING()
        ai.train(arena, 20000)

        # dill.dump(arena, file=open("SavedStates/"+str(7)+"-Arena.pickle", "wb"))
        # dill.dump(ai, file=open("SavedStates/"+str(7)+"-Q_AI.pickle", "wb"))

        # a=[[1,3,5,7,9,7,5,3,1],
        #   [1,3,5,7,9,7,5,3,1],
        #   [1,3,5,7,9,7,5,3,1],
        #   [1,3,5,7,9,7,5,3,1],
        #   [1,3,5,7,9,7,5,3,1],
        #   [1,3,5,7,9,7,5,3,1],
        #   [1,3,5,7,9,7,5,3,1],
        #   [1,3,5,7,9,7,5,3,1],
        #   [1,3,5,7,9,7,5,3,1]]
        # dill.dump(pattern, file=open("Patterns/" + str(6) + ".pickle", "wb"))

    return arena, gui, ai
