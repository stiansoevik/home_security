#!/usr/bin/python
import json
import logging

logging.basicConfig(level = logging.DEBUG)

class StateMachine:
    def __init__(self, config_file = 'state_machine_config.json'):
        logging.debug("Initializing state machine")
        self.states = []
        self.current_state = None
        self.sm_dict = self.load(config_file)

    def load(self, config_file):
        logging.debug("Loading {}".format(config_file))
        with open(config_file) as file:
            config_dict = json.loads(file.read())

        # Create all states first, so transitions can find a valid state
        logging.debug("Creating states")
        self.states = [State(name) for name in config_dict.get('states', [])]

        logging.debug("Adding properties to states")
        for state_name, properties in config_dict.get('states', []).iteritems():
            from_state = self.find_state(state_name)
            for t in properties.get('transitions', []):
                transition = Transition(
                        event = t.get('event'),
                        condition = t.get('condition'),
                        to_state = self.find_state(t.get('to_state'))
                        )
                from_state.add_transition(transition)
            # TODO Consider entry events

        initial_state = config_dict.get('initial_state')
        logging.debug("Initial state: {}".format(initial_state))
        self.set_state(self.find_state(initial_state))

    def set_state(self, state):
        logging.info("Transitioning from {} to {}".format(self.current_state, state))
        self.current_state = state

    def update(self, event, param = None):
        response = self.current_state.handle_event(event, param)
        self.set_state(response.next_state)
        return response

    def handle_actions(self, actions):
        if 'log' in actions:
            print("LOG: {}".format(actions.log))

    def find_state(self, name = None):
        if name:
            return [s for s in self.states if s.name == name][0] or None
        return None

    def __str__(self):
        return "State machine with states: " + ", ".join([str(s) for s in self.states])


class State:
    def __init__(self, name):
        self.name = name
        self.transitions = []

    def add_transition(self, transition):
        self.transitions.append(transition)

    def handle_event(self, event, param = None):
        logging.info("Handling event: {}".format(event))
        for transition in self.transitions:
            if transition.event == event:
                # Move condition checking etc to Transition class?
                logging.debug("Event {} found, checking condition {}".format(event, transition.condition))
                if not transition.condition:
                    logging.debug("No condition, OK")
                    return TransitionResult(next_state = transition.to_state)
                else:
                    logging.debug("Checking condition {}".format(transition.condition))
                    if transition.condition.execute():
                        logging.debug("Condition satisfied")
                        return TransitionResult(next_state = transition.to_state)
                    else:
                        logging.debug("Condition not satisfied")
                        # No return, continuing to next transition

                result = self.handle_actions
                # handle_event: finn passende event, sjekk conditions
                # transist (?): utf0r transisjonsaction, bytt tilstand
                # Transition.check_condition(param)?
                # Transition.do_action?

    def __str__(self):
        return self.name

class Transition:
    def __init__(self, event = None, condition = None, to_state = None):
        self.event = event
        self.condition = condition
        self.to_state = to_state

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

    def do(param):
        if self.log:
            logging.info(self.log)
        if self.validate_code:
            return self.validate_code == param
        if self.send_response:
            return 

sm = StateMachine()
sm.update("ARM")
sm.update("USER_CODE", 1234)
