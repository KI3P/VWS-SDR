/*
 * Credit to the T41 project (https://github.com/KI3P/T41-V12-SDT) for the code that 
 * controls the Si5351.
 *
 * Oliver KI3P, February 2025
 */

#include "si5351.h"

#define SI5351_LOAD_CAPACITANCE SI5351_CRYSTAL_LOAD_8PF
#define SI5351_DRIVE_CURRENT SI5351_DRIVE_2MA
#define SI5351_FREQ_CORRECTION_FACTOR 68000
#define Si_5351_crystal 25000000L
#define SDA 0
#define SCL 1
#define FREQ_MIN_HZ 100000
#define FREQ_MAX_HZ 200000000

Si5351 si5351;
long centerFreq;
long IFFreq;
long long Clk1SetFreq; 
long long Clk0SetFreq;
int multiple;
int oldMultiple;
long long pll_freq;
long long freq;
bool LED_state;
char strBufRes[100];

int EvenDivisor(long freq2) {
  // next 6 ifs added by DRM VK3KQT for use by a phase method of time delay described by
  // https://tj-lab.org/2020/08/27/si5351単体で3mhz以下の直交信号を出力する/
  // for below 3.2MHz the ~limit of PLLA @ 400MHz for a 126 divider
  if (freq2 < 100000)
      multiple = 8192;

  if ((freq2 >= 100000) && (freq2 < 200000))   // PLLA 409.6 MHz to 819.2 MHz
     multiple = 4096;
  
  if ((freq2 >= 200000) && (freq2 < 400000))   //   ""          "" 
     multiple = 2048;

  if ((freq2 >= 400000) && (freq2 < 800000))   //    ""          ""
     multiple = 1024;

  if ((freq2 >= 800000) && (freq2 < 1600000))   //    ""         ""
     multiple = 512;

  if ((freq2 >= 1600000) && (freq2 < 3200000))   //    ""        ""
     multiple = 256;
   //==================================================================  
  // the original multiple
  // if (freq2 < 6850000)
  if ((freq2 >= 3200000) && (freq2 < 6850000))   // 403.2 MHz - 863.1 MHz
    multiple = 126;

  if ((freq2 >= 6850000) && (freq2 < 9500000))
    multiple = 88;

  if ((freq2 >= 9500000) && (freq2 < 13600000))
    multiple = 64;

  if ((freq2 >= 13600000) && (freq2 < 17500000))
    multiple = 44;

  if ((freq2 >= 17500000) && (freq2 < 25000000))
    multiple = 34;

  if ((freq2 >= 25000000) && (freq2 < 36000000))
    multiple = 24;

  if ((freq2 >= 36000000) && (freq2 < 45000000))
    multiple = 18;

  if ((freq2 >= 45000000) && (freq2 < 60000000))
    multiple = 14;

  if ((freq2 >= 60000000) && (freq2 < 80000000))
    multiple = 10;

  if ((freq2 >= 80000000) && (freq2 < 100000000))
    multiple = 8;

  if ((freq2 >= 100000000) && (freq2 < 150000000)) // G0ORX changed upper limit
    multiple = 6;

  if ((freq2 >= 150000000) && (freq2 < 220000000))
    multiple = 4;

  // ? G0ORX - for higher bands
  if(freq2>=220000000) {
    multiple = 2;
  }
  return multiple;
}

void SetFreq() {   // reworked VK3KQT

  long long f=centerFreq;
  Clk1SetFreq = ((f * SI5351_FREQ_MULT) + IFFreq * SI5351_FREQ_MULT);
  multiple = EvenDivisor(Clk1SetFreq / SI5351_FREQ_MULT);
  pll_freq = Clk1SetFreq * multiple;
  freq = pll_freq / multiple;     // is this equal to Clk1SetFreq?
  
  if ( multiple == oldMultiple) {               // Still within the same multiple range 
      si5351.set_pll(pll_freq, SI5351_PLLA);    // just change PLLA on each frequency change of encoder
                                                // this minimizes I2C data for each frequency change within a 
                                                // multiple range
  }
  else { 
    if ( multiple <= 126) {                                 // this the library setting of phase for freqs
        si5351.set_freq_manual(freq, pll_freq, SI5351_CLK0);  // greater than 3.2MHz where multiple is <= 126
        si5351.set_freq_manual(freq, pll_freq, SI5351_CLK1);   // set both clocks to new frequency
        si5351.set_phase(SI5351_CLK0, 0);                      // CLK0 phase = 0 
        si5351.set_phase(SI5351_CLK1, multiple);               // Clk1 phase = multiple for 90 degrees(digital delay)
        si5351.pll_reset(SI5351_PLLA);                         // reset PLLA to align outputs 
        si5351.output_enable(SI5351_CLK0, 1);                  // set outputs on or off
        si5351.output_enable(SI5351_CLK1, 1);
        si5351.output_enable(SI5351_CLK2, 0);
    }
    else {        // this is the timed delay technique for frequencies below 3.2MHz as detailed in 
                  // https://tj-lab.org/2020/08/27/si5351単体で3mhz以下の直交信号を出力する/
        // cli and sei need to be disabled on Pico for some reason. Isn't a problem because
        // we don't use any interrupts in this simple code.
        //cli();                //__disable_irq(); or __enable_irq();     // or cli()/sei() pair; needed to get accurate timing??
        //si5351.output_enable(SI5351_CLK0, 0);  // optional switch off clocks if audio effects are generated
        //si5351.output_enable(SI5351_CLK1, 0);  //  with the change of multiple below 3.2MHz
        si5351.set_freq_manual((freq - 400ULL), pll_freq, SI5351_CLK0);  // set up frequencies of CLK 0/1 4 Hz low
        si5351.set_freq_manual((freq - 400ULL), pll_freq, SI5351_CLK1);  // as per TJ-Labs article 
        si5351.set_phase(SI5351_CLK0, 0);                          // set phase registers to 0 just to be sure
        si5351.set_phase(SI5351_CLK1, 0);                          
        si5351.pll_reset(SI5351_PLLA);                             // align both clockss in phase
        si5351.set_freq_manual(freq, pll_freq, SI5351_CLK0);       // set clock 0  to required freq
        //delayNanoseconds(625000000);       // 62.5 * 1000000      //configured for a 62.5 mSec delay at 4 Hz difference 
        delayMicroseconds(58500);                       //nominally 62500 this figure can be adjusted for a more exact delay which is phase
        si5351.set_freq_manual(freq, pll_freq, SI5351_CLK1);       // set CLK 1 to the required freq after delay
        //sei();
        si5351.output_enable(SI5351_CLK0, 1);                      // switch them on to be sure
        si5351.output_enable(SI5351_CLK1, 1);                      //    ""        ""
        si5351.output_enable(SI5351_CLK2, 0);
      }
  }
  oldMultiple = multiple;
}

void scanner() {
  byte error, address;
  int nDevices;

  Serial.println("Scanning...");

  nDevices = 0;
  for(address = 1; address < 127; address++ )
  {
    // The i2c_scanner uses the return value of
    // the Write.endTransmisstion to see if
    // a device did acknowledge to the address.
    Wire.beginTransmission(address);
    error = Wire.endTransmission();

    if (error == 0)
    {
      Serial.print("I2C device found at address 0x");
      if (address<16)
        Serial.print("0");
      Serial.print(address,HEX);
      Serial.println("  !");

      nDevices++;
    }
    else if (error==4)
    {
      Serial.print("Unknown error at address 0x");
      if (address<16)
        Serial.print("0");
      Serial.println(address,HEX);
    }
  }
  if (nDevices == 0)
    Serial.println("No I2C devices found\n");
  else
    Serial.println("done\n");

}

void setup() {
  Serial.begin(115200);
  delay(500);
  Wire.setSDA(SDA);
  Wire.setSCL(SCL);

  while (!si5351.init(SI5351_LOAD_CAPACITANCE, Si_5351_crystal, SI5351_FREQ_CORRECTION_FACTOR)){
    Serial.println("Unable to connect to Si5351");
    scanner();
    delay(3000);
  }
  si5351.drive_strength(SI5351_CLK0, SI5351_DRIVE_CURRENT);
  si5351.drive_strength(SI5351_CLK1, SI5351_DRIVE_CURRENT);
  si5351.set_ms_source(SI5351_CLK0, SI5351_PLLA);
  si5351.set_ms_source(SI5351_CLK1, SI5351_PLLA);

  IFFreq = 0;
  centerFreq = 10000000;
  SetFreq();
}

int read_input(String *command, int *value){
  String selection = Serial.readString();  //read until timeout
  selection.trim();                        // remove any \r \n whitespace at the end of the String
  selection.toUpperCase();
  // We receive strings in the form "CM VALUE". Check for valid formatting
  if (selection.length() < 4){
    sprintf(strBufRes,"Command string too short! Length %d < mininimum length 4: ",selection.length());
    Serial.print(strBufRes);
    Serial.println(selection);
    return 1;
  }
  if (selection[2] != ' '){
    sprintf(strBufRes,"3rd character must be a space: ",selection);
    Serial.print(strBufRes);
    Serial.println(selection);
    return 1;
  }
  String value_str = selection.substring(3);
  *command = selection.substring(0, 2);
  *value = value_str.toInt();
  return 0;
}

void loop() {
  Serial.println("ENTER FREQUENCY IN HZ:");
  Serial.println("FR 123456");

  while (Serial.available() == 0) {
  }     //wait for data available
  String command;
  int value;
  if (!read_input(&command, &value)) {      
    if (command == "FR"){
      if ((value >= FREQ_MIN_HZ) & (value <= FREQ_MAX_HZ)){
        centerFreq = value;
        SetFreq();
        Serial.println("OK");
      } else {
        sprintf(strBufRes,"Frequency %d outside of valid range %d to %d!\n",value,FREQ_MIN_HZ,FREQ_MAX_HZ);
        Serial.print(strBufRes);
      }
    } else {
      Serial.print("Unrecognized command: ");
      Serial.println(command);
    }
  }

}
