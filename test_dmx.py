import serial
import sys
import time

class DMXController:
    # DMX Protocol Constants
    DMX_SIZE = 512
    COM_BAUD = 250000  # Try higher baud rate
    COM_TIMEOUT = 1
    BREAK_TIME = 0.0001  # 100 microseconds
    MAB_TIME = 0.0001   # 100 microseconds
    INTER_FRAME_DELAY = 0.03  # 30 milliseconds

    def __init__(self, port):
        print(f"Initializing DMX controller on port {port}...")
        self.dmx_frame = [0] * self.DMX_SIZE
        try:
            # Open serial port
            self.com = serial.Serial(
                port=port,
                baudrate=self.COM_BAUD,
                timeout=self.COM_TIMEOUT,
                bytesize=serial.EIGHTBITS,
                parity=serial.PARITY_NONE,
                stopbits=serial.STOPBITS_TWO,  # Try two stop bits
                rtscts=False,
                dsrdtr=False
            )
            print(f"Opened {self.com.portstr}")
            print(f"Serial port settings: {self.com.get_settings()}")

            # Set RTS for RS485
            self.com.rts = False
            print("RTS set for RS485")

            # Send initial break to reset device
            self.com.break_condition = True
            time.sleep(0.1)  # Longer initial break
            self.com.break_condition = False
            time.sleep(0.1)  # Longer initial mark
            print("Initial break sent")

        except Exception as e:
            print(f"Could not open device {port}. Error: {e}")
            raise

    def set_channel(self, channel, value, autorender=False):
        if not 1 <= channel <= self.DMX_SIZE:
            print(f'Invalid channel specified: {channel}')
            return
        # clamp value
        value = max(0, min(value, 255))
        self.dmx_frame[channel-1] = value
        print(f"Setting channel {channel} to {value}")
        if autorender:
            self.render()

    def clear(self, channel=0):
        if channel == 0:
            self.dmx_frame = [0] * self.DMX_SIZE
            print("Clearing all channels")
        else:
            self.dmx_frame[channel-1] = 0
            print(f"Clearing channel {channel}")

    def render(self):
        print("Rendering DMX frame...")
        print(f"Current frame values (channels 1-4): {self.dmx_frame[:4]}")
        
        try:
            # Send break signal
            self.com.break_condition = True
            time.sleep(self.BREAK_TIME)
            self.com.break_condition = False
            time.sleep(self.MAB_TIME)

            # Send start code (0x00)
            self.com.write(bytes([0x00]))
            time.sleep(0.0001)  # Small delay after start code
            
            # Send DMX data
            self.com.write(bytes(self.dmx_frame))
            
            # Ensure all data is sent
            self.com.flush()
            
            # Wait for inter-frame delay
            time.sleep(self.INTER_FRAME_DELAY)
            
            print("DMX frame sent successfully")
        except Exception as e:
            print(f"Error sending DMX frame: {e}")

    def close(self):
        print("Closing serial connection...")
        # Send blackout before closing
        self.clear()
        self.render()
        time.sleep(0.1)
        self.com.close()

    def run(self):
        print("Starting DMX control...")
        try:
            # Send a few initial frames to ensure device is ready
            for _ in range(3):
                self.clear()
                self.render()
                time.sleep(0.1)

            while True:
                print("\n--- Setting channels to full power ---")
                # Set channels 1-4 to full power
                for channel in range(1, 5):
                    self.set_channel(channel, 255, autorender=True)
                time.sleep(1)
                
                print("\n--- Clearing all channels ---")
                # Clear all channels
                self.clear()
                self.render()
                time.sleep(1)
        except KeyboardInterrupt:
            print("\nStopping DMX control...")
        finally:
            self.close()

def main():
    try:
        # Create DMX controller using tty version of the device
        controller = DMXController('/dev/tty.usbserial-AQ01FJYP')
        controller.run()
    except Exception as e:
        print(f"Fatal error: {e}")
    finally:
        print("Program ended")

if __name__ == "__main__":
    main()

