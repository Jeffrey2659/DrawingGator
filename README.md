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
- Responses to UART with debugging information
- Transferred algorithm functions and structure to Arduino code

# Libraries used for the svg_algorithm.py
1. Pillow: Image Processing
2. numpy: for numerical arrays
3. svgwrite: generate the svg file
4. matplotlib + svgpathtools: for parsing and plotting the lines

# Run the following command:
```pip install pillow numpy svgwrite matplotlib svgpathtools```

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
- The text in the view box from the serial port is not properly formatted
- The status bar for the Lines sent does not update after a new g code file is loaded in over the exsisitng one
- The svg to gcode conversion does not complete fully

**Serial Communication**
- The buffer is immediately filled with data and does not wait for the "okay" responses from the microcontroller

**Simulation Output**
- In some tested files there seems to be a "pen not lifted" and it drags the line when it draws. 
