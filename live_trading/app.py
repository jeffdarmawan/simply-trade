from flask import Flask, request
import threading, time
from trade import Status, trade_attempt

class LiveTrading:
    def __init__(self):
        self.thread = None
        self.status = Status.Inactive
        self.status_lock = threading.Lock()

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
            trade_attempt(status=self.status)
                
            
            time.sleep(2)

    def get_status(self):
        with self.status_lock:
            return self.status

    def set_status(self, new_status: Status):
        with self.status_lock:
            self.status = new_status

    def start(self, params):
        while True:
            print("current status: ", self.get_status())
            # if self.get_status() == Status.Active:
            # print(f"Thread ID: {threading.get_ident()}")
            # print(a)
            # a += 1
            trade_attempt(
                take_profit=params['tp'],
                stop_loss=params['sl'],
                status=self.status)
                
            
            time.sleep(2)



# app function for waitress
def create_app():
    app = Flask(__name__)

    ltrading = LiveTrading()

    @app.route('/activate', methods=['POST'])
    def activate():
        # custom tp/sl
        tp = request.json.get('tp')
        sl = request.json.get('sl')

        ltrading.set_status(Status.Active)
        ltrading.start(params={'tp': tp, 'sl': sl})

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