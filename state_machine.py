#!/usr/bin/python
import json
import pprint

class StateMachine:
    def load(self, filename):
        print('Loading {}'.format(filename))
        with open(filename) as file:
            self.sm_dict = json.loads(file.read())
        pprint.pprint(self.sm_dict)

class State:


sm = StateMachine()
sm.load('state_machine_config.json')
