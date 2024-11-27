# Firmware MacroBoard

This repository contains the firmware for the m42e.de MacroBoard.

## Features

- 5 Buttons with status reports
- 5 LEDs (and 1 extra which is not controllable by the host program)
- Boot option selection (Enable Serial, Enable Filesystem)

## Button Ids

The buttons are ordered in the following way:

```
+---+
| o |   Button 1, buttons[0]
| o |   Button 2, buttons[1]
| o |   Button 3, buttons[2]
| o |   Button 4, buttons[3]
| o |   Button 5, buttons[4]
|   |
+---+
```


