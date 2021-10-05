# -*- coding: utf-8 -*-
from __future__ import print_function
from __future__ import division

import sys
import numpy as np
import numba

# imports spectrum driver functions
import pyspcm as sp


class Card(object):
    """A class for communication with a Spectrum Instrumentation M-series data 
    acquisition card."""
    
    def __init__(self, address="/dev/spcm0"):
        """Connects to a DAQ card"""

        # Opens card
        self._hCard = sp.spcm_hOpen(address)
        if self._hCard == None:
            msg = ("The card could not be open. Try closing other software "
                   "that may be using it.")
            raise CardInaccessibleError(msg)

        # Reads the type, function and serial number of the card.
        lCardType = self._get32(sp.SPC_PCITYP)
        lSerialNumber = self._get32(sp.SPC_PCISERIALNO)
        lFncType = self._get32(sp.SPC_FNCTYPE)

        sCardName = szTypeToName(lCardType.value)
        print("Found: {0} sn {1:05d}".format(sCardName, lSerialNumber.value))

        # Checks if the card's type is analog input (AI).
        if lFncType.value != sp.SPCM_TYPE_AI:
            self.close()
            msg = ("The card type (%i) is not AI (%i)." % (lFncType.value, 
                                                           sp.SPCM_TYPE_AI))
            raise CardIncompatibleError(msg)

        # Resets the card to prevent undefined behaviour.
        self.reset()
        
        # Creates a set of conversions: factors for converting between ADC 
        # values and voltages (for all enabled channels)
        self._conversions = np.zeros(4)

    def close(self):
        """Closes the connection to the DAQ card."""
        sp.spcm_vClose(self._hCard)

    def reset(self):
        """Resets the card to default settings."""
        sp.spcm_dwSetParam_i32(self._hCard, sp.SPC_M2CMD, sp.M2CMD_CARD_RESET)
        
    def __enter__(self):
        self.reset()
        return self
    
    def __exit__(self, *a):
        self.close()
        
    def ch_init(self, ch_nums=[1], terminations=["1M"], fullranges=[10]):
        """ Initialize channels.
        ch_nums is a list of channel numbers to initialize
        terminations is a list of terminations to use with these channels
        fullranges is a list of ranges for these channels
        The three lists have to have the same length
        """
        
        # Check that the channel numbers are correct
        if not all([(ch_n in range(4)) for ch_n in ch_nums]):    
            raise ValueError("Some channel numbers are invalid")
            
        # Enable these channels by creating a CHENABLE mask and applying it
        chan_mask = 0
        
        for ch_n in ch_nums:
            chan_mask |= getattr(sp, "CHANNEL%i" % ch_n)
            
        self._set32(sp.SPC_CHENABLE, chan_mask)
        
        for ch_n, term, fullrng in zip(ch_nums, terminations, fullranges):
            ch_n = int(ch_n)
            fullrng = int(fullrng * 1000)
            
            if fullrng in [200, 500, 1000, 2000, 5000, 10000]:
                range_param = getattr(sp, "SPC_AMP{0:d}".format(int(ch_n)))
                self._set32(range_param, fullrng); 
                
                maxadc = self._get32(sp.SPC_MIINST_MAXADCVALUE)
                self._maxadc = maxadc.value
                
                conversion = float(fullrng) / 1000 / self._maxadc
                self._conversions[ch_n] = conversion
            else:
                raise ValueError("The specified voltage range is invalid.")
            
            if term == "1M":
                term_val = 0
            elif term == "50":
                term_val = 1
            else:
                raise ValueError("The specified termination is invalid")
                
            term_param = getattr(sp, "SPC_50OHM{0:d}".format(int(ch_n)))
            self._set32(term_param, term_val)
         
    def acquisition_set(self, channels=[1], Ns=300e3, samplerate=30e6, 
                        clockmode = "int",
                        timeout=10, fullranges=[10], 
                        terminations=["1M"], pretrig_ratio=0):
        """
        Initializes acquisition settings

        Specify number of samples (per channel).
        Samplerate in Hz.
        Timeout in ms.
        Specify channel number as e.g. 0, 1, 2 or 3.
        Fullrange is in V has to be equal to one of {0.2, 0.5, 1, 2, 5, 10}.
        Termination is equal to 1 for 50 Ohm and 0 for 1 MOhm
        """  
        
        if len(channels) not in [1, 2, 4]:
            raise ValueError("Number of activated channels should be 1, 2 or 4 only")
            
        timeout *= 1e3 # Convert to ms
        self.Ns = int(Ns)
        if self.Ns % 4 != 0:
            raise ValueError("Number of samples should be divisible by 4")
        self.samplerate = int(samplerate)
        
        # Sort all the arrays
        sort_idx = np.argsort(channels)
        self._acq_channels = np.array(channels)[sort_idx]
        terminations = np.array(terminations)[sort_idx]
        fullranges = np.array(fullranges)[sort_idx]
        
        if Ns / samplerate >= timeout:
            raise ValueError("Timeout is shorter than acquisition time")
        
        # Settings for the DMA buffer
        # Buffer size in bytes. Enough memory samples with 2 bytes each
        self._qwBufferSize = sp.uint64(self.Ns * 2 * len(self._acq_channels)); 
        
        # Driver should notify program after all data has been transfered
        self._lNotifySize = sp.int32(0); 

        # Set number of samples per channel
        self._set32(sp.SPC_MEMSIZE, self.Ns)
        
        # Setting the posttrigger value which has to be a multiple of 4
        pretrig = np.clip(((self.Ns * pretrig_ratio) // 4) * 4, 4, self.Ns - 4)
        self._set32(sp.SPC_POSTTRIGGER, self.Ns - int(pretrig))
        
        # Single trigger, standard mode
        self._set32(sp.SPC_CARDMODE, sp.SPC_REC_STD_SINGLE)
        
        # Set timeout value
        self._set32(sp.SPC_TIMEOUT, int(timeout))
        
        if clockmode == "int":
             # clock mode internal PLL
            sp.spcm_dwSetParam_i32 (self._hCard, sp.SPC_CLOCKMODE, sp.SPC_CM_INTPLL) 
        else:
            # Set external reference lock with 10 MHz frequency
            self._set32(sp.SPC_CLOCKMODE, sp.SPC_CM_EXTREFCLOCK)
            self._set32(sp.SPC_REFERENCECLOCK, 10000000)
        
        # Set the sampling rate
        self._set64(sp.SPC_SAMPLERATE, self.samplerate)

        # Choose channel
        self.ch_init(self._acq_channels, terminations, fullranges)

        # define the data buffer
        # we try to use continuous memory if available and big enough
        self._pvBuffer = sp.c_void_p()
        self._qwContBufLen = sp.uint64(0)
        sp.spcm_dwGetContBuf_i64 (self._hCard, 
                                  sp.SPCM_BUF_DATA, 
                                  sp.byref(self._pvBuffer), 
                                  sp.byref(self._qwContBufLen))
        #sys.stdout.write ("ContBuf length: {0:d}\n".format(self._qwContBufLen.value))
        if self._qwContBufLen.value >= self._qwBufferSize.value:
            sys.stdout.write("Using continuous buffer\n")
        else:
            self._pvBuffer = sp.create_string_buffer(self._qwBufferSize.value)

        sp.spcm_dwDefTransfer_i64(self._hCard, sp.SPCM_BUF_DATA, 
                                   sp.SPCM_DIR_CARDTOPC, self._lNotifySize, 
                                   self._pvBuffer, sp.uint64(0), 
                                   self._qwBufferSize)

    def trigger_set(self, mode="soft", channel=0, edge="pos", level=0):
        """
        Set triggering mode. Can be either "software", i.e. immediate free-run,
        or on a rising or falling edge of one of the channels
        """
        if mode == "soft":
            # Software trigger
    
            self._set32(sp.SPC_TRIG_ORMASK, sp.SPC_TMASK_SOFTWARE)
            self._set32(sp.SPC_TRIG_ANDMASK, 0)
        elif mode == "ext":
            # External trigger

            # Disables all triggering.
            self._set32(sp.SPC_TRIG_ORMASK, 0)
            self._set32(sp.SPC_TRIG_ANDMASK, 0)
            self._set32(sp.SPC_TRIG_CH_ORMASK1, 0)
            self._set32(sp.SPC_TRIG_CH_ANDMASK1, 0)

            # Enables the external trigger.
            mask = getattr(sp, "SPC_TMASK_EXT%i" % channel)
            self._set32(sp.SPC_TRIG_ANDMASK, mask)

            modereg = getattr(sp, "SPC_TRIG_EXT%i_MODE" % channel)
            if edge == "pos":
                self._set32(modereg, sp.SPC_TM_POS)
            elif edge == "neg":
                self._set32(modereg, sp.SPC_TM_NEG)
        elif mode == "chan":
            # Channel level trigger

            # The division by 4 is necessary because the trigger has 14-bit 
            # resolution as compared to overall 16-bit resolution of the card
            trigvalue = int(level/self._conversions[channel]/4)
            
            # Check that the trigger level is within specified levels
            if abs(trigvalue) >= self._maxadc/4:
                raise ValueError("The specified trigger level is outside allowed values")
            
            # Disable all other triggering
            self._set32(sp.SPC_TRIG_ORMASK, sp.SPC_TMASK_NONE)
            self._set32(sp.SPC_TRIG_ANDMASK, 0)
            self._set32(sp.SPC_TRIG_CH_ORMASK1, 0)
            self._set32(sp.SPC_TRIG_CH_ANDMASK1, 0)
            
            # Enable the required trigger
            maskname = "SPC_TMASK0_CH{0:d}".format(int(channel))
            chmask = getattr(sp, maskname)
            self._set32(sp.SPC_TRIG_CH_ORMASK0, chmask)
            
            # Mode is set to the required one
            modereg_name = "SPC_TRIG_CH{0:d}_MODE".format(int(channel))
            modereg = getattr(sp, modereg_name)
            if edge == "pos":
                self._set32(modereg, sp.SPC_TM_POS)
            elif edge == "neg":
                self._set32(modereg, sp.SPC_TM_NEG)
            else:
                raise ValueError("Incorrect edge specification")
                
            # Finally, set the trigger level
            levelreg_name = "SPC_TRIG_CH{0:d}_LEVEL0".format(int(channel))
            levelreg = getattr(sp, levelreg_name)
            self._set32(levelreg, trigvalue)

    def acquire(self, convert=True):
        """Acquire time trace without time axis"""

        # Setup memory transfer parameters
        sp.spcm_dwDefTransfer_i64 (self._hCard, sp.SPCM_BUF_DATA, 
                                   sp.SPCM_DIR_CARDTOPC, 
                                   self._lNotifySize, self._pvBuffer, 
                                   sp.uint64(0), self._qwBufferSize)
        
        # Start card, enable trigger and wait until the acquisition has finished
        start_cmd = (sp.M2CMD_CARD_START | sp.M2CMD_CARD_ENABLETRIGGER
                     | sp.M2CMD_CARD_WAITREADY | sp.M2CMD_DATA_STARTDMA
                     | sp.M2CMD_DATA_WAITDMA)
        dwError = self._set32(sp.SPC_M2CMD, start_cmd)
        
        # check for error
        szErrorTextBuffer = sp.create_string_buffer(sp.ERRORTEXTLEN)
        if dwError != sp.ERR_OK:
            sp.spcm_dwGetErrorInfo_i32 (self._hCard, None, None, 
                                        szErrorTextBuffer)
            print("{0}\n".format(szErrorTextBuffer.value))
            self.close()
            return

        # Wait until acquisition has finished, then return data
        # Cast data pointer to pointer to 16bit integers
        pnData = sp.cast(self._pvBuffer, sp.ptr16) 
        
        # Convert the array of data into a numpy array
        # The array is already properly ordered, so we can already
        # give it the right shape
        Nch = len(self._acq_channels)
        data = np.ctypeslib.as_array(pnData, shape=(self.Ns, Nch))
        
        # Conversion factors for active channels
        conv_out = [self._conversions[ch_n] for ch_n in self._acq_channels]
            
        # Return a copy of the array to prevent it from being
        # overwritten by DMA
        if not convert:
            return (conv_out, data.copy())
        else:
            out = np.zeros((self.Ns, Nch), dtype=np.float64)
            _convert(out, data, conv_out)
            return out


    def _get32(self, reg):
        """Gets the value of a 32-bit register. 
        An alias for spcm_dwGetParam_i32."""
        dst = sp.int32(0)
        sp.spcm_dwGetParam_i32(self._hCard, reg, sp.byref(dst))
        return dst

    def _get64(self, reg):
        """Gets the value of a 64-bit register. 
        An alias for spcm_dwGetParam_i64."""
        dst = sp.int64(0)
        sp.spcm_dwGetParam_i64(self._hCard, reg, sp.byref(dst))
        return dst
    
    def _set32(self, reg, val):
        """Sets the value of a 32-bit register. 
        An alias for spcm_dwSetParam_i32."""
        return sp.spcm_dwSetParam_i32(self._hCard, reg, sp.int32(val))
    
    def _set64(self, reg, val):
        """Sets the value of a 64-bit register. 
        An alias for spcm_dwSetParam_i64."""    
        return sp.spcm_dwSetParam_i64(self._hCard, reg, sp.int64(val))


class CardError(Exception):
    """ Base class for card errors """
    
class CardInaccessibleError(CardError):
    pass

class CardIncompatibleError(CardError):
    pass

def szTypeToName(lCardType):
    """A vendor-supplied function for card name translation."""

    lVersion = (lCardType & sp.TYP_VERSIONMASK)
    lType = (lCardType & sp.TYP_SERIESMASK )

    if lType == sp.TYP_M2ISERIES:
        sName = 'M2i.%04x' % lVersion
    elif lType == sp.TYP_M2IEXPSERIES:
        sName = 'M2i.%04x-Exp' % lVersion
    elif lType == sp.TYP_M3ISERIES:
        sName = 'M3i.%04x' % lVersion
    elif lType == sp.TYP_M3IEXPSERIES:
        sName = 'M3i.%04x-Exp' % lVersion
    elif lType == sp.TYP_M4IEXPSERIES:
        sName = 'M4i.%04x-x8' % lVersion
    elif lType == sp.TYP_M4XEXPSERIES:
        sName = 'M4x.%04x-x4' % lVersion
    else:
        sName = ''

    return sName

    
@numba.jit(nopython=True, parallel=True)            
def _convert(out, x, convs):
    """Convert an int16 2D numpy array (N, ch) into a 2D float64 array using 
    the specified conversion factors and stores the result in a preallocated 
    array.
    """
    for ch in numba.prange(out.shape[1]):
        for n in numba.prange(out.shape[0]):
            out[n, ch] = x[n, ch] * convs[ch]
