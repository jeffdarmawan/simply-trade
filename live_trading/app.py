from flask import Flask, request, Response
import threading, time
from trade import Status, trade_attempt

class LiveTrading:
    def __init__(self):
        self.thread = None
        self.status = Status.Inactive
        self.status_lock = threading.Lock()
        self.params = {}
        self.params_lock = threading.Lock()

    def start(self):
        if not self.thread:
            self.thread = threading.Thread(target=self.run)
            self.thread.daemon = True
            self.thread.start()

    def run(self):
        # Your infinite addition logic here
        a = 0
        while True:
            print("current status: ", self.get_status())
            # if self.get_status() == Status.Active:
            # print(f"Thread ID: {threading.get_ident()}")
            # print(a)
            # a += 1
            if self.get_status() == Status.Active:
                trade_attempt(
                    # take_profit=self.params['tp'],
                    # stop_loss=self.params['sl'],
                    status=self.status)
                
            
            time.sleep(2)

    def get_status(self):
        with self.status_lock:
            return self.status

    def set_status(self, new_status: Status):
        with self.status_lock:
            self.status = new_status

    def set_params(self, params):
        print("set params: ", params)
        with self.params_lock:
            self.params = params

# app function for waitress
def create_app():
    app = Flask(__name__)

    ltrading = LiveTrading()
    ltrading.start()

    @app.route('/activate', methods=['POST'])
    def activate():
        # custom tp/sl
        tp = request.json.get('tp')
        sl = request.json.get('sl')
        model = request.json.get('model')
        rr_ratio = request.json.get('rr_ratio')

        if ltrading.get_status() == Status.Active:
            return Response("{'error':'Cannot activate when still active'}", status=201, mimetype='application/json')

        ltrading.set_params({'tp': tp, 'sl': sl, 'model': model, 'rr_ratio': rr_ratio})
        ltrading.set_status(Status.Active)

        print("activated")
        return "Print and addition activated\n"

    @app.route('/deactivate', methods=['POST'])
    def deactivate():
        ltrading.set_status(Status.Inactive)
        print("deactivated")
        return "Print and addition deactivated\n"
    
    @app.route('/stop', methods=['POST'])
    def stop():
        ltrading.set_status(Status.Stop)
        print("stopped")
        return "Print and addition stopped\n"

    return app