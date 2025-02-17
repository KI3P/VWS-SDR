#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#
# SPDX-License-Identifier: GPL-3.0
#
# GNU Radio Python Flow Graph
# Title: VWSSDR Receiver
# Author: Oliver KI3P
# GNU Radio version: 3.10.1.1

from packaging.version import Version as StrictVersion

if __name__ == '__main__':
    import ctypes
    import sys
    if sys.platform.startswith('linux'):
        try:
            x11 = ctypes.cdll.LoadLibrary('libX11.so')
            x11.XInitThreads()
        except:
            print("Warning: failed to XInitThreads()")

from PyQt5 import Qt
from gnuradio import qtgui
from gnuradio.filter import firdes
import sip
from gnuradio import audio
from gnuradio import blocks
from gnuradio import gr
from gnuradio.fft import window
import sys
import signal
from argparse import ArgumentParser
from gnuradio.eng_arg import eng_float, intx
from gnuradio import eng_notation
from gnuradio.qtgui import Range, RangeWidget
from PyQt5 import QtCore
import numpy as np
import vws_Sdr_KI3P_epy_block_0 as epy_block_0  # embedded python block



from gnuradio import qtgui

class vws_Sdr_KI3P(gr.top_block, Qt.QWidget):

    def __init__(self):
        gr.top_block.__init__(self, "VWSSDR Receiver", catch_exceptions=True)
        Qt.QWidget.__init__(self)
        self.setWindowTitle("VWSSDR Receiver")
        qtgui.util.check_set_qss()
        try:
            self.setWindowIcon(Qt.QIcon.fromTheme('gnuradio-grc'))
        except:
            pass
        self.top_scroll_layout = Qt.QVBoxLayout()
        self.setLayout(self.top_scroll_layout)
        self.top_scroll = Qt.QScrollArea()
        self.top_scroll.setFrameStyle(Qt.QFrame.NoFrame)
        self.top_scroll_layout.addWidget(self.top_scroll)
        self.top_scroll.setWidgetResizable(True)
        self.top_widget = Qt.QWidget()
        self.top_scroll.setWidget(self.top_widget)
        self.top_layout = Qt.QVBoxLayout(self.top_widget)
        self.top_grid_layout = Qt.QGridLayout()
        self.top_layout.addLayout(self.top_grid_layout)

        self.settings = Qt.QSettings("GNU Radio", "vws_Sdr_KI3P")

        try:
            if StrictVersion(Qt.qVersion()) < StrictVersion("5.0.0"):
                self.restoreGeometry(self.settings.value("geometry").toByteArray())
            else:
                self.restoreGeometry(self.settings.value("geometry"))
        except:
            pass

        ##################################################
        # Variables
        ##################################################
        self.samp_rate = samp_rate = 48000
        self.phase = phase = 0
        self.gain = gain = 1
        self.freq = freq = 48e3
        self.amp = amp = 0.1

        ##################################################
        # Blocks
        ##################################################
        self._phase_range = Range(-0.1, 0.1, 0.001, 0, 200)
        self._phase_win = RangeWidget(self._phase_range, self.set_phase, "'phase'", "counter_slider", float, QtCore.Qt.Horizontal)
        self.top_layout.addWidget(self._phase_win)
        self._gain_range = Range(0, 2, 0.001, 1, 200)
        self._gain_win = RangeWidget(self._gain_range, self.set_gain, "'gain'", "counter_slider", float, QtCore.Qt.Horizontal)
        self.top_layout.addWidget(self._gain_win)
        self.qtgui_sink_x_0 = qtgui.sink_c(
            1024, #fftsize
            window.WIN_BLACKMAN_hARRIS, #wintype
            0, #fc
            samp_rate, #bw
            "", #name
            True, #plotfreq
            True, #plotwaterfall
            True, #plottime
            True, #plotconst
            None # parent
        )
        self.qtgui_sink_x_0.set_update_time(1.0/10)
        self._qtgui_sink_x_0_win = sip.wrapinstance(self.qtgui_sink_x_0.qwidget(), Qt.QWidget)

        self.qtgui_sink_x_0.enable_rf_freq(False)

        self.top_layout.addWidget(self._qtgui_sink_x_0_win)
        self.qtgui_edit_box_msg_0 = qtgui.edit_box_msg(qtgui.INT, '10000', 'Center Frequency [kHz]', False, True, 'frequency_kHz', None)
        self._qtgui_edit_box_msg_0_win = sip.wrapinstance(self.qtgui_edit_box_msg_0.qwidget(), Qt.QWidget)
        self.top_layout.addWidget(self._qtgui_edit_box_msg_0_win)
        self.epy_block_0 = epy_block_0.blk(serial_port="/dev/ttyACM0")
        self.blocks_selector_0_0 = blocks.selector(gr.sizeof_float*1,0 if phase < 0 else 1,0)
        self.blocks_selector_0_0.set_enabled(True)
        self.blocks_selector_0 = blocks.selector(gr.sizeof_float*1,0 if phase < 0 else 1,0)
        self.blocks_selector_0.set_enabled(True)
        self.blocks_multiply_const_vxx_0_0_0 = blocks.multiply_const_ff(phase)
        self.blocks_multiply_const_vxx_0_0 = blocks.multiply_const_ff(phase)
        self.blocks_multiply_const_vxx_0 = blocks.multiply_const_ff(-gain)
        self.blocks_float_to_complex_0 = blocks.float_to_complex(1)
        self.blocks_add_xx_0_0 = blocks.add_vff(1)
        self.blocks_add_xx_0 = blocks.add_vff(1)
        self.audio_source_0 = audio.source(samp_rate, 'hw:0,0', True)
        self._amp_range = Range(0, 0.2, 0.01, 0.1, 200)
        self._amp_win = RangeWidget(self._amp_range, self.set_amp, "Amplitude", "counter_slider", float, QtCore.Qt.Horizontal)
        self.top_layout.addWidget(self._amp_win)


        ##################################################
        # Connections
        ##################################################
        self.msg_connect((self.qtgui_edit_box_msg_0, 'msg'), (self.epy_block_0, 'frequencyPort'))
        self.connect((self.audio_source_0, 1), (self.blocks_add_xx_0_0, 1))
        self.connect((self.audio_source_0, 0), (self.blocks_multiply_const_vxx_0, 0))
        self.connect((self.audio_source_0, 1), (self.blocks_multiply_const_vxx_0_0, 0))
        self.connect((self.audio_source_0, 1), (self.blocks_selector_0_0, 1))
        self.connect((self.blocks_add_xx_0, 0), (self.blocks_selector_0, 1))
        self.connect((self.blocks_add_xx_0_0, 0), (self.blocks_selector_0_0, 0))
        self.connect((self.blocks_float_to_complex_0, 0), (self.qtgui_sink_x_0, 0))
        self.connect((self.blocks_multiply_const_vxx_0, 0), (self.blocks_add_xx_0, 1))
        self.connect((self.blocks_multiply_const_vxx_0, 0), (self.blocks_multiply_const_vxx_0_0_0, 0))
        self.connect((self.blocks_multiply_const_vxx_0, 0), (self.blocks_selector_0, 0))
        self.connect((self.blocks_multiply_const_vxx_0_0, 0), (self.blocks_add_xx_0, 0))
        self.connect((self.blocks_multiply_const_vxx_0_0_0, 0), (self.blocks_add_xx_0_0, 0))
        self.connect((self.blocks_selector_0, 0), (self.blocks_float_to_complex_0, 0))
        self.connect((self.blocks_selector_0_0, 0), (self.blocks_float_to_complex_0, 1))


    def closeEvent(self, event):
        self.settings = Qt.QSettings("GNU Radio", "vws_Sdr_KI3P")
        self.settings.setValue("geometry", self.saveGeometry())
        self.stop()
        self.wait()

        event.accept()

    def get_samp_rate(self):
        return self.samp_rate

    def set_samp_rate(self, samp_rate):
        self.samp_rate = samp_rate
        self.qtgui_sink_x_0.set_frequency_range(0, self.samp_rate)

    def get_phase(self):
        return self.phase

    def set_phase(self, phase):
        self.phase = phase
        self.blocks_multiply_const_vxx_0_0.set_k(self.phase)
        self.blocks_multiply_const_vxx_0_0_0.set_k(self.phase)
        self.blocks_selector_0.set_input_index(0 if self.phase < 0 else 1)
        self.blocks_selector_0_0.set_input_index(0 if self.phase < 0 else 1)

    def get_gain(self):
        return self.gain

    def set_gain(self, gain):
        self.gain = gain
        self.blocks_multiply_const_vxx_0.set_k(-self.gain)

    def get_freq(self):
        return self.freq

    def set_freq(self, freq):
        self.freq = freq

    def get_amp(self):
        return self.amp

    def set_amp(self, amp):
        self.amp = amp




def main(top_block_cls=vws_Sdr_KI3P, options=None):

    if StrictVersion("4.5.0") <= StrictVersion(Qt.qVersion()) < StrictVersion("5.0.0"):
        style = gr.prefs().get_string('qtgui', 'style', 'raster')
        Qt.QApplication.setGraphicsSystem(style)
    qapp = Qt.QApplication(sys.argv)

    tb = top_block_cls()

    tb.start()

    tb.show()

    def sig_handler(sig=None, frame=None):
        tb.stop()
        tb.wait()

        Qt.QApplication.quit()

    signal.signal(signal.SIGINT, sig_handler)
    signal.signal(signal.SIGTERM, sig_handler)

    timer = Qt.QTimer()
    timer.start(500)
    timer.timeout.connect(lambda: None)

    qapp.exec_()

if __name__ == '__main__':
    main()
