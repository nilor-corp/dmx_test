#-------------------------------------------------------------
# DMXController Text DAT
# Paste this into a Text DAT (set to Python), then hit ▶︎ to start.
#-------------------------------------------------------------

import serial, time, threading

class DMXController:
    # DMX Protocol Constants
    DMX_SIZE = 512
    COM_BAUD = 250000
    COM_TIMEOUT = 1
    BREAK_TIME = 0.0001
    MAB_TIME = 0.0001
    INTER_FRAME_DELAY = 0.03

    def __init__(self, port):
        print(f"[DMX] Initializing on {port}...")
        self.dmx_frame = [0] * self.DMX_SIZE
        try:
            self.com = serial.Serial(
                port=port,
                baudrate=self.COM_BAUD,
                timeout=self.COM_TIMEOUT,
                bytesize=serial.EIGHTBITS,
                parity=serial.PARITY_NONE,
                stopbits=serial.STOPBITS_TWO,
                rtscts=False,
                dsrdtr=False
            )
            print(f"[DMX] Opened {self.com.portstr}")
            # Reset line
            self.com.rts = False
            self.com.break_condition = True
            time.sleep(0.1)
            self.com.break_condition = False
            time.sleep(0.1)
            print("[DMX] Initial break sent")
        except Exception as e:
            print(f"[DMX] Error opening {port}: {e}")
            raise

    def set_channel(self, channel, value, autorender=False):
        if not 1 <= channel <= self.DMX_SIZE:
            return
        value = max(0, min(value, 255))
        self.dmx_frame[channel-1] = value
        if autorender:
            self.render()

    def clear(self, channel=0):
        if channel == 0:
            self.dmx_frame = [0] * self.DMX_SIZE
        else:
            self.dmx_frame[channel-1] = 0

    def render(self):
        try:
            # Break + MAB
            self.com.break_condition = True
            time.sleep(self.BREAK_TIME)
            self.com.break_condition = False
            time.sleep(self.MAB_TIME)

            # Start code + data
            self.com.write(b'\x00')
            self.com.write(bytes(self.dmx_frame))
            self.com.flush()
            time.sleep(self.INTER_FRAME_DELAY)
        except Exception as e:
            print(f"[DMX] Render error: {e}")

    def close(self):
        print("[DMX] Closing...")
        self.clear()
        self.render()
        time.sleep(0.1)
        self.com.close()

    def run(self):
        print("[DMX] Starting loop thread...")
        try:
            # Kick things off
            for _ in range(3):
                self.clear()
                self.render()
                time.sleep(0.1)

            while True:
                # Ramp channels 1–4 full on
                for ch in range(1, 5):
                    self.set_channel(ch, 255, autorender=True)
                time.sleep(1)

                # Blackout
                self.clear()
                self.render()
                time.sleep(1)

        except Exception as e:
            print(f"[DMX] Loop stopped: {e}")
        finally:
            self.close()
            print("[DMX] Thread exiting")

# ------------------------------------------------------------
# Change this to match your actual device node
DEVICE_PORT = '/dev/tty.usbserial-AQ01FJYP'

def start_dmx():
    try:
        ctrl = DMXController(DEVICE_PORT)
        thread = threading.Thread(target=ctrl.run, daemon=True)
        thread.start()
    except Exception as e:
        print(f"[DMX] Failed to start: {e}")

# Kick it off
start_dmx()
