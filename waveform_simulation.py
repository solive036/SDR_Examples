"""
Simulate a transmitted waveform, you can edit the code inside the run().
"""
from PyQt6.QtWidgets import *
from PyQt6.QtCore import *
import numpy as np
import pyqtgraph as pg
import time, sys

class Worker(QObject):
    def __init__(self):
        super().__init__()
        self.fc= 1 #Hz
        self.buffer_size = 512
        self.sample_rate = 50
        self.time_vector = np.arange(0, self.buffer_size)/self.sample_rate

    plot_update = pyqtSignal(np.ndarray)
    end_of_run = pyqtSignal()

    def run(self):
        time.sleep(0.1)
        samples = np.sin(2*np.pi*self.fc*self.time_vector)
        self.time_vector += self.buffer_size / self.sample_rate
        self.plot_update.emit(samples)
        self.end_of_run.emit()

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.worker_thread = QThread()
        self.worker = Worker()
        self.worker.moveToThread(self.worker_thread)

        ###GUI Setup
        self.setWindowTitle('Waveform Simulation')
        main_layout = QHBoxLayout()

        #setup plot
        time_plot = pg.PlotWidget()
        time_plot.setMouseEnabled(x=False, y=False)
        time_plot.setYRange(-3, 3)
        self.c1 = time_plot.plot()

        main_layout.addWidget(time_plot)
        central_widget = QWidget(self)
        central_widget.setLayout(main_layout)
        self.setCentralWidget(central_widget)

        def plot_callback(data):
            self.c1.setData(data)

        def end_of_run_callback():
            QTimer.singleShot(0, self.worker.run)

        self.worker.plot_update.connect(plot_callback)
        self.worker.end_of_run.connect(end_of_run_callback) 
        self.worker_thread.started.connect(self.worker.run)
        self.worker_thread.start()

if __name__ == '__main__':
    print('Starting GUI')
    app = QApplication([])
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
