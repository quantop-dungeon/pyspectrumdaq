import sys
from typing import Sequence
import numpy as np
import numba

# Imports vendor-supplied driver functions
import pyspcm as sp


class Card:
    """A class for communication with a Spectrum Instrumentation M-series data 
    acquisition cards."""
    
    def __init__(self, address: str = "/dev/spcm0"):
        """Connects to a DAQ card."""

        # Opens the card.
        self._hCard = sp.spcm_hOpen(address)
        if self._hCard == None:
            msg = ("The card could not be open. Try closing other software "
                   "that may be using it.")
            raise CardInaccessibleError(msg)

        # Reads the type, function and serial number of the card.
        card_type = self.get32(sp.SPC_PCITYP)
        serial_number = self.get32(sp.SPC_PCISERIALNO)
        func_type = self.get32(sp.SPC_FNCTYPE)

        # Translates the type to a readable name.
        card_name = szTypeToName(card_type) 

        print(f"Found: {card_name} sn {serial_number}")

        # Checks that the card's type is analog input (AI).
        if func_type != sp.SPCM_TYPE_AI:
            self.close()
            msg = ("The card function type (%i) is not AI (%i)." 
                   % (func_type, sp.SPCM_TYPE_AI))
            raise CardIncompatibleError(msg)

        # Resets the card to prevent undefined behaviour.
        self.reset()
        
        # Creates a set of conversions: factors for converting between ADC 
        # values and voltages (for all enabled channels)
        self._conversions = np.zeros(4)

    def close(self) -> None:
        """Closes the connection to the DAQ card."""
        sp.spcm_vClose(self._hCard)

    def reset(self) -> None:
        """Resets the card to default settings."""
        self.set32(sp.SPC_M2CMD, sp.M2CMD_CARD_RESET)
        
    def __enter__(self):
        self.reset()
        return self
    
    def __exit__(self, *a):
        self.close()
        
    def set_channels(self, 
                     ch_nums: Sequence = (1,), 
                     terminations: Sequence = ("1M",), 
                     fullranges=(10,)) -> None:
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
            
        self.set32(sp.SPC_CHENABLE, chan_mask)

        self._maxadc = self.get32(sp.SPC_MIINST_MAXADCVALUE)
        
        for ch_n, term, fullrng in zip(ch_nums, terminations, fullranges):
            ch_n = int(ch_n)
            fullrng = int(fullrng * 1000)
            
            if fullrng in [200, 500, 1000, 2000, 5000, 10000]:
                range_param = getattr(sp, "SPC_AMP%i" % ch_n)
                self.set32(range_param, fullrng); 
                
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
                
            term_param = getattr(sp, "SPC_50OHM%i" % ch_n)
            self.set32(term_param, term_val)
         
    def set_acquisition(self, 
                        channels: Sequence = (1,), 
                        fullranges: Sequence = (10,), 
                        terminations: Sequence = ("1M",),
                        Ns: int = 300e3, 
                        samplerate: int = 30e6,
                        timeout: int = 10,  
                        pretrig_ratio: float =0) -> None:
        """
        Initializes acquisition settings

        Args:
            Specify number of samples (per channel).
            Samplerate in Hz.
            Timeout in ms.
            Specify channel number as e.g. 0, 1, 2 or 3.
            Fullrange is in V has to be equal to one of {0.2, 0.5, 1, 2, 5, 10}.
            Termination is equal to 1 for 50 Ohm and 0 for 1 MOhm
        """  
        
        # TODO: move the code between this place and set_channels to set_channels
        if len(channels) not in [1, 2, 4]:
            raise ValueError("The number of activated channels can be 1, 2 or 4 only") # TODO: This is an inconsistency, becayse the trigger assumes that there can be more than 4 channels.
        
        # Sort all the arrays
        sort_idx = np.argsort(channels)
        self._acq_channels = np.array(channels)[sort_idx]
        terminations = np.array(terminations)[sort_idx]
        fullranges = np.array(fullranges)[sort_idx]

        # Choose channel
        self.set_channels(self._acq_channels, terminations, fullranges)

        timeout *= 1e3  # Converts to ms
        self.Ns = int(Ns)
        if self.Ns % 4 != 0:
            raise ValueError("The number of samples should be divisible by 4")

        self.samplerate = int(samplerate)
        
        if Ns / samplerate >= timeout:
            raise ValueError("Timeout is shorter than acquisition time")

        # Set the sampling rate
        self.set64(sp.SPC_SAMPLERATE, self.samplerate)

        # Set number of samples per channel
        self.set32(sp.SPC_MEMSIZE, self.Ns)
        
        # Setting the posttrigger value which has to be a multiple of 4
        pretrig = np.clip(((self.Ns * pretrig_ratio) // 4) * 4, 4, self.Ns - 4)
        self.set32(sp.SPC_POSTTRIGGER, self.Ns - int(pretrig))
        
        # Single trigger, standard mode
        self.set_card_mode("std", "single")
        
        # Set timeout value
        self.set32(sp.SPC_TIMEOUT, int(timeout))

        # define the data buffer
        # we try to use continuous memory if available and big enough
        self._pvBuffer = sp.c_void_p()
        self._qwContBufLen = sp.uint64(0)
        sp.spcm_dwGetContBuf_i64(self._hCard, 
                                 sp.SPCM_BUF_DATA, 
                                 sp.byref(self._pvBuffer), 
                                 sp.byref(self._qwContBufLen))

        # Settings for the DMA buffer
        # Buffer size in bytes. Enough memory samples with 2 bytes each
        self._qwBufferSize = sp.uint64(self.Ns * 2 * len(self._acq_channels))
        
        if self._qwContBufLen.value >= self._qwBufferSize.value:
            sys.stdout.write("Using continuous buffer\n")
        else:
            self._pvBuffer = sp.create_string_buffer(self._qwBufferSize.value) 

        # Driver should notify program after all data has been transfered
        self._lNotifySize = sp.int32(0); 

        sp.spcm_dwDefTransfer_i64(self._hCard, sp.SPCM_BUF_DATA, 
                                   sp.SPCM_DIR_CARDTOPC, self._lNotifySize, 
                                   self._pvBuffer, sp.uint64(0), 
                                   self._qwBufferSize)

    def set_card_mode(self, mode: str, sub: str = "single") -> None:
        """Sets the card mode. The arguments are case-insensitive.

        Args:
            mode ('std' or 'fifo'): Main mode.
            sub ('single', 'multi', 'gate' or 'aba'): Sub-mode.
        """

        # Checks the consistency of arguments.
        mode = mode.upper()
        if mode not in ["STD", "FIFO"]:
            raise ValueError(f"The mode must be 'std' or 'fifo', not {mode}.")
        
        sub = sub.upper()
        if sub not in ["SINGLE", "MULTI", "GATE", "ABA"]:
            raise ValueError(f"The sub-mode must be 'single', 'multi', 'gate' "
                             f"or 'aba', not {sub}.")
        
        # Sets the card mode.
        mode_val = getattr(sp, "SPC_REC_%s_%s" % (mode, sub))
        self.set32(sp.SPC_CARDMODE, mode_val)

    def set_trigger(self, mode: str = "soft", channel: int = 0, edge: str = "pos", level: float = 0) -> None:
        """
        Set triggering mode. Can be either "software", i.e. immediate free-run,
        or on a rising or falling edge of one of the channels

        Args:
            mode {soft, ext or chan}
            edge {pos or neg}:
                Trigger edge. Applies to channel and external trigger modes.
            level: trigger level in volts. Only applies to channel triggers.
        """
        if mode == "soft":
            # Software trigger
    
            self.set32(sp.SPC_TRIG_ORMASK, sp.SPC_TMASK_SOFTWARE)
            # self._set32(sp.SPC_TRIG_ANDMASK, 0)  This is not a valid value to set, and it does not do anything, right?
        elif mode == "ext":
            # External trigger

            # Disables all triggering.
            self.set32(sp.SPC_TRIG_ORMASK, 0)
            self.set32(sp.SPC_TRIG_CH_ORMASK0, 0)
            self.set32(sp.SPC_TRIG_CH_ORMASK1, 0)
            self.set32(sp.SPC_TRIG_CH_ANDMASK0, 0)
            self.set32(sp.SPC_TRIG_CH_ANDMASK1, 0)

            # Enables the external trigger.
            self.set32(sp.SPC_TRIG_ANDMASK, "SPC_TMASK_EXT%i" % channel)

            modereg = getattr(sp, "SPC_TRIG_EXT%i_MODE" % channel)
            if edge == "pos":
                self.set32(modereg, sp.SPC_TM_POS)
            elif edge == "neg":
                self.set32(modereg, sp.SPC_TM_NEG)
        elif mode == "chan":
            # Channel level trigger

            # The division by 4 is necessary because the trigger has 14-bit 
            # resolution as compared to overall 16-bit resolution of the card
            trigvalue = int(level/self._conversions[channel]/4)
            
            # Check that the trigger level is within specified levels
            if abs(trigvalue) >= self._maxadc/4:
                raise ValueError("The specified trigger level is outside allowed values")
            
            # Enable the required trigger
            maskname = "SPC_TMASK0_CH{0:d}".format(int(channel))
            chmask = getattr(sp, maskname)

            # Disable all other triggering
            self.set32(sp.SPC_TRIG_ORMASK, 0)
            self.set32(sp.SPC_TRIG_ANDMASK, 0)
            self.set32(sp.SPC_TRIG_CH_ORMASK1, 0)
            self.set32(sp.SPC_TRIG_CH_ANDMASK0, 0)
            self.set32(sp.SPC_TRIG_CH_ANDMASK1, 0)

            self.set32(sp.SPC_TRIG_CH_ORMASK0, chmask)
            
            # Mode is set to the required one
            modereg_name = "SPC_TRIG_CH{0:d}_MODE".format(int(channel))
            modereg = getattr(sp, modereg_name)
            if edge == "pos":
                self.set32(modereg, sp.SPC_TM_POS)
            elif edge == "neg":
                self.set32(modereg, sp.SPC_TM_NEG)
            else:
                raise ValueError("Incorrect edge specification")
                
            # Finally, set the trigger level
            levelreg_name = "SPC_TRIG_CH{0:d}_LEVEL0".format(int(channel))
            levelreg = getattr(sp, levelreg_name)
            self.set32(levelreg, trigvalue)

    def set_clock(self, mode: str = "int", ext_freq: int = 10000000) -> None:
        """Sets the clock. The mode can be internal or external, for 
        the external mode the external cklock frequency must be specified."""

        if mode == "int":
             # Internal clock.
            self.set32(sp.SPC_CLOCKMODE, sp.SPC_CM_INTPLL) 
        else:
            # External reference clock.
            self.set32(sp.SPC_CLOCKMODE, sp.SPC_CM_EXTREFCLOCK)
            self.set32(sp.SPC_REFERENCECLOCK, int(ext_freq))

    def acquire(self, convert: bool = True):
        """Acquire time trace without time axis"""

        # Setup memory transfer parameters
        sp.spcm_dwDefTransfer_i64(self._hCard, sp.SPCM_BUF_DATA, 
                                 sp.SPCM_DIR_CARDTOPC, 
                                  self._lNotifySize, self._pvBuffer, 
                                  sp.uint64(0), self._qwBufferSize)
        
        # Start card, enable trigger and wait until the acquisition has finished
        start_cmd = (sp.M2CMD_CARD_START | sp.M2CMD_CARD_ENABLETRIGGER
                     | sp.M2CMD_CARD_WAITREADY | sp.M2CMD_DATA_STARTDMA
                     | sp.M2CMD_DATA_WAITDMA)
        err = self.set32(sp.SPC_M2CMD, start_cmd)
        
        # check for error
        if err != sp.ERR_OK:
            szErrorTextBuff = sp.create_string_buffer(sp.ERRORTEXTLEN)
            sp.spcm_dwGetErrorInfo_i32(self._hCard, None, None, szErrorTextBuff)
            print("Error code: {0}\n".format(szErrorTextBuff.value))
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

    def get32(self, reg: int) -> int:
        """Gets the value of a 32-bit register. 
        An alias for spcm_dwGetParam_i32.
        """
        dst = sp.int32(0)
        sp.spcm_dwGetParam_i32(self._hCard, reg, sp.byref(dst))
        return dst.value

    def get64(self, reg: int) -> int:
        """Gets the value of a 64-bit register. 
        An alias for spcm_dwGetParam_i64.
        """
        dst = sp.int64(0)
        sp.spcm_dwGetParam_i64(self._hCard, reg, sp.byref(dst))
        return dst.value
    
    def set32(self, reg: int, val: int) -> int:
        """Sets the value of a 32-bit register. Returns an error code if 
        an error occurred. An alias for spcm_dwSetParam_i32.
        """
        err = sp.spcm_dwSetParam_i32(self._hCard, reg, val)
        return err.value
    
    def set64(self, reg: int, val: int) -> int:
        """Sets the value of a 64-bit register. Returns an error code if 
        an error occurred. An alias for spcm_dwSetParam_i64.
        """   
        err = sp.spcm_dwSetParam_i64(self._hCard, reg, val) 
        return err.value


class CardError(Exception):
    """Base class for card errors"""
    
class CardInaccessibleError(CardError):
    pass

class CardIncompatibleError(CardError):
    pass

def szTypeToName(lCardType: int) -> str:
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
