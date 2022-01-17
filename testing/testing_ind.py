from testing import ProcessPool, sys, listdir, \
    os, import_module, json, get_agent_and_info, pandas, join


def mute(): sys.stdout = open(os.devnull, 'w')


class Test:
    def __init__(self, agent, env):
        self.env = env
        self.agent = agent

    def run_agent(self, agent_import, env, map, loc):
        sim = env(**map)
        agent1 = sim.add_agent(agent_class=agent_import, spawn_point=loc)

        result = "";i=0
        while not (sim.goal_test()) and 'has died' not in result:
            result = ""
            while result != "success" and 'has died' not in result:
                result = sim.take_action(agent1.act(), agent1)

        if 'has died' in result: sim.perceive(agent1)["cost"]=float('inf')

        return sim.perceive(agent1)["cost"]

    def cal_score(self, map_info):
        return map_info['cost']/self.run_agent(self.agent, self.env, map_info['map'], map_info['loc'])*100


def test_one_agent(agent, env, maps_list, timeout):
    test = Test(agent, env)

    test.cal_score(maps_list[0])
    results=[]
    with ProcessPool(max_workers=len(maps_list)) as pool:
        future = pool.map(test.cal_score, maps_list, timeout=timeout)

        iterator = future.result()
        for i in range(len(maps_list)):
            try:
                r=next(iterator)
                results.append({'score': r, 'map_id': i})
            except StopIteration:
                break
            except TimeoutError as error:
                print("function took longer than %d seconds" % error.args[1])
    print(results)

def test_once(test, name, maps=(0,1,2,3), timeout=4*60):
    pth=r'ex\%s'%test
    env = import_module(pth.replace('\\','.') + '.env.env').Env
    maps_list = json.load(open(r'config\maps\%s_%s.json'%
        ('astar' if test in ['ucs','astar','rbfs'] else 'bfs', 'easy'), 'rb'))['runs']
    maps_list = [mp for i,mp in enumerate(maps_list) if i in maps]
    test_one_agent(get_agent_and_info(r'%s\%s'%(pth,name)), env, maps_list, timeout=timeout)


def error_df():
    for test in listdir(r'ex'):
        print(test)
        try:
            df=pandas.read_csv(join('ex',test,'results.csv')).set_index('name')\
                [['error-0','error-1','error-2','error-3']]
            df=df[df.apply(lambda x: x!='timeout')]
            df=df.dropna(how='all')
            df.to_csv(join('ex',test,'error.csv'))
        except: pass


if __name__ == "__main__":
    test_once('a-star', 'یاس جابرانصاری')


