import threading
import time


class MyThread:
    def __init__(self):
        self.stop_event = threading.Event()
        self.thread = threading.Thread(target=self.run)

    def run(self):
        print("Thread started")
        while not self.stop_event.is_set():
            time.sleep(1)
        print("Thread stopped")

    def start(self):
        self.thread.start()

    def stop(self):
        self.stop_event.set()

    def join(self):
        self.thread.join()
        print("Thread joined")


my_thread = MyThread()
my_thread.start()

# Wait for a few seconds
time.sleep(5)

# Stop the thread
my_thread.stop()
