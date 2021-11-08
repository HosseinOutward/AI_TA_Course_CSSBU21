from env import Env
from ai import Agent
from gui import Graphics
from maploader import MapLoader


if __name__ == "__main__":
    sim = Env(**MapLoader().get_inits(10,15,10))
    agent1 = sim.add_agent(agent_class=Agent)
    gui = Graphics(30, game=sim.state, delay=70)

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
