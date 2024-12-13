# Stack-chan RT ver.

[![Build Stack-chan Firmware](https://github.com/meganetaaan/stack-chan/actions/workflows/build.yml/badge.svg)](https://github.com/meganetaaan/stack-chan/actions/workflows/build.yml)
[![Discord server invitation](https://dcbadge.vercel.app/api/server/eGhd9adnBm)](https://discord.gg/eGhd9adnBm)

[日本語](./README_ja.md)

![stackchan](./docs/images/stack-chan_main_2400x2400_350dpi_rgb.jpg)

This is the repository for Stack-chan RT ver.

* Official hashtag: [`#stackchan` | `#ｽﾀｯｸﾁｬﾝ` (JP)](https://twitter.com/search?q=%23stackchan%20OR%20%23%EF%BD%BD%EF%BE%80%EF%BD%AF%EF%BD%B8%EF%BE%81%EF%BD%AC%EF%BE%9D).


Stack-chan is a super cute, palm-sized communication robot developed and released in JavaScript by [Shinya Ishikawa](https://twitter.com/stack_chan).
* Project page: https://github.com/stack-chan/stack-chan
* Video (with English subtitles): https://youtu.be/fZb_mF08xV0

<br>

The RT version introduces the following updates:

* The dependent Moddable SDK version is now fixed at [4.9.5](https://github.com/Moddable-OpenSource/moddable/releases/tag/4.9.5).
* Several updates have been made to the circuit diagram and board design.
* The DYNAMIXEL XL330-M288-T servo motor has been integrated.
* The robot's exterior casing is produced using injection molding.

## Features

* :neutral_face:     Show cute face
* :smile:            Expression(Happy, Angry, Sad etc.)
* :smiley_cat:       Customize face
* :eyes:             Glance/stare/gaze
* :speech_balloon:   Say things
* :bulb:             Addon M5Units
* :cyclone:          Drive Serial(TTL)/PWM servos
* :game_die:         Make applications on your own

## Contents

This repository includes the following contents.

* __firmware__ : Source codes of the firmware.

## Installation

### Assemble board

* See [Stack-chan RT ver. Assembly Manual](docs/assembly.md)

### Flash firmware to M5Stack

* For Windows:  [(WSL2) Windows 11 Stack-chan Environment Setup Manual (Japanese)](firmware/docs/getting-started-wsl2_ja.md)
* For MacOS/Linux: [Getting Started (MacOS/Linux)](./firmware/docs/getting-started.md)

## Contribution

We accept __feature requests / bug reports__ through the [issues](https://github.com/rt-net/stack-chan/issues) page.

## License

Resources of this repository are distributed under Apache version 2.0 license.
See [LICENSE](./LICENSE).
