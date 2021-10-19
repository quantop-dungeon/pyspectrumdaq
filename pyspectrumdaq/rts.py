from typing import Union
from time import time

from multiprocessing import Process
from multiprocessing import Value
from multiprocessing import Array

import numpy as np
from numpy.fft import fftfreq  # TODO: replace this with manual calculation

import numba
import pyfftw

import pyqtgraph as pg
from pyqtgraph.Qt import QtCore
from pyqtgraph.Qt import QtGui

from .rtsui import Ui_RtsWidget

from .card import Card
#from dummy_card import DummyCard as Card

def daq(settings: dict, buff, buff_acc, buff_t, cnt, navg, navg_completed, stop_flag) -> None:
    """ Starts continuous data streaming from the card. """
    
    lbuff = len(buff)  # The number of buffered traces.
    nf = len(buff[0])  # The number of frequency axis bins.

    ntds = len(buff_t[0])  # The number of samples in the time-domain buffer.

    navg_rt = settings.pop("naverages_rt")
    trig_mode = settings.pop("trig_mode")

    cnt.value = 0  # The number of acquired traces is this value times TODO: navg_rt
    navg_completed.value = 0

    # Represents the buffers as a numpy arrays.
    npbuff = [np.frombuffer(a.get_obj()) for a in buff]
    npbuff_acc = np.frombuffer(buff_acc)
    npbuff_t = [np.frombuffer(a) for a in buff_t]

    # Auxiliary arrays for the calcualtion of FFT.
    nsamples = 2 * (nf - 1)
    a = pyfftw.empty_aligned(2 * (nf - 1), dtype="float64")
    b = pyfftw.empty_aligned(nf, dtype="complex128")
    
    calc_fft = pyfftw.FFTW(a, b, flags=["FFTW_ESTIMATE"])
    # Using FFTW_ESTIMATE flag significantly reduces startup time at 
    # the expense of a less than 5 % reduction in speed.
    
    y = np.zeros(nf, dtype=np.float64)   # Abs spectrum squared.

    with Card() as adc:
        adc.set_acquisition(**settings)
        adc.set_trigger(trig_mode)

        i = 0  # The index inside the main buffer.
        j = 0  # The fast accumulation counter.

        dt_trace = nsamples / adc.samplerate  # The time of one trace.
        dt_not = 15  # Notification interval (seconds).

        start_time = time()
        prev_not_time = start_time

        for data in adc.fifo():
            a[:] = data[:, 0]
            calc_fft()
            calc_abs_square(y, b)
            # Now there is a new absolute squared FFT result stored in y.

            if j == 0:
                buff[i].acquire()
                npbuff[i][:] = y
            else:
                add_array(npbuff[i], y)

            j += 1

            if j == navg_rt:
                now = time()

                # Updates the time domain data.
                npbuff_t[i][:] = data[: ntds, 0]

                # Releases the buffer lock so that the new spectrum and time
                # domain data can be read by the ui process.
                buff[i].release()

                # Increments the counter of acquired traces and the index within the buffer.
                cnt.value += 1
                i = (cnt.value % lbuff)

                # Resets the fast averaging counter.
                j = 0

                delay = (now - start_time) - navg_rt * cnt.value * dt_trace
                if delay > 0 and (now - prev_not_time) > dt_not:
                    # Prints how far it is from real-time prformance.
                    print(f"The data reading is behind real time by (s): {delay}")
                    prev_not_time = now

            # Adds the trace to the accumulator buffer, which is independent of the fast averaging.
            navg_c = navg.value
            cmpl_c = navg_completed.value

            if cmpl_c < navg_c:
                if cmpl_c == 0:
                    npbuff_acc[:] = y
                else:
                    add_array(npbuff_acc, y)

                navg_completed.value += 1

            # Checks if there has been a command to stop and exit.
            if stop_flag.value:
                cnt.value = 0
                break


class RtsWindow(QtGui.QMainWindow):

    tdds: int = 100  # The shrinking factor for time-domain data.

    def __init__(self, card_settings: Union[dict, None] = None) -> None:
        super().__init__()
        self.createUi()

        self.daq_proc = None  # A reference to the data acquisition process.
        self.current_settings = None  # The settings of the process.

        # Shared variables for interprocess communication.
        self.navg = Value("i", 0, lock=False)
        self.navg_completed = Value("i", 0, lock=False)
        self.stop_daq_flag = Value("b", 0, lock=False)
        self.w_cnt = Value("i", 0, lock=False)

        self.r_cnt = 0

        # Number of traces to be averaged before displaying.
        self.navg_disp = 10

        self.buff = []  # List[Array]. The buffer for frequency-domain data.
        self.npbuff = []  # List[np.ndarray]. The same buffer as numpy arrays.

        self.buff_acc = None  # The buffer for averaged (accumulated) data.
        self.npbuff_acc = None

        self.buff_t = []  # List[Array]. The buffer for time-domain data.
        self.npbuff_t = []  # List[np.ndarray].

        self.show_overflow = True
        self.averging_now = False

        self.line = self.ui.plotWidget.plot()  # Real-time trace display.
        self.line.setPen((250, 0, 0))

        self.line_ref = self.ui.plotWidget.plot()  # Reference trace display.
        self.line_ref.setPen((20, 20, 20))

        self.line_td = self.ui.scopePlot.plot()  # Time domain display.
        self.line_td.setPen((126, 47, 142))

        # TODO: read the parameters below from the card.
        self.card_fullranges_mv = [10000, 10000, 10000, 10000]
        self.card_terminations = ["1M", "1M", "1M", "1M"]
        # Other card settings are stored in UI controls, but these have
        # dedicated attributes because only one channel is displayed in UI
        # at a time.

        if not card_settings:

            # Use default settings.
            card_settings = {"mode": "fifo_single",
                             "channels": (0,),
                             "fullranges": (10,),
                             "terminations": ("1M",),
                             "samplerate": 30e6,
                             "nsamples": 409600,
                             "trig_mode": "soft",
                             "naverages_rt": self.navg_disp}

        self.set_settings_to_ui(card_settings)

        self.xfd = None
        self.yfd_ref = None
        self.xtd = None

        self.updateTimer = QtCore.QTimer()
        self.updateTimer.timeout.connect(self.update_plot)
        self.updateTimer.start(0)

    def createUi(self):
        """Sets up the user interface."""
        self.setWindowTitle("Spectrum Analyzer")
        self.resize(1500, 800)

        self.ui = RtsWidget()
        self.setStyleSheet(self.ui.styleSheet())  
        # Uses the widget stylesheet for the entire window.

        self.setCentralWidget(self.ui)

        # Connects the control panel.
        self.ui.channelComboBox.currentIndexChanged.connect(self.on_channel_change)

        self.ui.fullrangeComboBox.currentIndexChanged.connect(self.on_channel_param_change)
        self.ui.terminationComboBox.currentIndexChanged.connect(self.on_channel_param_change)

        self.ui.trigmodeComboBox.currentIndexChanged.connect(self.start_daq)

        self.ui.samplerateLineEdit.editingFinished.connect(self.start_daq)
        self.ui.nsamplesLineEdit.editingFinished.connect(self.start_daq)

        self.ui.averagePushButton.clicked.connect(self.start_averaging)
        self.ui.naveragesLineEdit.editingFinished.connect(self.set_navg)

    def closeEvent(self, event):
        """Executed when the window is closed. This is an overloaded Qt method.
        """
        del event  # Unused but required by the signature.
        self.stop_daq()

    def update_plot(self):
        lbuff = len(self.buff)
        w_cnt = self.w_cnt.value  # The counter value of the writing process.

        if w_cnt > self.r_cnt and lbuff > 0:

            if w_cnt - self.r_cnt >= lbuff and self.show_overflow:
                print("Interprocess buffer overflow.")
                self.show_overflow = False

            i = self.r_cnt % lbuff

            self.buff[i].acquire()
            yfd = self.npbuff[i].copy()
            ytd = self.npbuff_t[i].copy()
            self.buff[i].release()

            self.r_cnt += 1

            # Updates the frequency domain display.
            divide_array(yfd, self.navg_disp)
            self.line.setData(self.xfd, yfd)

            # Updates the time domain display.
            self.line_td.setData(self.xtd, ytd)

        if self.averging_now:
            navg_c = self.navg.value
            cmpl_c = self.navg_completed.value

            self.ui.averagesCompletedLabel.setText(str(cmpl_c))

            if cmpl_c >= navg_c:
                self.averging_now = False

                self.yfd_ref = self.npbuff_acc.copy()
                divide_array(self.yfd_ref, cmpl_c)

                # Displays the reference trace.
                self.line_ref.setData(self.xfd, self.yfd_ref)

    def start_daq(self):
        """Starts data acquisition in a separate process with present settings.
        """

        settings = self.get_settings_from_ui()

        if settings != self.current_settings:
            self.current_settings = settings
        else:
            # Sometimes ui elements fire signals that call this function even
            # if there has been no actual change in the card settings.
            # Such calls are discarded.
            return

        if self.daq_proc and self.daq_proc.is_alive():
            self.stop_daq()  # Terminates the existing daq process.

        sr = settings["samplerate"]
        ns = settings["nsamples"]
        nf = ns // 2 + 1  # The number of frequency bins.

        # The number of traces averaged before display.

        print(f"Averaging over {self.navg_disp} traces")

        # Inits the x axis and the plot.
        self.xfd = fftfreq(ns + 1, 1/sr)[0: nf]  # TODO: check this, the frequencies are probably off.

        # Setting x and y ranges removes autoadjustment.
        self.ui.plotWidget.setXRange(self.xfd[0], self.xfd[-1])
        self.ui.plotWidget.setYRange(1e-20, 10)

        self.xtd = np.linspace(0, ns / sr, ns // self.tdds)

        rng = settings["fullranges"][0]  # TODO: this is not correct.
        self.ui.scopePlot.setXRange(0, ns / sr) # TODO: this is not very correct.
        self.ui.scopePlot.setYRange(-rng, rng)

        lbuff = 10  # The number of traces in the interprocess buffer.

        # Allocates a shared buffer for time-domain data.
        self.buff = [Array("d", nf, lock=True) for _ in range(lbuff)]
        self.npbuff = [np.frombuffer(a.get_obj()) for a in self.buff]
        # This buffer is completely responsible for synchronization, all other
        # shared buffers do not have their own locks.

        self.buff_acc = Array("d", nf, lock=False)
        self.npbuff_acc = np.frombuffer(self.buff_acc)

        self.buff_t = [Array("d", int(ns // self.tdds), lock=False) for _ in range(lbuff)]
        self.npbuff_t = [np.frombuffer(a) for a in self.buff_t]

        # daq(settings, buff, buff_acc, buff_t, ind, navg, avg_completed, stop_flag)
        self.daq_proc = Process(target=daq,
                                args=(settings, self.buff, self.buff_acc, self.buff_t,
                                      self.w_cnt, self.navg, self.navg_completed,
                                      self.stop_daq_flag),
                                daemon=True)
        self.daq_proc.start()

        # TODO: here, it would be appropriate to receive a response from the
        # daq card with the actual values of parameters that have been set.

    def stop_daq(self):

        # Tells the daq process to finish, waits until it does, and resets the flag.
        self.stop_daq_flag.value = True
        self.daq_proc.join()
        self.stop_daq_flag.value = False

        del self.buff[:]
        del self.npbuff[:]

        del self.buff_acc
        del self.npbuff_acc

        # Sets the read counter to zero.
        self.r_cnt = 0

        self.averging_now = False

    def start_averaging(self):
        self.set_navg()
        self.averging_now = True

        # This tells the daq process to re-start averaging.
        self.navg_completed.value = 0

    def get_settings_from_ui(self) -> dict:
        """Gets card settings from the user interface."""

        trig_mode = self.ui.trigmodeComboBox.currentData().lower()

        if trig_mode.startswith("ext"):
            card_mode = "fifo_multi"
        else:
            card_mode = "fifo_single"

        ch = self.ui.channelComboBox.currentData()
        frng = self.ui.fullrangeComboBox.currentData() / 1000  # The item data is in mV.
        term = self.ui.terminationComboBox.currentData()

        settings = {"mode": card_mode,
                    "channels": (ch,),
                    "fullranges": (frng,),
                    "terminations": (term,),
                    "samplerate": int(float(self.ui.samplerateLineEdit.text())),
                    "nsamples": int(float(self.ui.nsamplesLineEdit.text())),
                    "trig_mode": trig_mode,
                    "naverages_rt": self.navg_disp}

        return settings

    def set_settings_to_ui(self, settings: dict) -> None:
        """Displays card settings in the user interface."""

        with NoSignals(self.ui.samplerateLineEdit) as uielem:
            uielem.setText("%i" % settings["samplerate"])

        with NoSignals(self.ui.nsamplesLineEdit) as uielem:
            uielem.setText("%i" % settings["nsamples"])

        with NoSignals(self.ui.channelComboBox) as uielem:
            ch = settings["channels"][0]
            uielem.setCurrentIndex(ch)

        with NoSignals(self.ui.fullrangeComboBox) as uielem:
            fr_mv = int(1000 * settings["fullranges"][0])   # Full range in mV.

            ind = uielem.findData(fr_mv) 
            uielem.setCurrentIndex(ind)

            self.card_fullranges_mv[ch] = fr_mv

        with NoSignals(self.ui.terminationComboBox) as uielem:
            term = settings["terminations"][0]

            ind = uielem.findData(term)
            uielem.setCurrentIndex(ind)

            self.card_terminations[ch] = term

        with NoSignals(self.ui.trigmodeComboBox) as uielem:
            ind = uielem.findData(settings["trig_mode"])
            uielem.setCurrentIndex(ind)

    def on_channel_change(self):
        ch = self.ui.channelComboBox.currentData()

        with NoSignals(self.ui.fullrangeComboBox) as uielem:
            ind = uielem.findData(self.card_fullranges_mv[ch])
            uielem.setCurrentIndex(ind)

        with NoSignals(self.ui.terminationComboBox) as uielem:
            ind = uielem.findData(self.card_terminations[ch])
            uielem.setCurrentIndex(ind)

        self.start_daq()

    def on_channel_param_change(self):
        ch = self.ui.channelComboBox.currentData()

        self.card_fullranges_mv[ch] = self.ui.fullrangeComboBox.currentData()
        self.card_terminations[ch] = self.ui.terminationComboBox.currentData()

        print(self.card_fullranges_mv)
        print(self.card_terminations)

        self.start_daq()

    def set_navg(self):
        navg = int(self.ui.naveragesLineEdit.text())

        if self.navg.value != navg:
            self.navg.value = navg


class RtsWidget(QtGui.QWidget, Ui_RtsWidget):
    """The widget that contains the user interface."""

    def __init__(self) -> None:
        super().__init__()
        self.setupUi(self)

        self.trigmodeComboBox.clear()
        self.trigmodeComboBox.addItem("Software", "soft")
        self.trigmodeComboBox.addItem("External", "ext")

        self.terminationComboBox.clear()
        self.terminationComboBox.addItem("1 MOhm", "1M")
        self.terminationComboBox.addItem("50 Ohm", "50")

        with Card() as adc:
            nchannels = adc._nchannels
            valid_fullranges_mv = adc._valid_fullranges_mv

        self.channelComboBox.clear()
        for i in range(nchannels):
            self.channelComboBox.addItem(str(i), i)

        self.fullrangeComboBox.clear()
        for r in valid_fullranges_mv:
            self.fullrangeComboBox.addItem("%g" % (r/1000), r) 

        self.plotWidget.setBackground("w")
        self.plotWidget.setLabel("left", "PSD", units="")
        self.plotWidget.setLabel("bottom", "Frequency", units="Hz")
        self.plotWidget.showAxis("right")
        self.plotWidget.showAxis("top")
        self.plotWidget.getAxis("top").setStyle(showValues=False)
        self.plotWidget.getAxis("right").setStyle(showValues=False)

        self.plotWidget.plotItem.setLogMode(False, True)  # Log y.
        self.plotWidget.plotItem.showGrid(True, True)

        self.scopePlot.setBackground("w")
        self.scopePlot.setLabel("left", "Signal", units="V")
        self.scopePlot.setLabel("bottom", "Time", units="s")
        self.scopePlot.showAxis("right")
        self.scopePlot.showAxis("top")
        self.scopePlot.getAxis("top").setStyle(showValues=False)
        self.scopePlot.getAxis("right").setStyle(showValues=False) 

        # TODO: add frame, remove axes for the time domain plot.


def rts():
    """Starts a real-time spectrum analyzer."""

    # Same as app = QtGui.QApplication(*args) with optimum parameters
    app = pg.mkQApp()

    mw = RtsWindow()
    mw.show()

    mw.start_daq()

    QtGui.QApplication.instance().exec_()


class NoSignals:
    """A context manager class that blocks signals from QObjects."""

    def __init__(self, uielement) -> None:
        self.uielement = uielement

    def __enter__(self):
        self.uielement.blockSignals(True)
        return self.uielement

    def __exit__(self, *a):
        self.uielement.blockSignals(False)


@numba.jit(nopython=True, parallel=True)
def add_array(a, b):
    """a = a + b 

    Adds two 1D arrays `b` and `a` element-wise and stores the result in `a`.
    """
    for i in numba.prange(a.shape[0]):
        a[i] = a[i] + b[i]


@numba.jit(nopython=True, parallel=True)
def calc_abs_square(a, b):
    """a = abs(b * b)

    Calculates absolute squares of the elements of a 1D array `b` and stores 
    the result in `a`.
    """
    for i in numba.prange(a.shape[0]):
        a[i] = abs(b[i] * b[i])


@numba.jit(nopython=True, parallel=True)
def divide_array(a, c):
    """a = a / c 

    Divides the elements of a 1D array `a` by a constant factor `c` and stores 
    the result in `a`.
    """
    for i in numba.prange(a.shape[0]):
        a[i] = a[i] / c
