import csv
import time
import os

import ADS1256
import RPi.GPIO as GPIO

VREF = 2.5
PGA_GAIN = 16
FULL_SCALE = (2.0*VREF)/PGA_GAIN
CHANNELS = {1: "NS", 2: "EW", 3: "UP"}
CYCLE_DURATION = 10 * 60

adc = ADS1256.ADS1256()
adc.ADS1256_init()
adc.ADS1256_ConfigADC(
    ADS1256.ADS1256_GAIN_E['ADS1256_GAIN_16'],
    ADS1256.ADS1256_DRATE_E['ADS1256_30000SPS'],
)

if not os.path.isdir("Data"):
    os.makedirs("Data")

try:
    while True:
        filename = "Data/Reading_{}.csv".format(time.strftime("%Y-%m-%d_%H-%M-%S"))
        print(f"Starting new cycle ->{filename}")
        
        with open(filename, "w", newline = "") as f:
            writer = csv.writer(f)
            writer.writerow(["TIMESTAMP","NS","EW","UP"])
            
            cycle_start = time.time()
            sample_count = 0
            rate_check_start = cycle_start
            
            
            while time.time() - cycle_start < CYCLE_DURATION:
                row = [time.strftime("%H:%M:%S")]
                for ch in CHANNELS:
                    adc.ADS1256_SetDiffChannal(ch)
                    adc.ADS1256_WriteCmd(ADS1256.CMD['CMD_SYNC'])
                    adc.ADS1256_WriteCmd(ADS1256.CMD['CMD_WAKEUP'])
                    raw = adc.ADS1256_Read_ADC_Data()
                    volts = (raw * FULL_SCALE) / 2**23-1
                    row.append(volts)
                writer.writerow(row)
                f.flush()
                
                sample_count+=1
                elapsed = time.time()-rate_check_start
                if elapsed >= 5:
                    print(f"Rate: {sample_count / elapsed:.1f} samples/sec")
                    sample_count = 0
                    rate_check_start = time.time()
                    
                
                print(f"Cycle_complete.Saved to {filename}")
except KeyboardInterrupt:
    print("\nStopped.")
finally:
    GPIO.cleanup()