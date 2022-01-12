from env import Env
from ai import Agent
from com_ai import Agent as ComAgent
from gui import Graphics
from maploader import MapLoader


if __name__ == "__main__":
    # MAP CONFIG VVV
    sim = Env(**MapLoader().get_inits(3,9,5,seed=0))
    agents_list = [sim.add_agent(agent_class=ComAgent, spawn_point=(2,4), optimized=False, mode='minimax'),
            sim.add_agent(agent_class=Agent, spawn_point=(2,2), optimized=False),]
    # MAP CONFIG ^^^

    gui = Graphics(30, game=sim.state, delay=70)

    print("initial map")
    gui.redrawPage(sim.state)
    while not (sim.goal_test()):
        result=""

        agent=agents_list[sim.whose_turn]

        snake=sim.state.agent_list[agent.my_id]
        gui.drawTextLog(snake.name+" (of team "+snake.team.upper()+") individual Score is: " + str(snake.foodScore),
                        color=agent.my_id)
        while result != "success" and 'has died' not in result:
            action = agent.act()
            # action = gui.getAction()
            print("attempting", action)
            result=sim.take_action(action, agent)
            print(action, result)
        gui.redrawPage(sim.state)
        gui.drawScores(sim.state)
        gui.drawTextLog(snake.name+" (of team "+snake.team.upper()+") individual Score is: " + str(snake.foodScore),
                        color=agent.my_id)
        print("\n")

    print(
        "\n\nпобеда!!!",
        '\nwinner is '+str(sim.get_current_state()['whose_winner']),
        "\nyour cost (number of valid actions):", sim.perceive(agent)["cost"],
        "\nyour score (Food score - turn costs):", sim.perceive(agent)["score"]
    )
