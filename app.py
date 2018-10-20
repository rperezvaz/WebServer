"""
WebServer Application
"""

import socketio
from flask import Flask, render_template
import aws_manager as web_server_aws_manager
import threading
import logging

logging.basicConfig(format='[%(asctime)s] [%(levelname)8s] --- %(message)s', level=logging.WARNING,
                    filename='/tmp/web_server.log')
blocked_users_echo = []
blocked_users_search = []

sio = socketio.Server(async_mode='threading')
app = Flask(__name__)
app.wsgi_app = socketio.Middleware(sio, app.wsgi_app)
aws_manager = web_server_aws_manager.Manager()


def echo(my_sio, sid, msg):
    aws_manager.set_credentials(user_id=str(sid))
    aws_manager.send_message(type_message='echo', message=msg, queue_name='inbox')
    response = aws_manager.receive_message(queue_name='outbox')
    my_sio.emit('echo', data=response.body, room=sid)
    blocked_users_echo.remove(sid)

    return


def search(my_sio, sid):
    aws_manager.set_credentials(user_id=str(sid))
    aws_manager.send_message(type_message='search', message='search', queue_name='inbox')
    response = aws_manager.receive_message(queue_name='outbox')

    if response.message_attributes[str(sid)]['StringValue'] == 'False':
        my_sio.emit('search', data=False, room=sid)
    else:
        my_sio.emit('search', data=response.body, room=sid)

    blocked_users_search.remove(sid)

    return


@sio.on('search')
def search_handler(sid):
    if sid not in blocked_users_search:
        blocked_users_search.append(sid)
        t = threading.Thread(target=search, args=[sio, sid])
        t.start()


@sio.on('echo')
def echo_handler(sid, msg):
    if sid not in blocked_users_echo:
        blocked_users_echo.append(sid)
        t = threading.Thread(target=echo, args=[sio, sid, msg])
        t.start()


@app.route('/')
def index():
    return render_template("index.html")


if __name__ == '__main__':
    app.run(threaded=True, host='0.0.0.0')
