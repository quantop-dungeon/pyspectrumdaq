# -*- coding: utf-8 -*-
from __future__ import print_function
from __future__ import division


import sys
import numpy as np
from scipy import signal

# import spectrum driver functions
import pyspectrumdaq.Spectrum_M2i4931_pydriver.pyspcm as sp

# Function for card name translation
def szTypeToName (lCardType):
    sName = ''
    lVersion = (lCardType & sp.TYP_VERSIONMASK)
    if (lCardType & sp.TYP_SERIESMASK) == sp.TYP_M2ISERIES:
        sName = 'M2i.%04x'%lVersion
    elif (lCardType & sp.TYP_SERIESMASK) == sp.TYP_M2IEXPSERIES:
        sName = 'M2i.%04x-Exp'%lVersion
    elif (lCardType & sp.TYP_SERIESMASK) == sp.TYP_M3ISERIES:
        sName = 'M3i.%04x'%lVersion
    elif (lCardType & sp.TYP_SERIESMASK) == sp.TYP_M3IEXPSERIES:
        sName = 'M3i.%04x-Exp'%lVersion
    elif (lCardType & sp.TYP_SERIESMASK) == sp.TYP_M4IEXPSERIES:
        sName = 'M4i.%04x-x8'%lVersion
    elif (lCardType & sp.TYP_SERIESMASK) == sp.TYP_M4XEXPSERIES:
        sName = 'M4x.%04x-x4'%lVersion
    else:
        sName = 'unknown type'
    return sName

class connect():
    # Connect to DAQ card
    def __init__(self):
        szErrorTextBuffer = sp.create_string_buffer (sp.ERRORTEXTLEN)
        dwError = sp.uint32 ();
        lStatus = sp.int32()
        lAvailUser = sp.int32()
        lPCPos = sp.int32()
        qwTotalMem = sp.uint64(0);
        qwToTransfer = sp.uint64(sp.MEGA_B(8));
        
        # open card
        self._hCard = sp.spcm_hOpen ("/dev/spcm0");
        if self._hCard == None:
            print("No card found...")
            exit()

        # read type, function and sn and check for A/D card
        lCardType = sp.int32(0)
        sp.spcm_dwGetParam_i32 (self._hCard, sp.SPC_PCITYP, sp.byref(lCardType))
        lSerialNumber = sp.int32(0)
        sp.spcm_dwGetParam_i32 (self._hCard, sp.SPC_PCISERIALNO, sp.byref(lSerialNumber))
        lFncType = sp.int32(0)
        sp.spcm_dwGetParam_i32 (self._hCard, sp.SPC_FNCTYPE, sp.byref(lFncType))

        sCardName = szTypeToName (lCardType.value)
        if lFncType.value == sp.SPCM_TYPE_AI:
            sys.stdout.write("Found: {0} sn {1:05d}\n".format(sCardName,lSerialNumber.value))
        else:
            sys.stdout.write("Card: {0} sn {1:05d} not supported by example\n".format(sCardName,lSerialNumber.value))
            exit ()

        # Acqusition and channel settings
        self.acquisition_set()

    # Close connection to DAQ card
    def close(self):
        sp.spcm_vClose(self._hCard)

    # Reset the card to default settings
    def reset(self):
        sp.spcm_dwSetParam_i32(self._hCard, sp.SPC_M2CMD, sp.M2CMD_CARD_RESET)

    '''
    Specify memory length.
    Samplerate in Hz.
    Timeout in ms.
    Specify channel number as e.g. 0, 1, 2 or 3.
    Fullrange is in mV has to be equal to one of {200,500,1000,2000,5000,10000}.
    Termination is equal to 1 for 50 Ohm and 0 for 1 MOhm
    '''            
    # Initializes acquisition settings
    def acquisition_set(self, channel=1, memorylen=300e3, samplerate=30e6, timeout=10, fullrange=200, termination=1):
        timeout *= 1e3 # Convert to ms
        self.memorylen = int(memorylen)
        self.samplerate = int(samplerate)
        
        # Factor for converting between ADC values and voltages
        self._conversion = 0
        
        # settings for the DMA buffer
        self._qwBufferSize = sp.uint64(self.memorylen * 2 * 1); # in bytes. Enough memory  samples with 2 bytes each, only one channel active
        self._lNotifySize = sp.int32(0); # driver should notify program after all data has been transfered

        # Activate channel 0
        sp.spcm_dwSetParam_i32 (self._hCard, sp.SPC_MEMSIZE,        self.memorylen)                  # acquire 16 kS in total
        sp.spcm_dwSetParam_i32 (self._hCard, sp.SPC_POSTTRIGGER,    60000)                   # half of the total number of samples after trigger event
        sp.spcm_dwSetParam_i32 (self._hCard, sp.SPC_CARDMODE,       sp.SPC_REC_STD_SINGLE)     # single trigger standard mode
        sp.spcm_dwSetParam_i32 (self._hCard, sp.SPC_TIMEOUT,        sp.int32(int(timeout)))                  # in ms
        sp.spcm_dwSetParam_i32 (self._hCard, sp.SPC_TRIG_ORMASK,    sp.SPC_TMASK_SOFTWARE)     # trigger set to software
        sp.spcm_dwSetParam_i32 (self._hCard, sp.SPC_TRIG_ANDMASK,   0)                      # ...
        #sp.spcm_dwSetParam_i32 (self._hCard, sp.SPC_CLOCKMODE,      sp.SPC_CM_INTPLL)         # clock mode internal PLL
        sp.spcm_dwSetParam_i32 (self._hCard, sp.SPC_CLOCKMODE,      sp.SPC_CM_EXTREFCLOCK)     # clock mode external reference clock
        sp.spcm_dwSetParam_i32 (self._hCard, sp.SPC_REFERENCECLOCK, 10000000);              # Reference clock that is fed in is 10 MHz
        sp.spcm_dwSetParam_i64 (self._hCard, sp.SPC_SAMPLERATE,     sp.int64(self.samplerate));              # We want to have 30 MHz as sampling rate

        # Choose channel
        g = globals()
        if channel in [0,1,2,3]:
            sp.spcm_dwSetParam_i32 (self._hCard, sp.SPC_CHENABLE,       g["CHANNEL" + str(channel)])
        else:
            raise ValueError("The specified channel is invalid")       

        # Set channel range
        if fullrange in [200,500,1000,2000,5000,10000]:
            sp.spcm_dwSetParam_i32 (self._hCard, g["sp.SPC_AMP" + str(channel)], int(fullrange));            
            maxadc = sp.int32(0)
            sp.spcm_dwGetParam_i32(self._hCard, sp.SPC_MIINST_MAXADCVALUE, sp.byref(maxadc))
            self._maxadc = maxadc.value
            self._conversion = float(fullrange)/1000 / self._maxadc
            #print("The conversion factor is {0:.2e} Volts per step".format(self._conversion))
        else:
            raise ValueError("The specified voltage range is invalid")

        if termination in [0,1]:
            sp.spcm_dwSetParam_i32 (self._hCard, g["sp.SPC_50OHM" + str(channel)], int(termination));
        else:
            raise ValueError("The specified input termination is invalid")

        # define the data buffer
        # we try to use continuous memory if available and big enough
        self._pvBuffer = sp.c_void_p ()
        self._qwContBufLen = sp.uint64(0)
        sp.spcm_dwGetContBuf_i64 (self._hCard, sp.spcm_BUF_DATA, sp.byref(self._pvBuffer), sp.byref(self._qwContBufLen))
        #sys.stdout.write ("ContBuf length: {0:d}\n".format(self._qwContBufLen.value))
        if self._qwContBufLen.value >= self._qwBufferSize.value:
            sys.stdout.write("Using continuous buffer\n")
        else:
            self._pvBuffer = sp.create_string_buffer (self._qwBufferSize.value)
            #sys.stdout.write("Using buffer allocated by user program\n")

        sp.spcm_dwDefTransfer_i64 (self._hCard, sp.spcm_BUF_DATA, sp.spcm_DIR_CARDTOPC, self._lNotifySize, self._pvBuffer, sp.uint64(0), self._qwBufferSize)


    '''
    Acquire time trace without time axis
    '''
    def acquire(self):
        # Reset buffer
        sp.spcm_dwDefTransfer_i64 (self._hCard, sp.spcm_BUF_DATA, sp.spcm_DIR_CARDTOPC, self._lNotifySize, self._pvBuffer, sp.uint64(0), self._qwBufferSize)

        # start card and DMA
        dwError = sp.spcm_dwSetParam_i32 (self._hCard, sp.M2CMD, sp.M2CMD_CARD_START |  sp.M2CMD_CARD_ENABLETRIGGER |  sp.M2CMD_DATA_STARTDMA)

        # check for error
        szErrorTextBuffer = sp.create_string_buffer (sp.ERRORTEXTLEN)
        if dwError != 0: # != ERR_OK
            sp.spcm_dwGetErrorInfo_i32 (self._hCard, None, None, szErrorTextBuffer)
            sys.stdout.write("{0}\n".format(szErrorTextBuffer.value))
            sp.spcm_vClose (self._hCard)
            exit()

        # wait until acquisition has finished, then calculated min and max
        else:
            dwError = sp.spcm_dwSetParam_i32 (self._hCard, sp.M2CMD,  sp.M2CMD_CARD_WAITREADY)
            if dwError != sp.ERR_OK:
                if dwError == sp.ERR_TIMEOUT:
                    sys.stdout.write ("... Timeout\n")
                else:
                    sys.stdout.write ("... Error: {0:d}\n".format(dwError))

            else:
                pnData = sp.cast(self._pvBuffer, sp.ptr16) # cast to pointer to 16bit integer
                # Convert the array of data into a numpy array while also converting it to volts
                #a = np.fromiter(pnData, dtype=np.int16, count=int(self._qwBufferSize.value/2)).astype(float)*self._conversion
                b = np.ctypeslib.as_array(pnData, shape=(int(self._qwBufferSize.value/2),))
                a = b.astype(float)*self._conversion

                return a

    '''
    Returns averaged power spectral density
    '''
    def PSD_avg(self,avg, progbar=False):
        if progbar:            
            from tqdm import tqdm
            ran = tqdm(range(avg))
        else:
            ran = range(avg)
            
        for jj in ran:
            # Get time trace
            a = self.acquire()

            # Calculate PSD
            f, y = signal.periodogram(a, float(self.samplerate), 'hanning')

            # Average PSD
            if jj == 0:
                psd = y
            else:
                psd += y
        return f, psd/avg

    # Get array for time
    def time(self):
        dt = 1/float(self.samplerate)
        return np.linspace(0,self.memorylen*dt,self.memorylen)

if __name__ == '__main__':
    card = connect()
    card.acquisition_set(memorylen=30e6)#, samplerate=30e6, timeout=10e3, channel=1, fullrange=200, termination=1)
    for i in range(10):
        a = card.acquire()
        print(a[0])
    t = card.time()
    card.close()
    
