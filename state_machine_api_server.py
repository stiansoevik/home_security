import flask
import logging
import state_machine

logging.basicConfig(level = logging.DEBUG)

app = flask.Flask(__name__)
sm = state_machine.StateMachine()

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


