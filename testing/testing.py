import dill
import tarfile
from os import listdir
from os.path import isfile, join, isdir
from shutil import copyfile
import time
from importlib import import_module
import tracemalloc
import pandas
import json
import traceback
import shutil
import sys
import os
from pebble import ProcessPool
from concurrent.futures import TimeoutError


def unpack_zips(folder_path, rewrite=False):
    for f in listdir(folder_path):
        if not isfile(join(folder_path, f)) or not f.endswith(".tar.gz"): continue
        file_name = f.removesuffix('.tar.gz')
        if not rewrite and file_name in listdir(folder_path): continue

        tar = tarfile.open(join(folder_path, f), "r:gz")
        inerfolder = tar.firstmember.name

        try: shutil.rmtree(join(folder_path, file_name))
        except FileNotFoundError: pass

        tar.extractall(folder_path)
        os.rename(join(folder_path, inerfolder), join(folder_path, file_name))
        tar.close()


def replace_imports(folder_path):
    for f in listdir(folder_path):
        if not isdir(join(folder_path, f)) or f=='env': continue
        my_file = open(join(folder_path, f,'agent.py'), "r")
        text=my_file.read()
        my_file.close()

        text=text.replace('from env ', 'from .env ').replace('from modeled_env ', 'from .modeled_env ')

        my_file = open(join(folder_path, f,'agent.py'), "w")
        my_file.write(text)
        my_file.close()


def list_names(folder_path):
    names=[]; stu_codes=[]
    for f in listdir(folder_path):
        if not isdir(join(folder_path, f)) or f=='env': continue
        names.append(f)
        with open(join(folder_path, f, 'INFO'), 'r') as myfile:
            stu_codes.append(myfile.readlines()[-1])
    return list(zip(names, stu_codes))


def get_agent_and_info(submission_path):
    # copyfile(join(submission_path, 'env.py'), 'env.py')
    # copyfile(join(submission_path, 'agent.py'), 'agent.py')
    # copyfile(join(submission_path, 'modeled_env.py'), 'modeled_env.py')
    # from agent import Agent
    Agent=import_module('.agent',submission_path.replace('\\','.')).Agent
    return Agent


class Test:
    def __init__(self, agent, env):
        self.env = env
        self.agent = agent

    def run_agent(self, agent_import, env, map, loc):
        sim = env(**map)
        agent1 = sim.add_agent(agent_class=agent_import, spawn_point=loc)

        t=time.time(); tracemalloc.start()
        result = ""
        while not (sim.goal_test()) and 'has died' not in result:
            result = ""
            while result != "success" and 'has died' not in result:
                result = sim.take_action(agent1.act(), agent1)
        t=time.time()-t; ram=tracemalloc.get_traced_memory()[1]/1024

        if 'has died' not in result: sim.perceive(agent1)["cost"]=float('inf')

        return sim.perceive(agent1)["cost"], t, ram

    def cal_score(self, map_info):
        try:
            run_cost, run_time, run_memory = \
                self.run_agent(self.agent, self.env, map_info['map'], map_info['loc'])
            return map_info['cost']/run_cost*100, run_time, run_memory, None
        except Exception as e:
            return 0, None, None, e


class AllTests:
    def __init__(self, map_list, env, timeout):
        self.maps_list = map_list
        self.env = env
        self.timeout=timeout

    def mute(self): sys.stdout = open(os.devnull, 'w')

    def raise_timeout(self, signum, frame): raise TimeoutError

    def test_one_agent(self, agent):
        test = Test(agent, self.env)

        results = []
        with ProcessPool(max_workers=len(self.maps_list),initializer=self.mute) as pool:
            future = pool.map(test.cal_score, self.maps_list, timeout=self.timeout)

            iterator = future.result()
            for i in range(len(self.maps_list)):
                try:
                    r=next(iterator)
                    if r[3] is not None:
                        results.append({'score': r[0], 'run_time': r[1], 'run_memory': r[2], 'map_id': i})
                    else: results.append({'score': r[0], 'error': r[3], 'map_id': i})
                except StopIteration: break
                except TimeoutError as error:
                    # print("function took longer than %d seconds" % error.args[1])
                    results.append({'score': 0, 'map_id': i, 'error': 'timeout %s'%self.timeout})

        sorted(results, key=lambda x: x['map_id'])
        return results


def all_test(pth, zip_names_stu, env, maps_list, time_out=None):
    all_test_obj = AllTests(maps_list, env, time_out)

    agent_list=[get_agent_and_info(r'%s\%s'%(pth,name)) for name, stu in zip_names_stu]
    with ProcessPool(max_workers=len(agent_list)) as pool:
        future = pool.map(all_test_obj.test_one_agent, agent_list)
        iterator = future.result()
        result_list = []
        for name, stu in zip_names_stu:
            try:
                r=next(iterator)
                result_list.append({'name': name, 'stu_id': stu, 'final_score': sum([rr['score'] for rr in r])/len(r),
                                    'error': True in ['error' in rr.keys() for rr in r], 'result': r})
            except StopIteration: break

    print(*result_list, sep='\n')
    return result_list


def prepeare_run(test, unpack, import_fix, backup=False, overwrite=False, time_out=None, map_diff='easy'):
    pth=r'ex\%s'%test

    if backup:
        f=join('backup', test)
        shutil.make_archive(join(f,'bu%s.zip'%len(listdir(f))), 'zip', pth)

    if unpack: unpack_zips(pth, rewrite=overwrite)
    if import_fix: replace_imports(pth)

    env = import_module(pth.replace('\\','.') + '.env.env').Env
    maps_list = json.load(open(r'config\maps\%s_%s.json'%
        ('astar' if test in ['ucs','astar','rbfs'] else 'bfs', map_diff), 'rb'))['runs']

    print('testing ', len(maps_list), 'maps for ', pth)

    pandas.DataFrame(all_test(pth, list_names(pth), env,
        maps_list, time_out=time_out)).to_csv(join(pth,'results.csv'), index=False)


if __name__ == "__main__":
    prepeare_run('ucs', unpack=True, import_fix=True, overwrite=False, backup=False, time_out=120)

