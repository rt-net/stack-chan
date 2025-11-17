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

## Abaou this repository
This repository include programs for Stack-chan RT ver. implemented in UIFlow2.

UIFlow2 is a GUI-based programing environment officially supported by M5Stack.

## Features
With this implementatio, following features supported.

+ **Variaous faces**
    * Normal(with blinking), Smiling, Anger,  Sad, Winking,  Rotation and moving, and Custmizables.
    
    ![Stack-chan-faces](uiflow2/html/images/face.png)

+ **Serual motor control**
    * Dynamixel or SG90 compatilble motor support
+ **Text to speech**
    * Google Text-to-speech API supported
+ **Speech recognition**
    * Google Speech-to-text API supported
+ **Web serivce**
    * Original web service implementation with customizable REST API supported
+ **Image capture**
    * Camera image capture via Web service

## Installation

### Assemble board
* See [Stack-chan RT ver. Assembly Manual](docs/assembly.md)


### Flash firmware to M5Stack
Install the UIFlow2 firmware provided on the official website.
- [Instaration the firmware for Core3](https://docs.m5stack.com/ja/uiflow2/m5cores3/program)

### Upload files
#### Upload programs
Upload the Python programs(except main.py) placed under 'uiflow2/scripts' to '/flush/libs' on Core3.
Similarly, upload 'scripts/main.py' under the directory '/flash'.

#### Customize configurtion files
The following three configuration files required.
The default configuration files is in the directory 'uiflow2/conf/', so please modify to suit your envisonments.

- stackchan.json
- wlan.json
- apikey.txt

###### stackchan.json
This file configuration for type of motor, servie settings for  text-to-speech and speech recognition.

The default configyrations for RT ver. is in the uiflow2/conf/stackchan.json.

- **motor**: "Dynamixel" or "SG90"
- **tts**: "google"
- **asr**: "google"

###### wlan.json
This fiile can contein settings for three Wi-fi connections: Home, Work and Mobile connections.
When the this program starts, it will scan for access points and automatically connect.

```
{
    "Home": {"essid": "", "passwd": ""},
    "Work": {"essid": "", "passwd": ""},
    "Mobile": {"essid": "", "passwd": ""}
}
```
###### apikey.txt
This file contains the API keys for GoogleCloud Service: Speech API and Gemini API.
Enter the API key of speech API in *OPENHRI_KEY*, and that of the Gemini serives in *GEMINI_KEY*.

```
OPENHRI_KEY=
GEMINI_KEY=
```

##### Upload configuration files
Upload these three configuration files:stackchan.json, wlan.json, apikey.txt to the SD-card (/sd).

#### Upload HTML files
This package support for Web service including REST-API functions.
The default contents are in '/uilflow2/html', please upload all files under the SD-card as '/sd/html'.


We accept __feature requests / bug reports__ through the [issues](https://github.com/rt-net/stack-chan/issues) page.

## License

Resources of this repository are distributed under Apache version 2.0 license.
See [LICENSE](./LICENSE).
