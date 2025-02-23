import configure
from quisk_hardware_model import Hardware as BaseHardware
import _quisk as QS
import serial

################ Receivers VWS SDR, A receiver designed by KI3P.
## hardware_file_name		Hardware file path, rfile
# This is the file that contains the control logic for each radio.
#hardware_file_name = "vwsquiskpkg/quisk_hardware.py"

## widgets_file_name			Widget file path, rfile
# This optional file adds additional controls for the radio.
#widgets_file_name = ""

## rx_max_amplitude_correct		Max ampl correct, number
# If you get your I/Q samples from a sound card, you will need to correct the
# amplitude and phase for inaccuracies in the analog hardware.  The correction is
# entered using the controls from the "Rx Phase" button on the config screen.
# You must enter a positive number.  This controls the range of the control.
#rx_max_amplitude_correct = 0.42

## rx_max_phase_correct			Max phase correct, number
# If you get your I/Q samples from a sound card, you will need to correct the
# amplitude and phase for inaccuracies in the analog hardware.  The correction is
# entered using the controls from the "Rx Phase" button on the config screen.
# You must enter a positive number.  This controls the range of the control in degrees.
#rx_max_phase_correct = 10.0

## vws_name                   Serial port, text
# The name of the VWS serial port to open.
#vws_name = "/dev/ttyACM0"

sample_rate = 48000
channel_i = 1
channel_q = 0
correction = 630

class Hardware(BaseHardware):
  def __init__(self, app, conf):
    BaseHardware.__init__(self, app, conf)
          
  def open(self):
    text = BaseHardware.open(self)
    self.serial = serial.Serial(getattr(self.conf, "vws_name"),115200)
    self.vfo = None
    self.tune = None
    return text

  def close(self):
    del self.serial
    self.vfo = None
    self.tune = None
    pass

  def ChangeFrequency(self, tune, vfo, source='', band='', event=None):
    if vfo != self.vfo:
      self.serial.write(b'FR %d\r'%(vfo+correction))
      self.vfo = vfo
    self.tune = tune
    return [self.tune, self.vfo]

  def ReturnFrequency(self):
    return [self.tune, self.vfo]
  
  def ImmediateChange(self, name):
    pass
  
  def PollGuiControl(self):
    pass
