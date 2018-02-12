import flask
import state_machine

app = flask.Flask(__name__)
sm = state_machine.StateMachine()

@app.route('/send_event/<event>', methods = ['POST'])
def send_event(event):
    if flask.request.is_json:
        param = flask.request.get_json().get('param')
    else:
        param = None
    result = sm.update(event, param)
    return result.response_text or "No response"


