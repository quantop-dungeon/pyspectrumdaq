import time

from numpy import dtype
from numpy.random import random

class DummyCard:
    """A class for simulating real-time data streaming."""

    def __init__(self, *args, **kwargs):
        print("Using a dummy card.")

        self._valid_fullranges_mv = [200, 500, 1000, 2000, 5000, 10000]
        self._nchannels = 4

    def __enter__(self):
        return self

    def __exit__(self, *a):
        pass

    def set_acquisition(self, **kwargs):
        self.samplerate = int(kwargs["samplerate"])
        self.nchannels = len(kwargs["channels"])
        self.nsamples = int(kwargs["nsamples"])

        print("Acquisition settings:")
        print(kwargs)

    def set_trigger(self, *args, **kwargs):
        print("Trigger settings:")
        print(args)
        print(kwargs)

    def fifo(self, convert=True):
        """Generates random traces while emulating the delays of real-time data 
        acquisition by the card."""

        # The sampling time of one trace (seconds).
        dt_trace = self.nsamples / self.samplerate

        cnt = 0  # The trace counter.

        start_time = time.time()
        while True:
            data = random((self.nsamples, self.nchannels))
            cnt += 1

            now = time.time()
            delay = cnt * dt_trace - (now - start_time)
            if delay > 0:
                time.sleep(delay)

            yield data