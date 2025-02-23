# w1dsp VWS tuner for CircuitPython
# derived from various sources: NT7S, KI3P, etal

import board
import busio
import time

# KISS tuner class for si5351.  Should run in CircuitPython
# with no additional libraries
# the class just sets quadrature clocks clk0, clk1, and
# is otherwise defined by all the other bells and whistles
# it doesn't support compared to more complete libraries
# like Etherkit, etc

class si5351:

    si5351_xtal = 25000000
    si5351_xtalpf = 3   # 10 pf
    si5351_drive = 3

    debug = False

    def __init__(self, i2c_addr, SCL, SDA, correction=0, initial_frequency=14000000):
        self.i2c_addr = i2c_addr
        self.SCL = SCL
        self.SDA = SDA
        self.i2c = busio.I2C(SCL, SDA)
        self.xtal_freq = self.si5351_xtal + correction
        self._init_(initial_frequency)
        
    def __del__(self):
        self.SCL = None
        self.SDA = None
        del self.i2c
    
    def i2c_write(self, reg, vals):
        while not self.i2c.try_lock():
            time.sleep(.01)
        if not isinstance(vals, list):
            vals = [vals]
        if self.debug:
            print(f"i2c_write: reg {reg}, values {[hex(x) for x in vals]}")
        l = [reg]
        l.extend(vals)
        self.i2c.writeto(self.i2c_addr, bytearray(l))
        self.i2c.unlock()

    def i2c_read(self, reg, cnt=1):
        while not self.i2c.try_lock():
            time.sleep(.01)
        result = bytearray(cnt)
        self.i2c.writeto(self.i2c_addr, bytearray([reg]))
        self.i2c.readfrom_into(self.i2c_addr, result)
        self.i2c.unlock()
        return result

    # pack PLL feedback control words
    def _pack_msn(self, p1, p2, p3):
        return [(p3>>8)&0xff, p3&0xff,
                (p1>>16)&0b11, (p1>>8)&0xff, p1&0xff,
                (((p3>>16)&0b1111)<<4) | ((p2>>16)&0b1111),
                (p2>>8)&0xff, p2&0xff, (p3>>8)&0xff, p3&0xff]
    
    # pack multisynth control words
    def _pack_msa(self, p1, p2, p3, rdiv=0, divby4=0b00):
        return [(p3>>8)&0xff, p3&0xff,
                (rdiv&0b111)<<4 | divby4<<2 | (p1>>16)&0b11 ,
                (p1>>8)&0xff, p1&0xff,
                ((p3>>16)&0b1111)<<4 | (p2>>16)&0b1111,
                (p2>>8)&0xff, p2&0xff]
    
    def _init_(self, initial_frequency):

        # Figure 12 flowchart, si5351 datasheet
        self.i2c_write(3, 0xff)                  # disable clocks
        self.i2c_write(16, [0x80]*3)  # power down clock outputs
        
        self.i2c_write(149, [0x00]*13)          # Spread Spectrum registers: turn off
        self.i2c_write(183, self.si5351_xtalpf<<6)  # Set crystal load capacitance
        self.i2c_write(15, 0)                    # PLLA/PPLB clock source is xtal, divide by 1
        self.i2c_write(24, 0)                    # clk0-3 disable state low
        self.i2c_write(25, 0)                    # clk4-7 disable state low
        
        self.i2c_write(162, [0x00]*3)           # VCXO param
        self.i2c_write(165, [0x00]*3)           # phase offset
        self.i2c_write(187, 0xd0)               # AN619 specifies setting to 0xd0 (pg 61)
        self.setfreq(initial_frequency)
        self.i2c_write(1, 0)                    # clear sticky loss of signal (LOS) bits
        
        if self.debug:
            status = self.i2c_read(0)
            print(f"si5351._init_: status reg 0x{status[0]:02x}")

    def dumpregs(self):
        cnt = 0
        for reg in range(188):
            if (cnt&15) == 0:
                print(f"{reg:3d}:  ", end="")
            v = self.i2c_read(reg)[0]
            print(f"{v:02x} ", end="")
            if (cnt&15) == 15:
                print("")
            cnt += 1
        print("")

    def clk_control(self, clknum, enable):
        clk_mask = self.i2c_read(3)[0]
        if self.debug:
            print(f"read clk_mask {clk_mask:08b}")
        if enable:
            clk_mask &= ~(1<<clknum)
        else:
            clk_mask |= (1<<clknum)
            clk_mask &= 0xff
        if self.debug:
            print(f"write clk_mask {clk_mask:08b}")
        self.i2c_write(3, clk_mask)
            
    # Cut/paste from KI3P Arduino IDE sketch
    # a direct calculation is surely possible, but this method
    # shows the multiplier as a function of frequency range,
    # which is useful for debug
    def _divisor(self, frequency):
        if ((frequency >= 1600000) and (frequency < 3200000)):
            multiple = 256
        if ((frequency >= 3200000) and (frequency < 6850000)):
            multiple = 126
        if ((frequency >= 6850000) and (frequency < 9500000)):
            multiple = 88
        if ((frequency >= 9500000) and (frequency < 13600000)):
            multiple = 64
        if ((frequency >= 13600000) and (frequency < 17500000)):
            multiple = 44
        if ((frequency >= 17500000) and (frequency < 25000000)):
            multiple = 34
        if ((frequency >= 25000000) and (frequency < 36000000)):
            multiple = 24
        if ((frequency >= 36000000) and (frequency < 45000000)):
            multiple = 18
        if ((frequency >= 45000000) and (frequency < 60000000)):
            multiple = 14
        if ((frequency >= 60000000) and (frequency < 80000000)):
            multiple = 10
        if ((frequency >= 80000000) and (frequency < 100000000)):
            multiple = 8
        return multiple

    # set clk0/clk1 to frequency, clk1 is in quadrature to clk0
    # PLLA is set to integer factor of 4 multiple of the desired frequency
    def setfreq(self, freq):

        if freq <= 0 or freq >= 100000000:
            print(f"Frequency out of range: {freq} hz")
            return False
        
        if self.debug:
            print(f"si5351_setfreq({freq})")

        denom = (1<<20)-1
        mult = self._divisor(freq)
        vco = freq*mult
        a = vco // self.xtal_freq
        b = ((vco % self.xtal_freq)*denom) // self.xtal_freq
        c = denom

        if self.debug:
            print(f"frequency {freq} hz, mult {mult}, vco {vco} hz, a {a}, b {b}, c {c} b/c {b/c}")
            
        p1 = int(128*a + (128*b)//c - 512)
        p2 = int(128*b - (128*b)//c)
        p3 = c
        if self.debug:
            print(f"p1 {p1} p2 {p2} p3 {p3}")
        vals = self._pack_msn(p1, p2, p3)       # set PLLA to a 
        self.i2c_write(26, vals)                # Write to 8 PLLA msynth regs 26-33

        divider_vals = self._pack_msa(128*mult-512, 0, 1)
        for clknum in range(2):
            self.clk_control(clknum, False)
            self.i2c_write(16+clknum, 0x80)               # power down clock output
            self.i2c_write(42+clknum*8, divider_vals)     # Write to multisynth regs
            self.i2c_write(16+clknum, 0x0f)               # power up clock
            self.clk_control(clknum, True)
        
        self.i2c_write(166, mult)  # set phase offset
        self.i2c_write(177, 0x20)  # Reset PLLA
        
        if self.debug:
            status = self.i2c_read(0)
            print(f"init: status reg {status[0]:02x}")

        return True
    
def main():

    si = si5351(i2c_addr=0x60, SCL=board.GP1, SDA=board.GP0, initial_frequency=14100000)
    
    while True:
        command = input("tune> ")
        try:
            tokens = command.strip().split()
            if len(tokens)==2 and tokens[0].lower() == "fr":
                frequency = int(tokens[1])
                if not si.setfreq(frequency):
                    print("set frequency failed")
                else:
                    print("OK")
        except:
            print("input error")
            
main()


