# Firmware MacroBoard

This repository contains the firmware for the mutenix.de MacroBoard.

## Features

- 5/10 Buttons with status reports
- 5+1/13 LEDs
- Boot option selection (Enable Serial, Enable Filesystem)
- Automated Update (no FS mount necessary)

## Button Ids

Based on the hardware Version the buttons are ordered in the following way:

### V1

```
+---+
| o |   Button 1, buttons[0], GP0
| o |   Button 2, buttons[1], GP1
| o |   Button 3, buttons[2], GP2
| o |   Button 4, buttons[3], GP3
| o |   Button 5, buttons[4], GP4
|   |
+---+
```

### V2 - USB 5 Buttons

```
+---+
| o |   Button 1, buttons[0], GP11
| o |   Button 2, buttons[1], GP10
| o |   Button 3, buttons[2], GP9
| o |   Button 4, buttons[3], GP8
| o |   Button 5, buttons[4], GP7
|   |
+---+
```

### V2 - BT 5 Buttons

```
+---+
| o |   Button 1, buttons[0], P1_04
| o |   Button 2, buttons[1], P1_06
| o |   Button 3, buttons[2], P0_09
| o |   Button 4, buttons[3], P0_10
| o |   Button 5, buttons[4], P1_11
|   |
+---+
```


### V2 - USB 10 Buttons

```
                               +-----+
  Button 1, buttons[0], GP11   | o o |   Button 6, buttons[5], GP6
  Button 2, buttons[1], GP10   | o o |   Button 7, buttons[6], GP3
  Button 3, buttons[2], GP9    | o o |   Button 8, buttons[7], GP2
  Button 4, buttons[3], GP8    | o o |   Button 9, buttons[8], GP1
  Button 5, buttons[4], GP7    | o o |   Button 10, buttons[9], GP0
                               |     |
                               +-----+
```

### V2 - BT 10 Buttons

```
                               +-----+
  Button 1, buttons[0], P1_04  | o o |   Button 6, buttons[5], P1_13
  Button 2, buttons[1], P1_06  | o o |   Button 7, buttons[6], P1_15
  Button 3, buttons[2], P0_09  | o o |   Button 8, buttons[7], P0_02
  Button 4, buttons[3], P0_10  | o o |   Button 9, buttons[8], P0_29
  Button 5, buttons[4], P1_11  | o o |   Button 10, buttons[9], P0_31
                               |     |
                               +-----+
```