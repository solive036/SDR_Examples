"""
Simulate a noisy signal and what effects this has on the received signal
"""
from PyQt6.QtWidgets import QVBoxLayout, QHBoxLayout, QLabel, QMainWindow, QWidget, QApplication, QDoubleSpinBox
from PyQt6.QtCore import QObject, pyqtSignal, QThread, QTimer
import numpy as np
import pyqtgraph as pg
import sys
import time


class SDR_Worker(QObject):
    def __init__(self):
        super().__init__()
        self.buffer_size = 512
        self.rx_samples = np.zeros(self.buffer_size)
        self.fc = 1 #frequency of sinusoidal signal
        self.sample_rate = 50 #samples per second 
        self.time_vector = np.arange(0, self.buffer_size)/self.sample_rate
        self.freq_vector = np.fft.fftshift(np.fft.fftfreq(self.buffer_size, 1/self.sample_rate))
        self.noise_sigma = 0.0 #changes the amount of noise, std deviation of Gaussian noise

    plot_update = pyqtSignal(np.ndarray)
    psd_update = pyqtSignal(np.ndarray, np.ndarray)
    end_of_run = pyqtSignal()

    def update_noise(self, noise_sigma):
        self.noise_sigma = noise_sigma

    def run(self):
        while True:
            time.sleep(0.1) #time between displayed frames, change to less time for faster simulation
            waveform = np.sin(2*np.pi*self.fc*self.time_vector) #simulate sine waveform
            noise = np.random.normal(0, self.noise_sigma, self.buffer_size) #simulate noise
            rx_samples = noise + waveform #add the noise to the signal
            psd = 10*np.log10(np.fft.fftshift(np.abs(np.fft.fft(rx_samples)**2)/len(rx_samples)))
            self.time_vector += self.buffer_size / self.sample_rate
            self.psd_update.emit(psd, self.freq_vector)
            self.plot_update.emit(rx_samples)
            self.end_of_run.emit()

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        # Initialize SDR thread
        self.sdr_thread = QThread()
        self.worker = SDR_Worker()
        self.worker.moveToThread(self.sdr_thread)

        ### GUI Setup
        self.setWindowTitle('Noise Simulation')
        main_layout = QVBoxLayout()  # Use a vertical layout for the main window
        options_layout = QHBoxLayout()

        #setup the slider for noise level
        label = QLabel('Noise Level: ')
        noise_value = QDoubleSpinBox()
        noise_value.setRange(0, 5)
        noise_value.setSingleStep(0.1)
        options_layout.addWidget(label)
        options_layout.addWidget(noise_value)
        noise_value.valueChanged.connect(lambda: self.worker.update_noise(noise_value.value()))

        # Setup the time plot
        plot = pg.PlotWidget(labels={'top':'Signal in Time','left': 'Amplitude', 'bottom': 'Time'})
        plot.setYRange(-1.5, 1.5)
        self.c1 = plot.plot()  # Initialize plot with an empty data set

        #setup the PSD plot
        psd_plot = pg.PlotWidget(labels={'top':'Power Spectral Density','left':'Amplitude', 'bottom':'Frequency'})
        psd_plot.setYRange(-40, 30)
        self.c2 = psd_plot.plot()

        #add plot widgets to main layout
        main_layout.addLayout(options_layout)
        main_layout.addWidget(plot)  
        main_layout.addWidget(psd_plot)
        central_widget = QWidget(self)
        central_widget.setLayout(main_layout)
        self.setCentralWidget(central_widget)

        # Define callbacks
        def plot_callback(data):
            self.c1.setData(data) 

        def psd_callback(data, freq_vector):
            self.c2.setData(freq_vector, data)

        def end_of_run_callback():
            QTimer.singleShot(0, self.worker.run)
        

        # Connect signals to slots
        self.worker.plot_update.connect(plot_callback)
        self.worker.psd_update.connect(psd_callback)
        self.worker.end_of_run.connect(end_of_run_callback) 
        self.sdr_thread.started.connect(self.worker.run)
        self.sdr_thread.start()


if __name__ == '__main__':
    print('Starting GUI')
    app = QApplication([])
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
