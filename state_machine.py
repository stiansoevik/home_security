#!/usr/bin/python
import json
import pprint

class StateMachine:
    def __init__(self, config_file = 'state_machine_config.json'):
        self.sm_dict = self.load(config_file)

    def load(self, config_file):
        print('Loading {}'.format(config_file))
        with open(config_file) as file:
            config_dict = json.loads(file.read())
        pprint.pprint(config_dict)
        return config_dict

class State:
    def __init__(self, name):
        self.name = name
        self.transitions = []

    def add_transition(self, transition):
        self.transitions.append(transition)

    def __str__(self):
        return "{}:\n{}".format(self.name, "\n".join([str(s) for s in self.transitions]))

class Transition:
    def __init__(self, event = None, condition = None, to_state = None):
        self.event = event
        self.condition = condition
        self.to_state = to_state

    def __str__(self):
        return "@{} [{}]: -> {}".format(self.event, self.condition, self.to_state.name)

sm = StateMachine()

disarmed_state = State("DISARMED")
armed_state = State("ARMED")

arm_transition = Transition(to_state = armed_state)
disarm_transition = Transition(to_state = disarmed_state)

disarmed_state.add_transition(arm_transition)
armed_state.add_transition(disarm_transition)

print(disarmed_state)
