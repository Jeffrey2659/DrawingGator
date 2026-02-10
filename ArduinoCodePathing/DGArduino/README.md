# Arduino Program Usage Guide


## Uploading Code
To upload the code, open the .ino file as a project in the Arduino IDE. 
You should see the .h header files populate within the project. 
From there, you should be able to communicate directly with the device through
the Arduino IDE Serial Monitor.

## Wiring Guide
There are 6 pins that must be connected. All digital pins `D#` may also be read as just the pin number `#`. 
- `GND` - Ground of the arduino to ground of the circuit
- `D3` - Servo PWM data pin
- `D6` - Left motor direction pin
- `D7` - Left motor step pin
- `D8` - Right motor direction pin
- `D9` - Right motor step pin

Currently power is provided through the USB cable and the PC. This may change later on, but means that we are guaranteed to be connected to the device and can be powered independently.

## Important State Information
The device only stores up to two legs of information: the one it is currently executing and the one that it is executing next. I have not fully documented the errors present, but you can run into this quite easily if you halt or stop the program and attempt to send 2 instructions that generate legs (G0-G2).

## Calling a Command
Once the program is running on the device, you send a command over UART on the USB using 8 data bits, no parity, 1 start bit, and 1 stop bit. 

*Example hold down pen:* `M3 S250`   
*Example raise pen:* `M3 S0` (parsed as `S70`)    
*Example shutdown:* `M112`    
*Example restart:* `M999`

*Example Set Position interaction (- characters should be omitted when sending):* 

```diff
====================
- From PC
+ From Arduino
=== Comments
====================

=== Program Start
=== Initial prints, just indicating Restart and Idle states
+ Now in state 4
+ Now in state 2

=== Accessing current state information
- G60
+ >> G60
+ Printing State:
+ curPos: (X=0.00, Y=0.00)
+ curOffset: (X=0.00, Y=0.00)
+ curPWM: 70, changedPWM: 0, changedMove: 0, toHalt: 0
+ (lMove,rMove): (X=0.00, Y=0.00)
+ unitState: 0, penState: 1, moveState: 2
+ End of States 

=== Showing arg error message
- G92 X5
+ >> G92 X14
+ Missing arg: Y

=== Setting the current position is 
- G92 X5 Y5 I6 J6
+ >> G92 X5 Y5 I6 J6
- G60
+ Printing State:
+ curPos: (X=5.00, Y=5.00)
+ curOffset: (X=1.00, Y=1.00)
+ curPWM: 70, changedPWM: 0, changedMove: 0, toHalt: 0
+ (lMove,rMove): (X=0.00, Y=0.00)
+ unitState: 0, penState: 1, moveState: 2
+ End of States
```

## GCode Command List

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
    - `double I` - X of offset from left cable point to current position (in units)
    - `double J` - Y of offset from left cable point to current position (in units)
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