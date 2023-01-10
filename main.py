from threading import Thread
import serial
import datetime
import time
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import pandas as pd

class serial_plot:
    def __init__(self, port = '/dev/ttyUSB0', baud = 115200):
        self.port = port
        self.baud = baud
        self.raw = None
        self.init_timer = 0
        self.data = []
        self.timer = []
        self.run = True
        self.receving = False
        self.thread = None
        self.csv = []

        print(f"Trying to connect to: {port} at {baud} BAUD.")
        try:
            self.serial_connection = serial.Serial(port, baud, timeout=5)
            print(f"Connected to {port} at {baud} BAUD.")
        except:
            print(f"Failed to connect with {port} at {baud} BAUD.")
            exit(1)

    def readSerialStart(self):
        if self.thread is None:
            self.thread = Thread(target=self.backgroundThread)
            self.thread.start()
            while self.receving is not True:
                time.sleep(0.01)

    def getSerialData(self, frame, ax, lines):
        current = time.perf_counter_ns() / 1000000 - self.init_timer
        if self.raw is None:
            return
        value  = float(self.raw.decode())
        self.data.append(value)
        self.timer.append(current)
        lines.set_data(self.timer, self.data)
        self.csv.append((current, self.data[-1]))
        ax.set_xlim(0, current)
        ax.set_ylim(min(self.data) * 1.1, max(self.data)*1.1)
        self.raw = None

    def backgroundThread(self):
        time.sleep(1.0)
        self.serialConnection.reset_input_buffer()
        self.init_timer = time.perf_counter_ns() / 1000000
        while (self.run):
            self.raw = self.serialConnection.readline()
            self.receving = True

    def close(self):
        self.run = False
        self.thread.join()
        self.serialConnection.close()
        print('Disconnected...')
        df = pd.DataFrame(self.csv)
        df.to_csv(f'{datetime.date.today()}.csv')


def main():
    port_name = '/dev/tty.usbserial-13440' #COM5
    baud_rate = 115200
    s = serial_plot(port_name, baud_rate)
    s.readSerialStart()
    fig = plt.figure()
    ax = plt.axes()
    ax.set_title('Loadcell Data Plotter')
    ax.set_xlabel("Second")
    ax.set_ylabel("Gram")
    lines = ax.plot([], [], label="Loadcell's Value")[0]
    anim = animation.FuncAnimation(fig, s.getSerialData, fargs=(ax, lines), interval=1)
    plt.legend(loc="upper left")
    plt.show()
    s.close()


if __name__ == '__main__':
    main()
