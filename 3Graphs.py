import time
import matplotlib.pyplot as plt

import ADS1256
import RPi.GPIO as GPIO

VREF = 2.5
PGA_GAIN = 16
FULL_SCALE = (2.0 * VREF) / PGA_GAIN

CHANNELS = {1: "NS", 2: "EW", 3: "UP"}
WINDOW = 300  # number of points to keep on screen

# Fixed y-axis range in volts. Adjust these if your signal gets clipped
# (looks flat-topped) or if it's too small to see -- narrower range =
# more visible detail on small taps, but big taps may get cut off.
Y_MIN = -0.05
Y_MAX = 0.05

adc = ADS1256.ADS1256()
adc.ADS1256_init()
# Fast data rate + gain so the chip can keep up with a quick tap/drop
# instead of using whatever slow default it powers up with.
adc.ADS1256_ConfigADC(
    ADS1256.ADS1256_GAIN_E['ADS1256_GAIN_16'],
    ADS1256.ADS1256_DRATE_E['ADS1256_30000SPS'],
)

# one list of readings per channel
history = {ch: [] for ch in CHANNELS}
times = []
start = time.time()

plt.ion()  # turn on interactive mode so the plot updates live
fig, ax = plt.subplots()

# Create each line once and reuse it -- much cheaper than clearing and
# replotting from scratch every frame, which was the main thing slowing
# this down.
lines = {}
for ch, name in CHANNELS.items():
    (line,) = ax.plot([], [], label=name)
    lines[ch] = line
ax.legend()
ax.set_xlabel("Time (s)")
ax.set_ylabel("Voltage (V)")
ax.set_ylim(Y_MIN, Y_MAX)
ax.set_xlim(0, WINDOW * 0.01)  # rough initial guess, gets corrected below

REDRAW_EVERY = 5  # only refresh the screen every N samples -- sampling
                   # itself can run much faster than the screen needs to

try:
    sample_count = 0
    while True:
        now = time.time() - start
        times.append(now)

        for ch, name in CHANNELS.items():
            adc.ADS1256_SetDiffChannal(ch)
            adc.ADS1256_WriteCmd(ADS1256.CMD['CMD_SYNC'])
            adc.ADS1256_WriteCmd(ADS1256.CMD['CMD_WAKEUP'])
            raw = adc.ADS1256_Read_ADC_Data()
            volts = (raw * FULL_SCALE) / (2**23 - 1)
            history[ch].append(volts)

        # trim to the last WINDOW points so the plot doesn't slow down
        if len(times) > WINDOW:
            times = times[-WINDOW:]
            for ch in CHANNELS:
                history[ch] = history[ch][-WINDOW:]

        sample_count += 1
        if sample_count % REDRAW_EVERY == 0:
            for ch, line in lines.items():
                line.set_data(times, history[ch])
            ax.set_xlim(times[0], times[-1] if times[-1] > times[0] else times[0] + 1)
            fig.canvas.draw_idle()
            plt.pause(0.001)  # just enough to let the GUI event loop breathe

except KeyboardInterrupt:
    print("\nStopped.")
finally:
    GPIO.cleanup()