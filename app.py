from flask import Flask, send_from_directory
import os
from flask_socketio import send, emit, SocketIO
from Queue import Queue
from threading import Thread
import time
import requests

serviceAQueue = Queue(maxsize=0)
serviceBQueue = Queue(maxsize=0)

app = Flask(__name__, static_url_path="/static")
app.config['SECRET_KEY'] = 'sesdfasdfascret!'
socketio = SocketIO(app)

@app.route('/')
def index():
    return send_from_directory('static', 'index.html')

@app.route('/health')
def health():
    return 'healthy'

def tick(data):
    socketio.emit('tick', data)

def ping(queue, url):
    while True:
        t0 = time.time()
        r = requests.get(url)
        t1 = time.time()
        queue.put((t1-t0, r.text))
    
def count(tick_func, q_a, q_b):
    while True:
        time.sleep(3)

        count_a = 0
        max_a = q_a.qsize()
        result_a = []
        while count_a < max_a:
            try:
                result_a.append(q_a.get_nowait())
                count_a += 1
            except Empty, e:
                break

        count_b = 0
        max_b = q_b.qsize()
        result_b = []
        while count_b < max_b:
            try:
                result_a.append(q_b.get_nowait())
                count_b += 1
            except Empty, e:
                break

        avg_a = 0
        response_a = []
        for element in result_a:
            avg_a += element[0]
            response_a.append(element[1])

        avg_a = float(avg_a) / float(result_a.size())

        avg_b = 0
        response_b = []
        for element in result_b:
            avg_b += element[0]
            response_b.append(element[1])

        avg_b = float(avg_b) / float(result_b.size())

        tick_func({'avg_a': [avg_a], 'avg_b': [avg_b], 'response_a': response_a, 'response_b': response_b})



if __name__ == '__main__':
    for i in range(20):
        worker = Thread(target=ping, args=(serviceAQueue, "http://service-a-trex-demo-prod.router.default.svc.cluster.local/demo"),)
        worker.setDaemon(True)
        worker.start()

    for i in range(20):
        worker = Thread(target=ping, args=(serviceBQueue, "http://service-b-trex-demo-prod.router.default.svc.cluster.local/demo"),)
        worker.setDaemon(True)
        worker.start()

    counter = Thread(target=count, args=(tick, serviceAQueue, serviceBQueue, ))
    counter.setDaemon(True)
    counter.start()

    socketio.run(app, host='0.0.0.0', port=8080)
    #app.run(debug=False,host='0.0.0.0',port=8080)

