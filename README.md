Readme · MD
# Seisberry
 
A DIY 3-axis seismometer built on a Raspberry Pi. Three coil geophones (north-south, east-west, vertical) feed a Waveshare ADS1256 24-bit ADC HAT, and Python scripts either plot the signals live or log them to CSV.
 
Based on the open-source Seisberry project.
 
## Hardware
 
- Raspberry Pi (any model with the 40-pin header)
- Waveshare High-Precision AD/DA Board (ADS1256)
- 3 coil geophones in 3D-printed housings, oriented NS / EW / UP
- Geophones wired as differential inputs:
| ADC channel | Axis |
|---|---|
| 1 | NS (north-south) |
| 2 | EW (east-west) |
| 3 | UP (vertical) |
 
## Scripts
 
| File | What it does |
|---|---|
| `seismo_plot.py` | Live scrolling plot of all three axes |
| `seismo_logger.py` | Logs all three axes to CSV, starting a new file every 10 minutes in `Data/` |
| `ADS1256.py`, `config.py` | Waveshare ADS1256 driver and pin config |
 
The ADC runs at a PGA gain of 16, so the input range is about ±0.31 V. Readings are converted to volts with:
 
```
volts = raw * (2 * VREF / PGA_GAIN) / (2^23 - 1)
```
 
### CSV format
 
```
TIMESTAMP,NS,EW,UP
1761435300.123456,0.00123,-0.00041,0.00210
```
 
`TIMESTAMP` is Unix time in seconds; the other columns are volts.
 
## Setup
 
1. Enable SPI:
```bash
   sudo raspi-config   # Interface Options -> SPI -> Enable
   sudo reboot
```
2. Clone and install dependencies:
```bash
   git clone https://github.com/T8Ren/seisberry.git
   cd seisberry
   pip install -r requirements.txt
```
3. Run:
```bash
   python3 seismo_plot.py     # live view (needs a display or VNC)
   python3 seismo_logger.py   # headless logging
```
   Stop either with `Ctrl+C`.
 
## Notes
 
- **Negative readings:** the stock Waveshare `ADS1256_Read_ADC_Data()` mishandles the sign bit (`read &= 0xF000000`), so negative voltages read as 0. The fix is to replace that line with:
```python
  if read & 0x800000:
      read -= 1 << 24
```
- **Sample rate:** each sample switches the ADC's input channel, so the effective rate is limited by the Python loop, not the ADC's data-rate setting. The logger prints the measured rate every 5 seconds.
- **Plot range:** if the live plot looks flat-topped, widen `Y_MIN` / `Y_MAX` in `seismo_plot.py`.
## Credits
 
- Waveshare for the ADS1256 driver code
- [ul-gh/PiPyADC](https://github.com/ul-gh/PiPyADC) and [will127534/RaspberryPi-seismograph](https://github.com/will127534/RaspberryPi-seismograph) for reference
