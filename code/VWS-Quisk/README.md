Lab notebook on how I got quisk to operate with the VWS-SDR:

---- Install tuner software on VWS SDR
I use a Python tuner on the Pico to tune the SDR.  It works similarly to the Arduino sketch in the
KI3P git repo, the only difference is commands are terminated by a newline (\n) in the Python
code, versus carriage return (\r) in the sketch.  If the preferred tuner is the sketch, just
edit this line in vwsquiskpkg/quisk_hardware.py:

   self.serial.write(b'FR %d\r'%(vfo+correction))

And change to \r to \n.  The original thinking in using Python for the VWS was to facilitate the
extensive driver libraries Adafruit provides for their peripherals, as well as the ease of use
and velocity of development Python brings to low speed control applications.

To install the Python tuner, the Pico must first be loaded with CircuitPython as described
here https://learn.adafruit.com/getting-started-with-raspberry-pi-pico-circuitpython/circuitpython.
Once CircuitPython is installed and booted, you will see a virtual disk drive for the board
appear.  On my machine it is /media/rick/CIRCUITPY.

To run the tuner, copy vws_tuner/{code.py,vws_tuner.py}
to the virtual disk drive, and power cycle the board.  To verify operation, connnect to the
serial port associated with the board (here, it is /dev/ttyACM0, 115200 bps), and type a
carriage return.  You should see a tune> prompt, and entering a command like FR 7074000
will cause the 5351 to tune to 7.074 mhz.  As required by the VWS SDR designs, clk0/clk1
are in quadrature.  The Python script works similarly to various 5351 libraries to generate
quadrature clocks: PLLA is a integer multiple of the desired frequency (factor of 4).

My eventual goal is to eliminate the need for a sound board and get IQ sent over USB to quisk
directly.  The current state of CircuitPython may not support bulk data transfer via USB, and
if so, I'll likely switch to using the Raspi SDK to write an appropriate driver.

---- Install quisk
Quisk documentation:  https://james.ahlstrom.name/quisk/docs.html
Quisk github: https://github.com/jimahlstrom/quisk
Build Quisk according to https://james.ahlstrom.name/quisk/docs.html#Installation

Once quisk is built, copy the included vwsquiskpkg directory into the quisk distribution directory (I run
quisk in the build location).

Note: This is the way new radios are introduced to the quisk radio configuration manager: for a new radio
named xyzzy, you create a directory named xyzzypkg in the quisk directory, and write a quisk_hardware.py
module.  Python class inheritence will define most of the necessary routines, but functionally you'll want
open/close/tune method as shown in the vwsquiskpkg version.

From the command line "python3 quisk.py" will start quisk.

---- Configure Quisk
To add the VWS SDR as a radio, click the Config Button, then select the Radios tab.
In the Radios config panel, select the "Add a new radio with the general type", and select the VWS SDR item,
name the radio "VWS"

You should see a new Radio appear just below the title bar named "VWS".  Click that item,
and then select the Hardware tab.  Enter the serial port name (in my case it was /dev/ttyACM0).
Click the Audio tab, and choose appropriate settings for "Radio Sound Output" and "Microphone
Input".  In Digital Rx0 line, select pulse: Use name QuiskDigitalOutput.monitor.  Of couse,
you'll need to have loaded the pulse audio system.  Note that I have not tested any of this
on Mac or Windows, and wouldn't expect it to work out of the box on either system type.

Back on the Config Radios screen, select VWS in the "When Quisk starts, use the radio" line.

In the Config tab, quisk provides the ability to adjust IQ balance via "Adjust receive amplitude
and phase".  I manually adjusted this using a signal generator tuned to the vicinity of 14.074 mhz,
and then saved the result.

---- Configure WSJT-X if desired
To use the WSJT-X integration, use the package manager to install wsjtx, or build from source.

I've been starting wsjtx manually within quisk: Click Config, select the Config tab, then look for the
Start WSJT-X item.  The drop down menu has an option Main Rx0 Now item - select that and
quisk will start the wsjtx application.  Once you've fully debugged the quisk:wsjtx integration,
setting "Start WSJT-X" to "Main Rx0 on startup" on the Config menus, Config tab will automatically
start up wstjx when quisk starts.

The included screen captures show some of the details of getting quisk to interoperate with
wsjtx.  Note that quisk won't stream audio on QuiskDigitalOutput.monitor unless you're
in a digital mode (see DGT-U).

Quisk can be controlled by hamlib.  In the Config screens, select the VWS radio, then
Remote tab.  On the Remote config screen, set the port to 4532.  You'll have to restart
quisk for the setting to take effect.  After this is done, you can use rigctl -m 2 to
test: for example, the command "F 14074000" will tune quisk to the FT8 band on 20M.  Once
the hamlib integration has been confirmed as working, you'll be able to control quisk
via the wsjtx application, i.e. switching bands, frequencies in that app, and quisk following
along as a normal radio would.

----
I've not provided a "LICENSE" for any of this work, as it is mostly just a few learnings about
how to get Quisk working with the VWS SDR.  Any IP contained herein may be used for free and
for any purpose, and as usual, I'm to be held harmless for its use.



