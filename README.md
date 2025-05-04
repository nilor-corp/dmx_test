# DMX Control for Enttec Open DMX USB

A Python-based DMX controller for the Enttec Open DMX USB device. This program allows you to control DMX channels through a simple Python interface.

## Requirements

- Python 3.x
- pyserial package
- Enttec Open DMX USB device
- DMX-compatible lighting fixtures

## Installation

1. Create a virtual environment (recommended):

```bash
python -m venv venv
source venv/bin/activate  # On macOS/Linux
```

2. Install required packages:

```bash
pip install pyserial
```

## Device Setup

1. Connect your Enttec Open DMX USB device
2. Find the device port:

```bash
ls /dev/cu.usbserial*  # On macOS
ls /dev/ttyUSB*        # On Linux
```

## Usage

Run the DMX controller:

```bash
python test_dmx.py
```

The program will:

1. Initialize the DMX device
2. Alternate between full power (255) and off (0) for channels 1-4 every second
3. Press Ctrl+C to stop the program

## Technical Details

- Baud Rate: 250000
- Stop Bits: 2
- Break Time: 100 microseconds
- Mark After Break: 100 microseconds
- Inter-frame Delay: 30 milliseconds

## DMX Protocol

The program implements the standard DMX512 protocol:

1. Break signal (100μs)
2. Mark After Break (100μs)
3. Start code (0x00)
4. DMX data (512 channels)
5. Inter-frame delay (30ms)

## Troubleshooting

If the device is not working:

1. Check the device port is correct
2. Verify the device is properly connected
3. Try different baud rates (250000, 115200, 57600)
4. Check device permissions:

```bash
sudo chmod 666 /dev/tty.usbserial-AQ01FJYP
```

## License

This project is open source and available under the MIT License.
