from .behavior_file import *
from .scene_file import *

class PointYAML :
    def __init__(self, x, y) :
        self._x = float(x)
        self._y = float(y)
        # for agent point
        self._name = 'GroupId' 

    def params(self, key, value) :
        self._params[key] = value

    def get(self, key) :
        if self._params and key in self._params :
            return self._params[key]
        raise ValueError("Invalid key provided")

class BasicYAML :
    def __init__(self):
        self._attributes = {}

    def getAttributes(self):
        return self._attributes

    def load(self, yaml_node):
        for key in yaml_node :
            self._attributes[key] = yaml_node[key]

class StateYAML (BasicYAML):

    def __init__(self) :
        BasicYAML.__init__(self)
        self._attributes['name'] = None
        self._attributes['goal_set'] = None
        self._attributes['navmesh_file_name'] = None
        self._attributes['final'] = 0

    def load(self, yaml_node):

        BasicYAML.load(self, yaml_node)

        B_state = BehaviorState()
        B_goal_selector = GoalSelector()
        B_vel_component = VelComponent()

        if self._attributes['name'] :
            B_state.setStateName(self._attributes['name'])
        
        if self._attributes['goal_set'] :
            B_goal_selector.setGoalSetId(self._attributes['goal_set'])

        if self._attributes['navmesh_file_name'] :
            B_vel_component.setNavMeshFile(self._attributes['navmesh_file_name'])

        if self._attributes['final'] :
            B_state.setFinalState()
        else :
            B_state.setUnFinalState()
            B_state.setGoalSelector(B_goal_selector)
            B_state.setVelComponent(B_vel_component)

        return B_state

class TransitionYAML (BasicYAML):

    def __init__(self) :
        BasicYAML.__init__(self)
        self._attributes['from'] = None
        self._attributes['to'] = None
        self._attributes['Condition'] = None
        self._attributes['Target'] = None

    def load(self, yaml_node) :
        BasicYAML.load(self, yaml_node)

        B_transition = StateTransition()

        if self._attributes['from'] :
            B_transition.setFromStateName(self._attributes['from'])
        else :
            raise ValueError("A 'from' state must be configured for a transition")
        
        if self._attributes['to'] :
            B_transition.setToStateName(self._attributes['to'])

        if self._attributes['Condition'] :
            B_transition.parseCondition(self._attributes['Condition'])
        else :
            raise ValueError("A 'Condition' state must be configured for a transition")
        
        if self._attributes['Target'] :
            B_transition.parseTarget(self._attributes['Target'])

        if not self._attributes['to'] and not self._attributes['Target'] :
            raise ValueError("A transition must include either 'to' state or a set of 'Target' states.")

        return B_transition


class GoalSetYAML (BasicYAML):
    
    def __init__(self) :
        BasicYAML.__init__(self)
        self._attributes['set_id'] = None
        self._attributes['set_area'] = None
        self._attributes['capacity'] = None

    def load(self, yaml_node) :
        BasicYAML.load(self, yaml_node)
        B_goal_set = GoalSet()

        if not self._attributes['set_id'] == None:
            B_goal_set.setId( self._attributes['set_id'] )
        else :
            raise ValueError("missing 'set_id' for GoalSet")
        
        if self._attributes['set_area'] :
            for area in self._attributes['set_area'] :
                B_goal_set.addGoalArea(area)
        else :
            raise ValueError("missing 'set_area' for GoalSet")

        if self._attributes['capacity'] :
            B_goal_set.setCapacity( self._attributes['capacity'] )
        else :
            raise ValueError("missing 'capacity' for capacity")

        # haven't initialize each goal
        return B_goal_set


class GoalsYAML :
    def __init__(self) :
        self._goals = {}

    def loadGoal(self, yaml_node) :
        for g in yaml_node :
            area = g[3]
            goal = PointYAML(g[0], g[1])

            if not area in self._goals :
                self._goals[area] = []
            
            self._goals[area].append(goal)

    def getGoals(self, area):
        return self._goals[area]


class AgentProfileYAML (BasicYAML):
    def __init__(self):
        BasicYAML.__init__(self)
        self._attributes['name'] = None

        self._attributes['class'] = 'agentClassId'
        self._attributes['max_accel'] = 5
        self._attributes['max_angle_vel'] = 360
        self._attributes['max_neighbors'] = 10
        self._attributes['max_speed'] = 0
        self._attributes['neighbor_dist'] = 5
        self._attributes['obstacleSet'] = 'obstacleSetId'
        self._attributes['pref_speed'] = 0
        self._attributes['r'] = 0.2

        self._attributes['ORCA_tau'] = 1.0
        self._attributes['ORCA_tauObst'] = 0.4

    def load(self, yaml_node):
        keys = yaml_node.keys()

        if len(keys) < len(self.getAttributes()) :
            raise ValueError("There are unspecified parameters for AgentProfile")
        
        if len(yaml_node['name']) == 0:
            raise ValueError("Invalid AgentProfile name provided")
        
        self._attributes['name'] = yaml_node['name']
        agent_profile = AgentProfile(yaml_node['name'])

        # verify the parent method is working
        BasicYAML.load(self, yaml_node)
        
        for key in keys:
            if key == 'class' or \
                key == 'max_accel' or \
                key == 'max_angle_vel' or \
                key == 'max_neighbors' or \
                key == 'max_speed' or \
                key == 'neighbor_dist' or \
                key == 'obstacleSet' or \
                key == 'pref_speed' or \
                key == 'r'  :
                agent_profile.setProfileCommon(key, yaml_node[key])
            if key == 'ORCA_tau' or \
                key == 'ORCA_tauObst' :
                agent_profile.setProfileORCA(key[5:], yaml_node[key])

        return agent_profile

class AgentGroupYAML (BasicYAML):
    def __init__(self):
        BasicYAML.__init__(self)
        self._attributes['GroupId'] = None
        self._attributes['profile_selector'] = None
        self._attributes['state_selector'] = None
        self._agent_group = None

    def load(self, yaml_node):
        keys = yaml_node.keys()

        if not 'GroupId' in keys or not 'profile_selector' in keys or not 'state_selector' in keys :
            raise ValueError("Invalid AgentGroup YAML provided.")

        BasicYAML.load(self, yaml_node)

        self._agent_group = AgentGroup(self._attributes['profile_selector'], self._attributes['state_selector'])
        return self._agent_group

    def loadAgents(self, agents_list_yaml) :
        agents_list = agents_list_yaml.getAgentsGroup(self._attributes['GroupId'])
        if not agents_list or not self._agent_group:
            print("No agents are loaded.")
            return 

        for agent in agents_list :
            # agent is type of PointXML
            self._agent_group.addAgent(agent._x, agent._y)

        return self._agent_group


class AgentsListYAML:
    # not needed in generating the template YAML list
    def __init__(self):
        self._agents = {}

    def load(self, yaml_node):
        for agent in yaml_node :
            group_id = str(agent[2])
            if not group_id in self._agents :
                self._agents[group_id] = []
            self._agents[group_id].append(PointYAML(agent[0], agent[1]))

    def allGroupId(self):
        return self._agents.keys()

    def getAgentsGroup(self, group_id):
        if not str(group_id) in self.allGroupId() :
            print("No agent for [", group_id, "] listed in conf_yaml")
            return None
        
        return self._agents[str(group_id)]


class ObstacleSetYAML (BasicYAML) :
    def __init__(self) :
        BasicYAML.__init__(self)
        self._attributes['class'] = 'obstacleSetId'
        self._attributes['file_name'] = None
        self._attributes['type'] = 'nav_mesh'
        self._obstacle_set = None

    def load(self, yaml_node) :
        BasicYAML.load(self, yaml_node)

        if not self._attributes['file_name']:
            raise ValueError("Invalid file_name provided for obstacle set.")

        self._obstacle_set = ObstacleSet()
        self._obstacle_set.setNavMeshFile(self._attributes['file_name'])
        self._obstacle_set.setClassId(self._attributes['class'])
        return self._obstacle_set        
        

if __name__ == '__main__' :
    import yaml
    f = open('test.yaml')
    y = yaml.load(f, yaml.SafeLoader)
    condition = TransitionYAML()
    condition.load(y['test'][0])
    print(condition.getAttributes())