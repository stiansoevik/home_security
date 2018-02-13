#!/usr/bin/python
# TODO Support multiple transitions? How should responses work etc?
# TODO Store PIN outside configuration file?
# TODO Support configurable log levels
# TODO Explicit transition priority?

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

    def update(self, event = None, param = None):
        response = self.current_state.handle_event(event, param)
        logging.info(str(response))
        if response.success:
            self.set_state(response.state)
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
                if transition.check_condition(param):
                    return transition.go(param)
        logging.warning("No matching event handlers found")
        return Response(state = self.name, message = "Invalid event", success = False)

    def __str__(self):
        return self.name

class Transition:
    def __init__(self, event = None, condition = None, to_state = None, action = None):
        logging.debug("Creating transition @{} [{}] -> {}, {}".format(event, condition, to_state, action))
        self.event = event
        self.condition = Action(**condition) if condition else None
        self.to_state = to_state
        self.action = Action(**action) if action else None

    def check_condition(self, param):
        if not self.condition:
            logging.debug("No condition, OK")
            return True
        else:
            result = self.condition.execute(param)
            logging.debug("Checking condition {} ({}): {}".format(self.condition, param, result))
            return result

    def go(self, param):
        action_result = self.action.execute(param) if self.action else None
        return Response(state = self.to_state, message = action_result, success = True)

    def __str__(self):
        return "@{} [{}]: -> {}".format(self.event, self.condition, self.to_state.name)

class Response:
    def __init__(self, state = None, message = None, success = None):
        self.state = state
        self.message = message
        self.success = success

    def __str__(self):
        return "Response: state: {}, message: {}, success: {}".format(self.state, self.message, self.success)

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

