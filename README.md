# circuitpy-compass
This project turns an Adafruit TFT Gizmo into a connected compass for Microsoft Flight Simulator.

## Installation

There are two modules to install. First, you need a TFT Gizmo configured to use CircuitPython and connected to an appropriate controller. The tested configuration is with a Circuit Playground Bluefruit. See https://learn.adafruit.com/adafruit-tft-gizmo. The code.py, boot.py and font file should be copied to CIRCUITPY to install the compass module.

In order to communicate with MSFS, you need to run a daemon in the background that reads information from MSFS in real time and communicates that information to the compass over a serial (COM) port. The code for the agent is provided in the CircuitpyCompassAgent folder. Inside that folder is a Visual Studio 2019 project with the code for the agent.

## Building the Agent

The agent requires the MSFS SDK to compile and link to the API libraries for MSFS. To install the SDK, see https://forums.flightsimulator.com/t/how-to-getting-started-with-the-sdk-dev-mode/123241

To build the agent:

- Load the solution into MSVS
- Go to Property Manager -> Add Existing Property Sheet -> Navigate to $(MSFS SDK install location)/SimConnectSDK/VS/SimConnectClient.props
- Change the architecture to `x64` from `x86`
- Build the agent (F5)
- Check for errors

The MSFS SDK install location is usually `C:\MSFS SFK`

## Running the Agent

The agent needs to know what COM port your compass is connected to. The easiest way to find out is to have the Device Manager open when you connect the USB of your TFT Gizmo, and see what COM ports show up. There will be 2 ports: the REPL will be first, and the data channel will be second. We want to use the second port. By default, COM9 is configured. If you have COM8 and COM9 showing you're good-to-go. Otherwise, edit CircuitpyCompassAgent.cpp#L10

# Running it all

To get it all working:

- Start MSFS and wait for it to get to the main menu
- Start the agent by running it from MSVS, or running a compiled executable
- Plug in your TFT Gizmo
- Start a flight

Your compass should reflect your simulated heading in the simulator and update (albeit slowly)