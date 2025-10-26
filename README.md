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
- Flexible point following of any count
  - Only limited by step count (customizable count in code)

## Known Bugs & Correction Statuses

<!-- ADD YOUR OWN BUG SECTION BELOW -->
**Simulator**
- ~~Simulator linear path gets dragged to line above drawing space~~ (Fixed)
- Does not identify impossible paths prior to generating, so can fail to reach goal and cap datapoints