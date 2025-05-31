"""
Embedded Python Blocks:

Each time this file is saved, GRC will instantiate the first class it finds
to get ports and parameters of your block. The arguments to __init__  will
be the parameters. All of them are required to have default values!
"""

import numpy as np
from gnuradio import gr
import pmt, serial

class blk(gr.sync_block):  # other base classes are basic_block, decim_block, interp_block
    """Embedded Python Block example - a simple multiply const"""

    def __init__(self, serial_port=None):  # only default arguments here
        """arguments to this function show up as parameters in GRC"""
        gr.sync_block.__init__(
            self,
            name='Update tune frequency',   # will show up in GRC
            in_sig=[],
            out_sig=[]
        )
        self.serial_port = serial_port
        self.frequencyPortName = 'frequencyPort'
        self.message_port_register_in(pmt.intern(self.frequencyPortName))
        self.set_msg_handler(pmt.intern(self.frequencyPortName), self.handle_msg)
        self.new_center_freq = 10000
        self.center_freq = 10000
        self.IF_frequency_kHz = 6
        if self.serial_port is not None:
            self.serial = serial.Serial(self.serial_port,115200)
        return

    def handle_msg(self, msg):
        #self.new_center_freq = pmt.to_long(pmt.cdr(msg)) - self.IF_frequency_kHz
        self.new_center_freq = pmt.to_float(pmt.cdr(msg)) - self.IF_frequency_kHz
        if (self.new_center_freq != self.center_freq):
            print("Updated frequency %d"%self.new_center_freq)
            self.serial.write(b'FR %d\n'%(self.new_center_freq*1000))
            self.center_freq = self.new_center_freq
        return

    def work(self, input_items, output_items):
        """example: multiply with constant"""
        if (self.new_center_freq != self.center_freq):
            self.center_freq = self.new_center_freq
        return 
