from env import Env
from ai import Agent
from gui import Graphics
from maploader import MapLoader


if __name__ == "__main__":
    map_initial = MapLoader().get_inits(10, 15, 10, seed=0)
    sim = Env(**map_initial)
    agent1 = sim.add_agent(agent_class=Agent, loc=(5,5))
    gui = Graphics(30, game=sim.state, delay=70)

    print("initial map")
    gui.redrawPage(sim.state)
    while not (sim.goal_test()):
        result=""

        snake=sim.state.agent_list[agent1.my_id]
        gui.drawTextLog(snake.name+" (of team "+snake.team.upper()+") individual Score is: " + str(snake.foodScore),
                        color=agent1.my_id)
        while result != "success" and 'has died' not in result:
            action = agent1.act()
            # action = gui.getAction()
            print("attempting", action)
            result=sim.take_action(action, agent1)
            print(action, result)
        gui.redrawPage(sim.state)
        gui.drawScores(sim.state)
        gui.drawTextLog(snake.name+" (of team "+snake.team.upper()+") individual Score is: " + str(snake.foodScore),
                        color=agent1.my_id)
        print("\n")

    print(
        "\n\nпобеда!!!",
        "\nyour cost (number of valid actions):", sim.perceive(agent1)["cost"],
        "\nyour score (Food score - turn costs):", sim.perceive(agent1)["score"]
    )
