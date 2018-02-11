#!/usr/bin/python
import json
import logging

logging.basicConfig(level = logging.DEBUG)

class StateMachine:
    def __init__(self, config_file = 'state_machine_config.json'):
        logging.info("Initializing state machine")
        self.states = {}
        self.current_state = None
        self.load(config_file)

    def load(self, config_file):
        logging.info("Loading configuration from file {}".format(config_file))
        with open(config_file) as file:
            config_dict = json.loads(file.read())
        for name, properties in config_dict.get('states').iteritems():
            logging.debug("Adding state {} with properties {}".format(name, properties))
            state = State(name)
            state.transitions = [Transition(**transition_dict) for transition_dict in properties.get('transitions', [])]
            self.states[name] = state
        self.set_state(config_dict.get('initial_state'))

    def set_state(self, state):
        logging.info("Transitioning from {} to {}".format(self.current_state, state))
        self.current_state = self.states[state]

    def update(self, event, param = None):
        response = self.current_state.handle_event(event, param)
        self.set_state(response.next_state)
        return response

    def __str__(self):
        return "State machine with states: " + ", ".join([str(s) for s in self.states])

class State:
    def __init__(self, name):
        logging.debug("Creating state {}".format(name))
        self.name = name
        self.transitions = []

    def handle_event(self, event, param = None):
        logging.info("Handling event: {}".format(event))
        for transition in self.transitions:
            if transition.event == event:
                if transition.check_condition():
                    return transition.go()
        logging.warning("No matching event handlers found")

    def __str__(self):
        return self.name

class Transition:
    def __init__(self, event = None, condition = None, to_state = None, action = None):
        logging.debug("Creating transition @{} [{}] -> {}, {}".format(event, condition, to_state, action))
        self.event = event
        self.condition = Action(**condition) if condition else None
        self.to_state = to_state
        self.action = Action(**action) if action else None

    def check_condition(self):
        logging.debug("Checking condition {}".format(self.condition))
        if not self.condition:
            logging.debug("No condition")
            return True
        else:
            result = self.condition.execute(None)
            logging.debug("Condition returned {}".format(result))
            return result

    def go(self):
        action_result = self.action.execute(None) if self.action else None
        return TransitionResult(self.to_state, action_result)

    def __str__(self):
        return "@{} [{}]: -> {}".format(self.event, self.condition, self.to_state.name)

class TransitionResult:
    def __init__(self, next_state = None, response_text = None):
        self.next_state = next_state
        self.response_text = response_text

class Action:
    def __init__(self, log = None, validate_code = None, send_response = None):
        self.log = log
        self.validate_code = validate_code
        self.send_response = send_response

    def execute(self, param):
        if self.log:
            print(self.log)
            return None
        if self.validate_code:
            return self.validate_code == param
        if self.send_response:
            return self.send_response

    def __str__(self):
        return "log: {}, validate_code: {}, send_response: {}".format(self.log, self.validate_code, self.send_response)

sm = StateMachine()
sm.update("ARM")
sm.update("USER_CODE", 1234)
