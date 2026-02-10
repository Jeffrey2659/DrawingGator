# DrawingGator

## Contributors and Primary Task Division

<!-- Using HTML comments. Please correct if inaccurate or not even -->
- ***Jeffrey James*** - User Interface/PC Communication (SVG/X-Y to GCode, PC UART communication to Arduino)
- ***Peek Lesh*** - Mechanical & PCB (3d Printing, part design, PCB schematic and layout design)
- ***Sara Kola*** - User Interface (Customizability, input image to SVG, SVG to ordered X-Y paths)
- ***Ethan Pena Perez*** - Simulator & Arduino (arduino-side UART and paths to motor translation)

## Project Architecture

<!-- Correct if anything outright wrong. Chat it up if we aren't sure -->
In the simplest terms, the flow of the service is the following:

**Possible Calibration Phase**
*Arduino turns on and calibrates to area* => *Arduino indicates to PC/device it is ready* => ...

**GUI Phase**
*Desktop GUI* => *Your PNG/Image* => *Image as SVG/Lines* => *Your image customization* => *Final vector image* => ...

**Translation Phase**
*Final Vector Image Points* => *GCode generator* => *GCode sent to Arduino through UART* => ...

**Parsing/Drawing Phase**
*GCode recieved and parsed on Arduino* => *translate commands to actions* => *perform next action* => ...

**Conclusion**
*Repeat parsing/drawing phase until drawing complete*.


## Setting Up the Environment

### Programming the DrawingGator Arduino
Most of the time, the Arduino should already be properly programmed, as it shall be in our demo. However, should you need to re-upload code to the arduino, the following are the recommended instructions:

1. Clone main branch of this repository
2. Install the Arduino IDE software
3. Using the Arduino IDE software, open the `DrawingGator/CustomArduinoCode/DGArduino/DGArduino.ino` file.
4. Plug in the Arduino Mega/Uno to the computer
5. Select the Arduino Mega/Uno board and port at the top left of the screen
6. Upload the code using the arrow symbol next to the board selection dropdown
7. Wait for upload to complete

This procedure is also how you apply updates. 

*Note: If you are attempting to manually communicate*
*with the Arduino using the Arduino IDE or another USB/UART control program, please refer to*
*the `README.md` file found in the `DrawingGator/CustomArduinoCode/DGArduino/` directory.*

### Running the Desktop Application

1. Clone main branch of this repository
2. Install Python and ensure it works in the terminal
3. Enter the `DrawingGator/DG_UI/` directory in the terminal
4. Run the command `python app.py`
5. Upload image from exising folder in the opened window

## Completed Work

<!-- ADD YOUR OWN COMPLETED WORK SECTION BELOW -->
**Simulator**
- To-scale display of simple mechanical parameters
  - Spool/Rotating wheel radius
  - Width & Height
- Domain restricting (Stays only in realm of possible steps with measurable degrees)
- Path making (with replacable algorithms)
  - `GREEDY` - Only chooses best next step, no consideration for looks
  - `LINE_FOLLOW` - Tries to make best next step, equally weighting line dist and goal dist
  - `CIRCULAR` - Makes the shortest path arc around a given third point from the start to the end
- Flexible point following of any count
  - Only limited by step count (customizable count in code)
- Leg-based rather than point-based simulation
  - Allows for each line of the simulator to use a different algorithm (matches G-Code more closely)
- Now allows for more than 1 step in each motor direction (up to 2 in either direction works best thus far)

**UI**
- Rudimentary UI
  - Uses Model View Presenter Architecture:
    - Model: Handles logic of UI components and different libraries integrated into the application
    - View: This section handles the layout of the GUI components and stores any triggers from the user
     - Presenter: Communicates between View and Model, to send the triggers from view to appropraite function in Model and communicates the response that needs to be reflected in view
  - Basic UI components to load image and gcode
    - Parses and cleans G code
  - Text view box to see responses from serial port and view data being sent
    - Logging responses and errors from microntroller motion library
    - Logging G Code lines
  - Configuration boxes for serial 
    - Configure Com Port
    - Configure Baud Rate
  - Functionality to send indiviudal serial commands
      - Used Pyserial to establish serial connection and process data between devices
  - Status Bar to show G code lines sent
  - Functionality for whole file G code sending

**Arduino**
- Custom Vector implementation to store GCode instruction temporarily
- UART Parsing of GCode into key-value pairs of char and double
- Validation of GCode commands with referenced table of intended arguments
- Responses to UART with debugging information if in debug mode or simple acknowledgement of `OK` when command is fully executed
- Transferred algorithm functions and structure to Arduino code
- Arduino can calculate motor steps from the 

# Libraries used for the svg_algorithm.py
1. Pillow: Image Processing
2. numpy: for numerical arrays
3. svgwrite: generate the svg file
4. matplotlib + svgpathtools: for parsing and plotting the lines

# Run the following command:
```pip install pillow numpy svgwrite matplotlib svgpathtools PyQt6 serial serialtools lxml```

**For the case of potrace since it cannot be installed through the command line:**
1. Windows:

    Download the following zip and add it to PATH: https://potrace.sourceforge.net/download/1.16/potrace-1.16.win64.zip 
    Note: Potrace is then called using the subprocess

2. MacOS: ```brew install potrace```
3. Ubuntu: ```sudo apt install potrace```

## Known Bugs & Correction Statuses

<!-- ADD YOUR OWN BUG SECTION BELOW -->
**Simulator**
- ~~Simulator linear path gets dragged to line above drawing space~~ (Fixed)
- ~~Does not identify impossible paths prior to generating, so can fail to reach goal and cap datapoints~~ (Fixed, halts operation on point no longer making progress)
- Circular path may not generate if center is between start and goal point

**UI**
- The text in the view box from the serial port is not properly formatted (FIXED)
- The status bar for the Lines sent does not update after a new g code file is loaded in over the exsisitng one
- The svg to gcode conversion does not complete fully
- If closing svg preview and command window, no way of recalling them.

**Arduino-Assembly Movement**
- Locations seem to be skewed the closer they are to the top of the board
- Occassionally the servo will be locked in an incorrect orientation and needs to be manually moved to function correctly
- Plugging in the Arduino may cause motor steps to be sent even if no commands are sent

**Serial Communication**
- The buffer is immediately filled with data and does not wait for the `OK` responses from the microcontroller

**Simulation Output**
- In some tested files there seems to be a "pen not lifted" and it drags the line when it draws. (FIXED)
