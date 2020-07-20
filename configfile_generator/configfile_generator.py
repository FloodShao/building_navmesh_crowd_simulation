import sys
import os
import yaml

from .template_conf_yaml import *
from .behavior_file import *
from .scene_file import *
from .util import *

class BuildConfigYaml:
    def __init__(self, yaml_file):
        with open(yaml_file) as file:
            self._yaml_node = yaml.load(file, yaml.SafeLoader)

    # todo: add multiple levels integration     
    def getRawData(self):
        return self._yaml_node['L1']

def generate_behavior_file(yaml_node, output_dir):
    behavior_file = BehaviorFile()

    # first add all the goals
    goals = GoalsYAML()
    goals.loadGoal(yaml_node['goals'])

    # construct behavior file element
    for key in yaml_node:
        if key == "state" :
            for s in yaml_node[key] :
                state = StateYAML().load(s)
                behavior_file.addState(state)
        if key == "transition" :
            for t in yaml_node[key] :
                transition = TransitionYAML().load(t)
                behavior_file.addTransition(transition)
        if key == "goal_set" :
            for gs in yaml_node[key] :
                goal_set = GoalSetYAML().load(gs)

                # update goal_sets with goal
                for area in gs['set_area'] :
                    area_list = goals.getGoals(area)
                    for g in area_list :
                        # g is GoalYAML type
                        tmp = Goal()
                        tmp.setCoord(g._x, g._y)
                        tmp.setCapacity(gs['capacity'])
                        goal_set.addGoal(tmp)

                behavior_file.addGoalSet(goal_set)

    writeXmlFile(behavior_file.outputXmlElement(), output_dir = output_dir, file_name = 'behavior_file.xml')

def generate_scene_file(yaml_node, output_dir):
    scene_file = SceneFile()

    # add default configuration
    scene_file.addSpatialQuery()
    scene_file.addCommon()

    # load all the agent list first
    if not 'agent_list' in yaml_node :
        raise ValueError("No agent_list provided!")

    agent_list = AgentsListYAML()
    agent_list.load(yaml_node['agent_list'])

    for key in yaml_node:
        if key == 'obstacle_set' :
            for item in yaml_node[key] :
                tmp = ObstacleSetYAML().load(item)
                scene_file.addSubElement(tmp)

        if key == 'agent_profile' :
            for item in yaml_node[key]:
                tmp = AgentProfileYAML().load(item)
                scene_file.addSubElement(tmp)

        if key == 'agent_group' :
            for item in yaml_node[key]:
                tmp_yaml = AgentGroupYAML()
                tmp_yaml.load(item)
                tmp = tmp_yaml.loadAgents(agent_list)
                scene_file.addSubElement(tmp)

    writeXmlFile(scene_file.outputXmlElement(), output_dir = output_dir, file_name = 'scene_file.xml')


def main():
    if len(sys.argv) > 2 :
        config_yaml_path = sys.argv[1]
        output_dir = sys.argv[2]
    else: 
        sys.exit(1)
        raise ValueError("Please provide config_yaml_path and the output_dir as required.")
    
    if not os.path.exists(config_yaml_path):
        print('map path does not exist!')
        sys.exit(1)
        raise ValueError('Map path not exist!')

    if not os.path.exists(output_dir):
        os.mkdir(output_dir)
    
    yaml_parse = BuildConfigYaml(config_yaml_path)
    yaml_node = yaml_parse.getRawData()

    generate_behavior_file(yaml_node, output_dir)
    generate_scene_file(yaml_node, output_dir)

if __name__ == '__main__':
    sys.exit(main())
