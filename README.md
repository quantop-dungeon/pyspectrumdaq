# pyspectrumdaq
Acquire data from the Spectrum M2 DAQ cards. This module supports internal and external triggering, multi-channel acquisition, etc. Easy to use and fast by default.

Simple multi-channel usage example:

```python
from m2i4931 import Card

# It is highly recommended to use context management ("with" statement) to make sure
# proper closing of the card
with Card() as adc:
    adc.acquisition_set(channels=[0, 1, 2, 3], 
                        terminations=["1M", "1M", "50", "1M"], 
                        fullranges=[2, 2, 2, 2],
                        pretrig_ratio=0, 
                        Ns=10**6,
                        samplerate=10**6)             
    adc.trigger_set(mode="soft")

    a = adc.acquire()
    # a now contains the data as a float64 NumPy array, shaped as [n_samples, n_channels]
```
