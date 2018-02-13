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
    response = sm.update(event, param)
    if response.success:
        code = 200
    else:
        code = 400 # TODO Consider more fine-grained response codes

    return flask.json.jsonify(state=response.state, message=response.message), code


