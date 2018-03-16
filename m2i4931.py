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
            return sp.spcm_dwSetParam_i32(self._hCard, param, sp.int32(val))
        else:
            return sp.spcm_dwSetParam_i32(self._hCard, param, sp.uint32(val))
    
    def _set64(self, param, val, uint=False):
        val = int(val)
        if not uint:
            return sp.spcm_dwSetParam_i64(self._hCard, param, sp.int64(val))
        else:
            return sp.spcm_dwSetParam_i64(self._hCard, param, sp.uint64(val))
    
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

        # Reset the card to prevent undefined behaviour
        self.reset()

    # Close connection to DAQ card
    def close(self):
        sp.spcm_vClose(self._hCard)

    # Reset the card to default settings
    def reset(self):
        sp.spcm_dwSetParam_i32(self._hCard, sp.SPC_M2CMD, sp.M2CMD_CARD_RESET)
        
    """
    Initialize channels.
    ch_nums is a list of channel numbers to initialize
    terminations is a list of terminations to use with these channels
    fullranges is a list of ranges for these channels
    The three lists have to have the same length
    """
    def ch_init(self, ch_nums=[1], terminations=[Term.TERM_1M], 
                fullranges=[10]):
        # Check that the channel numbers are correct
        if not np.all(np.isin(ch_nums, range(4))):
            raise ValueError("Some channel numbers are invalid")
            
        # Enable these channels by creating a CHENABLE mask and applying it
        chan_mask = 0
        
        for ch_n in ch_nums:
            chan_mask |= getattr(sp, "CHANNEL{0:d}".format(int(ch_n)))
            
        self._set32(sp.SPC_CHENABLE, chan_mask)
        
        for i in range(len(ch_nums)):
            ch_n = ch_nums[i]
            fullrange_val = int(fullranges[i] * 1000)
            termination = terminations[i]
            
            if fullrange_val in [200,500,1000,2000,5000,10000]:
                range_param = getattr(sp, "SPC_AMP{0:d}".format(int(ch_n)))
                self._set32(range_param, fullrange_val);            
                maxadc = self._get32(sp.SPC_MIINST_MAXADCVALUE)
                self._maxadc = maxadc.value
                conversion = float(fullrange_val)/1000 / self._maxadc
                self._conversions[i] = conversion
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
    def acquisition_set(self, channels=[1], Ns=300e3, samplerate=30e6, 
                        timeout=10, fullranges=[10], 
                        terminations=[Term.TERM_1M]):
        timeout *= 1e3 # Convert to ms
        self.Ns = int(Ns)
        if self.Ns % 4 != 0:
            raise ValueError("Number of samples should be divisible by 4")
        self.samplerate = int(samplerate)
        
        self.Nchannels = len(channels)
        
        if Ns / samplerate >= timeout:
            raise ValueError("Timeout is shorter than acquisition time")
        
        # Factors for converting between ADC values and voltages (for all 
        # enabled channels)
        self._conversions = np.zeros(self.Nchannels)
        
        # Settings for the DMA buffer
        # Buffer size in bytes. Enough memory samples with 2 bytes each, 
        # only one channel active
        self._qwBufferSize = sp.uint64(self.Ns * 2 * self.Nchannels); 
        
        # Driver should notify program after all data has been transfered
        self._lNotifySize = sp.int32(0); 

        # Set number of samples per channel
        self._set32(sp.SPC_MEMSIZE, self.Ns)
        
        # All samples should be after the trigger (-4 is necessary)
        self._set32(sp.SPC_POSTTRIGGER, self.Ns - 4)
        
        # Single trigger, standard mode
        self._set32(sp.SPC_CARDMODE, sp.SPC_REC_STD_SINGLE)
        
        # Set timeout value
        self._set32(sp.SPC_TIMEOUT, int(timeout))
        
        # Trigger set to software
        self._set32(sp.SPC_TRIG_ORMASK, sp.SPC_TMASK_SOFTWARE)
        self._set32(sp.SPC_TRIG_ANDMASK, 0)                 
        
        # Set internal clock
        #sp.spcm_dwSetParam_i32 (self._hCard, sp.SPC_CLOCKMODE,      sp.SPC_CM_INTPLL)         # clock mode internal PLL
        
        # Set ecternal reference lock with 10 MHz frequency
        self._set32(sp.SPC_CLOCKMODE, sp.SPC_CM_EXTREFCLOCK)
        self._set32(sp.SPC_REFERENCECLOCK, 10000000)
        
        # Set the sampling rate
        self._set64(sp.SPC_SAMPLERATE, self.samplerate)

        # Choose channel
        self.ch_init(channels, terminations, fullranges)

        # define the data buffer
        # we try to use continuous memory if available and big enough
        self._pvBuffer = sp.c_void_p ()
        self._qwContBufLen = sp.uint64(0)
        sp.spcm_dwGetContBuf_i64 (self._hCard, 
                                  sp.SPCM_BUF_DATA, 
                                  sp.byref(self._pvBuffer), 
                                  sp.byref(self._qwContBufLen))
        #sys.stdout.write ("ContBuf length: {0:d}\n".format(self._qwContBufLen.value))
        if self._qwContBufLen.value >= self._qwBufferSize.value:
            sys.stdout.write("Using continuous buffer\n")
        else:
            self._pvBuffer = sp.create_string_buffer (self._qwBufferSize.value)
            #sys.stdout.write("Using buffer allocated by user program\n")

        sp.spcm_dwDefTransfer_i64 (self._hCard, sp.SPCM_BUF_DATA, 
                                   sp.SPCM_DIR_CARDTOPC, self._lNotifySize, 
                                   self._pvBuffer, sp.uint64(0), 
                                   self._qwBufferSize)


    '''
    Acquire time trace without time axis
    '''
    def acquire(self):
        # Reset buffer
        sp.spcm_dwDefTransfer_i64 (self._hCard, sp.SPCM_BUF_DATA, 
                                   sp.SPCM_DIR_CARDTOPC, 
                                   self._lNotifySize, self._pvBuffer, 
                                   sp.uint64(0), self._qwBufferSize)

        # start card and DMA
        start_cmd = sp.M2CMD_CARD_START | sp.M2CMD_CARD_ENABLETRIGGER \
        |  sp.M2CMD_DATA_STARTDMA
        dwError = self._set32(sp.SPC_M2CMD, start_cmd)

        # check for error
        szErrorTextBuffer = sp.create_string_buffer(sp.ERRORTEXTLEN)
        if dwError != sp.ERR_OK:
            sp.spcm_dwGetErrorInfo_i32 (self._hCard, None, None, 
                                        szErrorTextBuffer)
            print("{0}\n".format(szErrorTextBuffer.value))
            self.close()
            exit()

        # Wait until acquisition has finished, then return data
        else:
            dwError = self._set32(sp.SPC_M2CMD, sp.M2CMD_CARD_WAITREADY)
            if dwError != sp.ERR_OK:
                if dwError == sp.ERR_TIMEOUT:
                    print("... Timeout\n")
                else:
                    print("... Error: {0:d}\n".format(dwError))

            else:
                # Cast data pointer to pointer to 16bit integers
                pnData = sp.cast(self._pvBuffer, sp.ptr16) 
                
                # Convert the array of data into a numpy array
                total_samples = int(self.Ns*self.Nchannels)
                data = np.ctypeslib.as_array(pnData, shape=(total_samples,))
                
                # Convert it into a matrix where the number of cols is the
                # number of channels
                out = np.empty((self.Ns, self.Nchannels), dtype=np.float64)
                for i in range(self.Nchannels):
                    data_slice = data[i::self.Nchannels]
                    out[:,i] = data_slice.astype(np.float64)*self._conversions[i]

                return out

if __name__ == '__main__':
    card = Card()
    card.acquisition_set(memorylen=30e6)
    for i in range(10):
        a = card.acquire()
        print(a[0])
    card.close()
    
