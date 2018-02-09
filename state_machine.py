#!/usr/bin/python
import json
import pprint

class StateMachine:
    def __init__(self, config_file = 'state_machine_config.json'):
        self.states = []
        self.sm_dict = self.load(config_file)

    def load(self, config_file):
        with open(config_file) as file:
            config_dict = json.loads(file.read())

        # Create all states first, so transitions can find a valid state
        self.states = [State(name) for name in config_dict.get('states', [])]

        # Add properties
        for state_name, properties in config_dict.get('states', []).iteritems():
            from_state = self.find_state(state_name)
            for t in properties.get('transitions', []):
                transition = Transition(
                        event = t.get('event'),
                        condition = t.get('condition'),
                        to_state = self.find_state(t.get('to_state'))
                        )
                from_state.add_transition(transition)

    def find_state(self, name = None):
        if name:
            return [s for s in self.states if s.name == name][0] or None
        return None

    def __str__(self):
        return "\n".join([str(s) for s in self.states])


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
print(sm)
