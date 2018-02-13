#!/usr/bin/python

import json
import logging

logging.basicConfig(level = logging.INFO)

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

    def handle_event(self, event = None, param = None):
        # Pass incoming event
        response = self.update(event, param)

        # If next state can transition with no event and no conditions, continue
        logging.debug("Checking for auto transitions")
        while self.current_state.is_auto_transitioning():
            logging.info("Auto transitioning")
            response = self.update()

        return response # Return last response

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
            if transition.check(event, param):
                return transition.go(param)
        logging.warning("No matching event handlers found")
        return Response(state = self.name, message = "Invalid event", success = False)

    def is_auto_transitioning(self):
        for transition in self.transitions:
            if transition.check(None, None):
                return True
        return False

    def __str__(self):
        return self.name

class Transition:
    def __init__(self, event = None, condition = None, to_state = None, action = None):
        self.event = event
        self.condition = Action(**condition) if condition else None
        self.to_state = to_state
        self.action = Action(**action) if action else None
        logging.debug("Added transition {}".format(self))

    def check(self, event, param):
        logging.debug("Checking transition {} against {} ({})".format(str(self), event, param))
        if event == self.event:
            if not self.condition:
                logging.debug("No condition, OK")
                return True
            else:
                result = self.condition.execute(param)
                logging.debug("Checking condition {} ({}): {}".format(self.condition, param, result))
                return result
        return False

    def go(self, param):
        action_result = self.action.execute(param) if self.action else None
        return Response(state = self.to_state, message = action_result, success = True)

    def __str__(self):
        return "@{} [{}]: -> {} & {}".format(self.event, self.condition, self.to_state, self.action)

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

