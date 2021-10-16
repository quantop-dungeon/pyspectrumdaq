import time

from numpy import dtype
from numpy.random import random

class DummyCard:
    """A class for simulating real-time data streaming."""

    def __init__(self, *args, **kwargs):
        print("Using a dummy card.")
        pass

    def __enter__(self):
        return self

    def __exit__(self, *a):
        pass

    def set_acquisition(self, channels = (1,), samplerate: int = 30e6,
                        nsamples: int = 300e3, **kwargs):
        self.samplerate = int(samplerate)
        self.nchannels = len(channels)
        self.nsamples = int(nsamples)

    def set_trigger(self, *args, **kwargs):
        pass

    def fifo(self, convert=True):
        """Generates random traces while emulating the delays of real-time data 
        acquisition by the card."""

        dt_not = 10  # Notification interval (seconds).

        # The sampling time of one trace (seconds).
        dt_trace = self.nsamples / self.samplerate

        cnt = 0  # The trace counter.

        start_time = time.time()
        prev_not_time = start_time
        while True:
            data = random((self.nsamples, self.nchannels))
            cnt += 1

            now = time.time()
            delay = cnt * dt_trace - (now - start_time)
            if delay > 0:
                time.sleep(delay)
            elif (now - prev_not_time) > dt_not:
                # Prints how far it is from real-time prformance.
                print(f"The card is behind real time by (s): {-delay}")
                prev_not_time = now

            yield data