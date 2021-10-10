# pyspectrumdaq
Acquire data from the Spectrum M2 DAQ cards. This module supports internal and external triggering, multi-channel acquisition, etc. Easy to use and fast by default.

Tested with M2I4931.

A simple multi-channel usage example:

```python
from pyspectrumdaq import Card

# It is recommended to use context management ("with" statement) to ensire that 
# the card is closed when communication is over.
with Card() as adc:
    adc.set_acquisition(channels=[0, 1, 2, 3], 
                        terminations=["1M", "1M", "50", "1M"], 
                        fullranges=[2, 2, 2, 2],
                        pretrig_ratio=0, 
                        nsamples=10**6,
                        samplerate=10**6)             
    adc.set_trigger(mode="soft")

    data = adc.acquire()
    # data now contains a float64 NumPy array, shaped as [nsamples, nchannels]

    t = [i/10e6 for i in range(nsamples)]  # Calculates the time axis.
```

An example of using the card in FIFO mode with a single trigger:
```python
with Card() as adc:
    adc.set_acquisition(mode = "fifo_single", 
                        channels=[0, 1], 
                        terminations=["1M", "1M"], 
                        fullranges=[2, 2],
                        pretrig_ratio=0, 
                        nsamples=10**6,
                        ntraces="inf",  # Indefinite acquisition.
                        samplerate=10**6)             
    adc.set_trigger(mode="soft")

    lim = 100  # We want to acquire 100 traces and stop.

    for cnt, data in enumerate(adc.fifo()):
        process(data)
        if cnt >= lim:
            break
```

An example of using the card in FIFO mode with one trace per trigger:
```python
with Card() as adc:
    adc.set_acquisition(mode = "fifo_multi", 
                        channels=[0, 1], 
                        terminations=["1M", "1M"], 
                        fullranges=[2, 2],
                        pretrig_ratio=0, 
                        nsamples=10**6,
                        ntraces=50,
                        samplerate=10**6)             
    adc.set_trigger(mode="ext")  # Software trigger is not allowed in this mode.

    for data in adc.fifo():
        process(data)
    # FIFO stops once 50 trace have been acquired.
```
