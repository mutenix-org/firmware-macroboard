# Firmware MacroBoard

This repository contains the firmware for the mutenix.de MacroBoard.

## Features

- 5/10 Buttons with status reports
- 5+1/13 LEDs
- Boot option selection (Enable Serial, Enable Filesystem)
- Automated Update (no FS mount necessary)

## Supported Hardware

Currently the following boards are supported:

- [RPi2040-Zero](https://www.waveshare.com/wiki/RP2040-Zero)
- [ProMicro NRF52840 aka Supermini NRF52840 aka Nice!Nano](https://nicekeyboards.com/docs/nice-nano/)

## CircuitPython

The firmware is based on CircuitPython, to install Circuitpython use the file provided in base_software.

Use the following files per board:

- **ProMicro NRF52840** `base_software/adafruit-circuitpython-promicro-nrf52840-minimal-en_US-9.1.4.uf2` [here](base_software/adafruit-circuitpython-promicro-nrf52840-minimal-en_US-9.1.4.uf2)
- **RPi2040-Zero** `base_software/adafruit-circuitpython-waveshare_rp2040_zero-en_US-9.1.4.uf2` [here](base_software/adafruit-circuitpython-waveshare_rp2040_zero-en_US-9.1.4.uf2)

## Updating firmware of first samples (without automatic update support)

See [Updating first samples](docs/updating-old.md)

## Buttons and LEDs

Depending on the hardware version the buttons and LEDs are ordered in the following way:
The logical id of the LED corresponds to the buttons id. other ids are not controllable from host.

- `o` is a button
- `L` is LED

LEDs are expected to be GRB, except otherwise noted.

### V0.1

```
+-----+
| o L |   Button/LED 1, buttons[0], GP0, LED in Chain 5
| o L |   Button/LED 2, buttons[1], GP1, LED in Chain 4
| o L |   Button/LED 3, buttons[2], GP2, LED in Chain 3
| o L |   Button/LED 4, buttons[3], GP3, LED in Chain 2
| o L |   Button/LED 5, buttons[4], GP4, LED in Chain 1
|L    |   LED 0
+-----+

LED Pin GP7

```

**NB**: LEDs are expected to be GRBW

### V1.0 - USB 5 Buttons

```
+-------+
| L L L |   LED in Chain 5, 6, 7
| L o L |   Button/LED 1, buttons[0], GP11, LED in Chain 4, 8
| L o L |   Button/LED 2, buttons[1], GP10, LED in Chain 3, 9
| L o L |   Button/LED 3, buttons[2], GP9, LED in Chain 2, 10
| L o L |   Button/LED 4, buttons[3], GP8, LED in Chain 1, 11
| L o L |   Button/LED 5, buttons[4], GP7, LED in Chain 0, 12
|       |
+-------+
LED Pin GP15
```

### V1.0 - BT 5 Buttons

```
+-------+
| L L L |   LED in Chain 5, 6, 7
| L o L |   Button 1, buttons[0], P1_04, LED in Chain 4, 8
| L o L |   Button 2, buttons[1], P1_06, LED in Chain 3, 9
| L o L |   Button 3, buttons[2], P0_09, LED in Chain 2, 10
| L o L |   Button 4, buttons[3], P0_10, LED in Chain 1, 11
| L o L |   Button 5, buttons[4], P1_11, LED in Chain 0, 12
|       |
+-------+

LED Pin P0_20
```


### V1.0 - USB 10 Buttons

```
                                     +-------+
  LED in Chain (LiC) 5,6,7           | L L L |
  Button 1, buttons[0], GP11, LiC 4  | L o L |   Button 6, buttons[5], GP6,  LiC 8
  Button 2, buttons[1], GP10, LiC 3  | L o L |   Button 7, buttons[6], GP3,  LiC 9
  Button 3, buttons[2], GP9,  LiC 2  | L o L |   Button 8, buttons[7], GP2,  LiC 10
  Button 4, buttons[3], GP8,  LiC 1  | L o L |   Button 9, buttons[8], GP1,  LiC 11
  Button 5, buttons[4], GP7,  LiC 0  | L o L |   Button 10, buttons[9], GP0, LiC 12
                                     |       |
                                     +-------+
LED Pin  GP15
```

### V1.0 - BT 10 Buttons

```
                                      +-------+
  LED in Chain (LiC) 5,6,7            | L L L |
  Button 1, buttons[0], P1_04, LiC 4  | L o L |   Button 6, buttons[5], P1_13, LiC 8
  Button 2, buttons[1], P1_06, LiC 3  | L o L |   Button 7, buttons[6], P1_15, LiC 9
  Button 3, buttons[2], P0_09, LiC 2  | L o L |   Button 8, buttons[7], P0_02, LiC 10
  Button 4, buttons[3], P0_10, LiC 1  | L o L |   Button 9, buttons[8], P0_29, LiC 11
  Button 5, buttons[4], P1_11, LiC 0  | L o L |   Button 10, buttons[9], P0_31, LiC 12
                                      |       |
                                      +-------+
LED Pin P0_20
```

## Links

- [Host Software](https://github.com/mutenix-org/software-host)
- [MacroBoard Hardware](https://github.com/mutenix-org/hardware-macroboard)


## Create a release

- Update `pyproject.toml`
- run the script `scripts/prepare_release.sh`
- push the tag to github

## License

All files are licensed under MIT.

The library included in the lib directories may contain their own license.
