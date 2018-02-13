#!/usr/bin/python

import argparse
import flask
import logging
import state_machine

logging.basicConfig(level = logging.INFO)

app = flask.Flask(__name__)
sm = None

@app.route('/send_event/<event>', methods = ['POST'])
def send_event(event):
    if flask.request.is_json:
        param = flask.request.get_json().get('param')
    else:
        param = None

    response = sm.handle_event(event, param)

    if response.success: # Success is defined as state machine updated successfully, not e.g. correct PIN
        code = 200
    else:
        code = 400

    return flask.json.jsonify(state=response.state, message=response.message), code

def main():
    parser = argparse.ArgumentParser(description = "State machine server")
    parser.add_argument('--config', help = "Configuration file")
    args = parser.parse_args()

    global sm
    if args.config:
        sm = state_machine.StateMachine(config_file = args.config)
    else:
        sm = state_machine.StateMachine()

    app.run()

if __name__ == '__main__':
    main()
