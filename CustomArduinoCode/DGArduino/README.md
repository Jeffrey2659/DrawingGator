# Arduino Program Usage Guide


## Uploading Code
To upload the code, open the .ino file as a project in the Arduino IDE. 
You should see the .h header files populate within the project. 
From there, you should be able to communicate directly with the device through
the Arduino IDE Serial Monitor.

## GCode Commands

- [`G0`] Greedy Move
  - Attempts to move from current position to the provided position using the greedy movement algorithm.
  - Required arguments:
    - `double X` - X of new position (in units)
    - `double Y` - Y of new position (in units)
  - Optional arguments: None
- [`G1`] Linear Move
  - Attempts to move from current position to the provided position using the linear movement algorithm.
  - Required arguments:
    - `double X` - X of new position (in units)
    - `double Y` - Y of new position (in units)
  - Optional arguments: None
- [`G2`] Arc Move
  - Attempts to move from current position to the provided position using the circular movement algorithm.
  - Required arguments:
    - `double X` - X of new position (in units)
    - `double Y` - Y of new position (in units)
    - `double I` - X of the center of rotation (in units)
    - `double J` - Y of the center of rotation (in units)
  - Optional arguments: None
- [`G6`] Direct Stepper Move
  - Rotates both motors the specified number of steps at the same time. May not function properly over 1000 steps in one instruction.
  - Required arguments: None
  - Optional arguments: 
    - `int R = 0` - Steps to move the right motor
    - `int L = 0` - Steps to move the left motor
- [`G20`] Inch Units
  - Sets units to Inches (default)
  - Required arguments: None
  - Optional arguments: None
- [`G21`] ~~Millimeter Units~~ **AVOID, NOT IMPLEMENTED**
  - Required arguments: None
  - Optional arguments: None
- [`G60`] Request State Info
  - Uses Serial USB to print out the current state variables it is keeping track of.
  - Required arguments: None
  - Optional arguments: None
- [`G90`] Absolute Positioning
  - Sets expectation of points to be absolute positions (default).
  - Required arguments: None
  - Optional arguments: None
- [`G91`] ~~Relative Positioning~~ **AVOID, NOT IMPLEMENTED**
  - Required arguments: None
  - Optional arguments: None
- [`G92`] Overwrite Position
  - Tells the device what position it is at, defining current state.
  - Required arguments:
    - `double X` - X of current position (in units)
    - `double Y` - Y of current position (in units)
    - `double I` - X of offset from left cable point 0,0 (in units)
    - `double J` - Y of offset from left cable point 0,0 (in units)
  - Optional arguments: None

-----

- [`M0`] Unconditional Halt
  - Pauses the program between steps. Can be continued with *Continue*.
  - Required arguments: None
  - Optional arguments: None
- [`M1`] ~~Conditional Halt~~ **AVOID, NOT IMPLEMENTED**
  - Required arguments: None
  - Optional arguments: None
- [`M3`] Set Servo Position
  - Required arguments:
    - `int S` - PWM to set the Servo (maps to 70 (full released) to 255 (full pressed)).
  - Optional arguments: None
- [`M108`] Continue
  - Recovers and proceeds after a *Halt* command.
  - Required arguments: None
  - Optional arguments: None
- [`M112`] Shutdown
  - Stops all operations except for communication and requires *Restart*.
  - Required arguments: None
  - Optional arguments: None
- [`M999`] Restart
  - Clears state variables before continuing operation, only works after *Shutdown*.
  - Required arguments: None
  - Optional arguments: None