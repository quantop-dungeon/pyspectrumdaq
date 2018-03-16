# -*- coding: utf-8 -*-
from __future__ import print_function
from __future__ import division


import sys
import numpy as np
from enum import Enum

# import spectrum driver functions
import pyspectrumdaq.Spectrum_M2i4931_pydriver.pyspcm as sp

# Some useful constants

# Terminations enum
class Term(Enum):
    TERM_50 = 0
    TERM_1M = 1

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

def chan_from_num(chan_n):
    return getattr(sp, "CHANNEL{0:d}".format(int(chan_n)))

class Card():
    def _get32(self, param, uint=False):
        if not uint:
            destination = sp.int32(0)
        else:
            destination = sp.int32(0)
        sp.spcm_dwGetParam_i32(self._hCard, param, sp.byref(destination))
        return destination
    
    def _set32(self, param, val, uint=False):
        val = int(val)
        if not uint:
            sp.spcm_dwSetParam_i32(self._hCard, param, sp.int32(val))
        else:
            sp.spcm_dwSetParam_i32(self._hCard, param, sp.uint32(val))
    
    # Connect to DAQ card
    def __init__(self):
#        szErrorTextBuffer = sp.create_string_buffer (sp.ERRORTEXTLEN)
#        dwError = sp.uint32 ();
#        lStatus = sp.int32()
#        lAvailUser = sp.int32()
#        lPCPos = sp.int32()
#        qwTotalMem = sp.uint64(0);
#        qwToTransfer = sp.uint64(sp.MEGA_B(8));
        
        # open card
        self._hCard = sp.spcm_hOpen ("/dev/spcm0");
        if self._hCard == None:
            print("No card found...")
            exit()

        # read type, function and sn and check for A/D card
        lCardType = self._get32(sp.SPC_PCITYP)
        lSerialNumber = self._get32(sp.SPC_PCISERIALNO)
        lFncType = self._get32(sp.SPC_FNCTYPE)

        sCardName = szTypeToName(lCardType.value)
        if lFncType.value == sp.SPCM_TYPE_AI:
            print("Found: {0} sn {1:05d}\n".format(sCardName,lSerialNumber.value))
        else:
            print("Card: {0} sn {1:05d} not supported by example\n".format(sCardName,lSerialNumber.value))
            exit()

        # Acqusition and channel settings
        self.acquisition_set()

    # Close connection to DAQ card
    def close(self):
        sp.spcm_vClose(self._hCard)

    # Reset the card to default settings
    def reset(self):
        sp.spcm_dwSetParam_i32(self._hCard, sp.SPC_M2CMD, sp.M2CMD_CARD_RESET)
        
    # Initialize one channel (full range in Volts)
    def ch_init(self, ch_n=1, termination=Term.TERM_1M, fullrange=10):
        # Check that the channel number if correct
        if ch_n not in range(4):
            raise ValueError("The specified channel number is invalid")
            
        # Enable that channel
        chan_param = getattr(sp, "CHANNEL{0:d}".format(int(ch_n)))
        self._set32(sp.SPC_CHENABLE, chan_param)
        
        fullrange_val = int(fullrange * 1000)
        if fullrange_val in [200,500,1000,2000,5000,10000]:
            range_param = getattr(sp, "SPC_AMP{0:d}".format(int(ch_n)))
            self._set32(range_param, fullrange_val);            
            maxadc = self._get32(sp.SPC_MIINST_MAXADCVALUE)
            self._maxadc = maxadc.value
            self._conversion = float(fullrange_val)/1000 / self._maxadc
        else:
            raise ValueError("The specified voltage range is invalid")
        
        if termination == Term.TERM_1M:
            term_val = 0
        elif termination == Term.TERM_50:
            term_val = 1
        else:
            raise ValueError("The specified termination is invalid")
            
        term_param = getattr(sp, "SPC_50OHM{0:d}".format(int(ch_n)))
        self._set32(term_param, term_val)

    '''
    Specify number of samples (per channel).
    Samplerate in Hz.
    Timeout in ms.
    Specify channel number as e.g. 0, 1, 2 or 3.
    Fullrange is in V has to be equal to one of {0.2, 0.5, 1, 2, 5, 10}.
    Termination is equal to 1 for 50 Ohm and 0 for 1 MOhm
    '''            
    # Initializes acquisition settings
    def acquisition_set(self, channel=1, Ns=300e3, samplerate=30e6, 
                        timeout=10, fullrange=10, termination=Term.TERM_1M):
        timeout *= 1e3 # Convert to ms
        self.Ns = int(Ns)
        if self.Ns % 4 != 0:
            raise ValueError("Number of samples should be divisible by 4")
        self.samplerate = int(samplerate)
        
        if Ns / samplerate >= timeout:
            raise ValueError("Timeout is shorter than acquisition time")
        
        # Factor for converting between ADC values and voltages
        self._conversion = 0
        
        # settings for the DMA buffer
        self._qwBufferSize = sp.uint64(self.Ns * 2 * 1); # in bytes. Enough memory  samples with 2 bytes each, only one channel active
        self._lNotifySize = sp.int32(0); # driver should notify program after all data has been transfered

        # Set number of samples per channel
        self._set32(sp.SPC_MEMSIZE, self.Ns)
        
        # All samples should be after the trigger (-4 is necessary)
        self._set32(sp.SPC_POSTTRIGGER, self.Ns - 4)
        
        # Single trigger, standard mode
        self._set32(sp.SPC_CARDMODE, sp.SPC_REC_STD_SINGLE)
        self._set32(sp.SPC_TIMEOUT, int(timeout))                  # in ms
        sp.spcm_dwSetParam_i32 (self._hCard, sp.SPC_TRIG_ORMASK,    sp.SPC_TMASK_SOFTWARE)     # trigger set to software
        sp.spcm_dwSetParam_i32 (self._hCard, sp.SPC_TRIG_ANDMASK,   0)                      # ...
        #sp.spcm_dwSetParam_i32 (self._hCard, sp.SPC_CLOCKMODE,      sp.SPC_CM_INTPLL)         # clock mode internal PLL
        sp.spcm_dwSetParam_i32 (self._hCard, sp.SPC_CLOCKMODE,      sp.SPC_CM_EXTREFCLOCK)     # clock mode external reference clock
        sp.spcm_dwSetParam_i32 (self._hCard, sp.SPC_REFERENCECLOCK, 10000000);              # Reference clock that is fed in is 10 MHz
        sp.spcm_dwSetParam_i64 (self._hCard, sp.SPC_SAMPLERATE,     sp.int64(self.samplerate));              # We want to have 30 MHz as sampling rate

        # Choose channel
        self.ch_init(channel, termination, fullrange)

        # define the data buffer
        # we try to use continuous memory if available and big enough
        self._pvBuffer = sp.c_void_p ()
        self._qwContBufLen = sp.uint64(0)
        sp.spcm_dwGetContBuf_i64 (self._hCard, sp.SPCM_BUF_DATA, sp.byref(self._pvBuffer), sp.byref(self._qwContBufLen))
        #sys.stdout.write ("ContBuf length: {0:d}\n".format(self._qwContBufLen.value))
        if self._qwContBufLen.value >= self._qwBufferSize.value:
            sys.stdout.write("Using continuous buffer\n")
        else:
            self._pvBuffer = sp.create_string_buffer (self._qwBufferSize.value)
            #sys.stdout.write("Using buffer allocated by user program\n")

        sp.spcm_dwDefTransfer_i64 (self._hCard, sp.SPCM_BUF_DATA, sp.SPCM_DIR_CARDTOPC, self._lNotifySize, self._pvBuffer, sp.uint64(0), self._qwBufferSize)


    '''
    Acquire time trace without time axis
    '''
    def acquire(self):
        # Reset buffer
        sp.spcm_dwDefTransfer_i64 (self._hCard, sp.SPCM_BUF_DATA, sp.SPCM_DIR_CARDTOPC, self._lNotifySize, self._pvBuffer, sp.uint64(0), self._qwBufferSize)

        # start card and DMA
        dwError = sp.spcm_dwSetParam_i32 (self._hCard, sp.SPC_M2CMD, sp.M2CMD_CARD_START |  sp.M2CMD_CARD_ENABLETRIGGER |  sp.M2CMD_DATA_STARTDMA)

        # check for error
        szErrorTextBuffer = sp.create_string_buffer (sp.ERRORTEXTLEN)
        if dwError != 0: # != ERR_OK
            sp.spcm_dwGetErrorInfo_i32 (self._hCard, None, None, szErrorTextBuffer)
            sys.stdout.write("{0}\n".format(szErrorTextBuffer.value))
            sp.spcm_vClose (self._hCard)
            exit()

        # wait until acquisition has finished, then calculated min and max
        else:
            dwError = sp.spcm_dwSetParam_i32 (self._hCard, sp.SPC_M2CMD,  sp.M2CMD_CARD_WAITREADY)
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

if __name__ == '__main__':
    card = Card()
    card.acquisition_set(memorylen=30e6)#, samplerate=30e6, timeout=10e3, channel=1, fullrange=200, termination=1)
    for i in range(10):
        a = card.acquire()
        print(a[0])
    card.close()
    
