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
from PyQt5.QtCore import QObject, pyqtSlot
from gnuradio import qtgui
from gnuradio.filter import firdes
import sip
from gnuradio import analog
from gnuradio import audio
from gnuradio import blocks
from gnuradio import filter
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
        self.volume = volume = 0.7
        self.tune_freq_kHz = tune_freq_kHz = 10000
        self.samp_rate = samp_rate = 48000
        self.reverse = reverse = -1
        self.phase = phase = 0
        self.if_freq_kHz = if_freq_kHz = 6
        self.gain = gain = 1
        self.bfo = bfo = 1500

        ##################################################
        # Blocks
        ##################################################
        self._volume_range = Range(0, 1.0, 0.05, 0.7, 200)
        self._volume_win = RangeWidget(self._volume_range, self.set_volume, "Volume", "counter_slider", float, QtCore.Qt.Horizontal)
        self.top_grid_layout.addWidget(self._volume_win, 2, 0, 1, 3)
        for r in range(2, 3):
            self.top_grid_layout.setRowStretch(r, 1)
        for c in range(0, 3):
            self.top_grid_layout.setColumnStretch(c, 1)
        # Create the options list
        self._reverse_options = [-1, 1, 0]
        # Create the labels list
        self._reverse_labels = ['Upper', 'Lower', 'BFO']
        # Create the combo box
        # Create the radio buttons
        self._reverse_group_box = Qt.QGroupBox("Sideband" + ": ")
        self._reverse_box = Qt.QHBoxLayout()
        class variable_chooser_button_group(Qt.QButtonGroup):
            def __init__(self, parent=None):
                Qt.QButtonGroup.__init__(self, parent)
            @pyqtSlot(int)
            def updateButtonChecked(self, button_id):
                self.button(button_id).setChecked(True)
        self._reverse_button_group = variable_chooser_button_group()
        self._reverse_group_box.setLayout(self._reverse_box)
        for i, _label in enumerate(self._reverse_labels):
            radio_button = Qt.QRadioButton(_label)
            self._reverse_box.addWidget(radio_button)
            self._reverse_button_group.addButton(radio_button, i)
        self._reverse_callback = lambda i: Qt.QMetaObject.invokeMethod(self._reverse_button_group, "updateButtonChecked", Qt.Q_ARG("int", self._reverse_options.index(i)))
        self._reverse_callback(self.reverse)
        self._reverse_button_group.buttonClicked[int].connect(
            lambda i: self.set_reverse(self._reverse_options[i]))
        self.top_grid_layout.addWidget(self._reverse_group_box, 3, 2, 1, 1)
        for r in range(3, 4):
            self.top_grid_layout.setRowStretch(r, 1)
        for c in range(2, 3):
            self.top_grid_layout.setColumnStretch(c, 1)
        self._phase_range = Range(-0.1, 0.1, 0.001, 0, 200)
        self._phase_win = RangeWidget(self._phase_range, self.set_phase, "'phase'", "counter_slider", float, QtCore.Qt.Horizontal)
        self.top_layout.addWidget(self._phase_win)
        self._gain_range = Range(0.6, 1.4, 0.001, 1, 200)
        self._gain_win = RangeWidget(self._gain_range, self.set_gain, "'gain'", "counter_slider", float, QtCore.Qt.Horizontal)
        self.top_layout.addWidget(self._gain_win)
        self._bfo_range = Range(0, 3000, 10, 1500, 200)
        self._bfo_win = RangeWidget(self._bfo_range, self.set_bfo, "Fine tuning", "counter_slider", float, QtCore.Qt.Horizontal)
        self.top_grid_layout.addWidget(self._bfo_win, 4, 0, 1, 3)
        for r in range(4, 5):
            self.top_grid_layout.setRowStretch(r, 1)
        for c in range(0, 3):
            self.top_grid_layout.setColumnStretch(c, 1)
        self.qtgui_sink_x_0 = qtgui.sink_c(
            1024, #fftsize
            window.WIN_BLACKMAN_hARRIS, #wintype
            (tune_freq_kHz-if_freq_kHz)*1000, #fc
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

        self.qtgui_sink_x_0.enable_rf_freq(True)

        self.top_layout.addWidget(self._qtgui_sink_x_0_win)
        self.qtgui_edit_box_msg_0 = qtgui.edit_box_msg(qtgui.INT, '10000', 'Tune Frequency [kHz]', True, True, 'frequency_kHz', None)
        self._qtgui_edit_box_msg_0_win = sip.wrapinstance(self.qtgui_edit_box_msg_0.qwidget(), Qt.QWidget)
        self.top_layout.addWidget(self._qtgui_edit_box_msg_0_win)
        self.freq_xlating_fir_filter_xxx_0 = filter.freq_xlating_fir_filter_ccf(1, firdes.low_pass(1,samp_rate,3000, 200), if_freq_kHz*1000, samp_rate)
        self.epy_block_0 = epy_block_0.blk(serial_port="/dev/ttyACM0")
        self.blocks_selector_0_0 = blocks.selector(gr.sizeof_float*1,0 if phase < 0 else 1,0)
        self.blocks_selector_0_0.set_enabled(True)
        self.blocks_selector_0 = blocks.selector(gr.sizeof_float*1,0 if phase < 0 else 1,0)
        self.blocks_selector_0.set_enabled(True)
        self.blocks_multiply_xx_0_0 = blocks.multiply_vff(1)
        self.blocks_multiply_xx_0 = blocks.multiply_vff(1)
        self.blocks_multiply_const_vxx_0_1 = blocks.multiply_const_ff(volume)
        self.blocks_multiply_const_vxx_0_0_1 = blocks.multiply_const_ff(reverse)
        self.blocks_multiply_const_vxx_0_0_0 = blocks.multiply_const_ff(phase)
        self.blocks_multiply_const_vxx_0_0 = blocks.multiply_const_ff(phase)
        self.blocks_multiply_const_vxx_0 = blocks.multiply_const_ff(-gain)
        self.blocks_msgpair_to_var_0 = blocks.msg_pair_to_var(self.set_tune_freq_kHz)
        self.blocks_float_to_complex_0 = blocks.float_to_complex(1)
        self.blocks_complex_to_float_0 = blocks.complex_to_float(1)
        self.blocks_add_xx_0_1 = blocks.add_vff(1)
        self.blocks_add_xx_0_0 = blocks.add_vff(1)
        self.blocks_add_xx_0 = blocks.add_vff(1)
        self.audio_source_0 = audio.source(samp_rate, 'hw:0,0', True)
        self.audio_sink_0_0 = audio.sink(48000, '', True)
        self.analog_sig_source_x_0_0 = analog.sig_source_f(samp_rate, analog.GR_SIN_WAVE, bfo, 1, 0, 0)
        self.analog_sig_source_x_0 = analog.sig_source_f(samp_rate, analog.GR_COS_WAVE, bfo, 1, 0, 0)


        ##################################################
        # Connections
        ##################################################
        self.msg_connect((self.qtgui_edit_box_msg_0, 'msg'), (self.blocks_msgpair_to_var_0, 'inpair'))
        self.msg_connect((self.qtgui_edit_box_msg_0, 'msg'), (self.epy_block_0, 'frequencyPort'))
        self.connect((self.analog_sig_source_x_0, 0), (self.blocks_multiply_xx_0, 0))
        self.connect((self.analog_sig_source_x_0_0, 0), (self.blocks_multiply_xx_0_0, 1))
        self.connect((self.audio_source_0, 1), (self.blocks_add_xx_0_0, 1))
        self.connect((self.audio_source_0, 0), (self.blocks_multiply_const_vxx_0, 0))
        self.connect((self.audio_source_0, 1), (self.blocks_multiply_const_vxx_0_0, 0))
        self.connect((self.audio_source_0, 1), (self.blocks_selector_0_0, 1))
        self.connect((self.blocks_add_xx_0, 0), (self.blocks_selector_0, 1))
        self.connect((self.blocks_add_xx_0_0, 0), (self.blocks_selector_0_0, 0))
        self.connect((self.blocks_add_xx_0_1, 0), (self.blocks_multiply_const_vxx_0_1, 0))
        self.connect((self.blocks_complex_to_float_0, 0), (self.blocks_multiply_xx_0, 1))
        self.connect((self.blocks_complex_to_float_0, 1), (self.blocks_multiply_xx_0_0, 0))
        self.connect((self.blocks_float_to_complex_0, 0), (self.freq_xlating_fir_filter_xxx_0, 0))
        self.connect((self.blocks_float_to_complex_0, 0), (self.qtgui_sink_x_0, 0))
        self.connect((self.blocks_multiply_const_vxx_0, 0), (self.blocks_add_xx_0, 1))
        self.connect((self.blocks_multiply_const_vxx_0, 0), (self.blocks_multiply_const_vxx_0_0_0, 0))
        self.connect((self.blocks_multiply_const_vxx_0, 0), (self.blocks_selector_0, 0))
        self.connect((self.blocks_multiply_const_vxx_0_0, 0), (self.blocks_add_xx_0, 0))
        self.connect((self.blocks_multiply_const_vxx_0_0_0, 0), (self.blocks_add_xx_0_0, 0))
        self.connect((self.blocks_multiply_const_vxx_0_0_1, 0), (self.blocks_add_xx_0_1, 1))
        self.connect((self.blocks_multiply_const_vxx_0_1, 0), (self.audio_sink_0_0, 0))
        self.connect((self.blocks_multiply_xx_0, 0), (self.blocks_add_xx_0_1, 0))
        self.connect((self.blocks_multiply_xx_0_0, 0), (self.blocks_multiply_const_vxx_0_0_1, 0))
        self.connect((self.blocks_selector_0, 0), (self.blocks_float_to_complex_0, 0))
        self.connect((self.blocks_selector_0_0, 0), (self.blocks_float_to_complex_0, 1))
        self.connect((self.freq_xlating_fir_filter_xxx_0, 0), (self.blocks_complex_to_float_0, 0))


    def closeEvent(self, event):
        self.settings = Qt.QSettings("GNU Radio", "vws_Sdr_KI3P")
        self.settings.setValue("geometry", self.saveGeometry())
        self.stop()
        self.wait()

        event.accept()

    def get_volume(self):
        return self.volume

    def set_volume(self, volume):
        self.volume = volume
        self.blocks_multiply_const_vxx_0_1.set_k(self.volume)

    def get_tune_freq_kHz(self):
        return self.tune_freq_kHz

    def set_tune_freq_kHz(self, tune_freq_kHz):
        self.tune_freq_kHz = tune_freq_kHz
        self.qtgui_sink_x_0.set_frequency_range((self.tune_freq_kHz-self.if_freq_kHz)*1000, self.samp_rate)

    def get_samp_rate(self):
        return self.samp_rate

    def set_samp_rate(self, samp_rate):
        self.samp_rate = samp_rate
        self.analog_sig_source_x_0.set_sampling_freq(self.samp_rate)
        self.analog_sig_source_x_0_0.set_sampling_freq(self.samp_rate)
        self.freq_xlating_fir_filter_xxx_0.set_taps(firdes.low_pass(1,self.samp_rate,3000, 200))
        self.qtgui_sink_x_0.set_frequency_range((self.tune_freq_kHz-self.if_freq_kHz)*1000, self.samp_rate)

    def get_reverse(self):
        return self.reverse

    def set_reverse(self, reverse):
        self.reverse = reverse
        self._reverse_callback(self.reverse)
        self.blocks_multiply_const_vxx_0_0_1.set_k(self.reverse)

    def get_phase(self):
        return self.phase

    def set_phase(self, phase):
        self.phase = phase
        self.blocks_multiply_const_vxx_0_0.set_k(self.phase)
        self.blocks_multiply_const_vxx_0_0_0.set_k(self.phase)
        self.blocks_selector_0.set_input_index(0 if self.phase < 0 else 1)
        self.blocks_selector_0_0.set_input_index(0 if self.phase < 0 else 1)

    def get_if_freq_kHz(self):
        return self.if_freq_kHz

    def set_if_freq_kHz(self, if_freq_kHz):
        self.if_freq_kHz = if_freq_kHz
        self.freq_xlating_fir_filter_xxx_0.set_center_freq(self.if_freq_kHz*1000)
        self.qtgui_sink_x_0.set_frequency_range((self.tune_freq_kHz-self.if_freq_kHz)*1000, self.samp_rate)

    def get_gain(self):
        return self.gain

    def set_gain(self, gain):
        self.gain = gain
        self.blocks_multiply_const_vxx_0.set_k(-self.gain)

    def get_bfo(self):
        return self.bfo

    def set_bfo(self, bfo):
        self.bfo = bfo
        self.analog_sig_source_x_0.set_frequency(self.bfo)
        self.analog_sig_source_x_0_0.set_frequency(self.bfo)




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
