[日本語](./README_ja.md)

# Sample MOD

This is a collection of sample Stack-chan user applications (MODs).  
See [Building and Writing Programs](../docs/flashing-firmware.md) for instructions on how to write mods. 

As described in the section on building and writing programs, when writing mods, the port may not be found, and the message "/bin/sh: 1: [[ not found" may be displayed and writing may not be possible. At that time, specify the port before npm.
The following is an example of writing mods/cherrup_ble_lite for windows (WLS2).

```console
$ UPLOAD_PORT=/dev/ttyACM0 npm run mod --target=esp32/m5stack_cores3 ./mods/cheerup_ble_lite/manifest.json
```

Some MODs require a network connection or an external server to run.


## Look Around: Kyoro-kyoro gaze Stack-chan(windows/Ubuntu/mac)

![squeaking Stack-chan](../docs/images/stackchan.gif)  
- This is the same action that is in the A button during preferences.
- When buling the host, you do not need to set up Wi-Fi.
    - $ npm run build --target=esp32/m5stack_cores3
- Write the host program.
    - $ npm run deploy --target=esp32/m5stack_cores3
- Writing mod.
    - $ npm run mod --target=esp32/m5stack_cores3. /mods/look_around/manifest.json
- When the Stack-chan face appears, press the A button and it should move.
- [look_around](./look_around/)

## Monologue: Posho-posho soliloquy stackchan(Ubuntu/mac)
- Windows is not eligible because the Wi-Fi bridge does not work properly.
- Use TTS(synthesized speech) to playback audio; for more information on using TTS, please refer to [here](../docs/text-to-speech.md).
- The operation presented in this section, show how to install the method pre-generated using VoiceVox.
- Clone the TTS engine VoiceVox.
    - $ git clone https://github.com/VOICEVOX/voicevox_engine.git
- Start it using docker; see https://docs.docker.com/engine/install/ubuntu/ for docker installaton.
    - $ sudo chmod 777 /var/run/docker.sock
    - $ docker pull voicevox/voicevox_engine:cpu-ubuntu20.04-0.21.1
    - $ docker run --rm -p 50021:50021 voicevox/voicevox_engine:cpu-ubuntu20.04-0.21.1
- Set up the TTS environment.
    - Correct the IP address of the TTS host of the PC from which docker was started in stack-chan/firmware/statckchan/manifest_local.json.
- Write the sentence to be spoken in the JavaScript file. The speech will be random.
    - JavaScripts file : stack-chan/firmware/mods/monologue/speeches_monologue.js
- Wi-Fi setup is required when building the host; Wi-Fi connection should be 2.4G.
    - $ npm run build --target=esp32/m5stack_cores3 ssid="SSID name" password="SSID password"
- Write the host program.
    - $ npm run deploy --target=esp32/m5stack_cores3
- Writing mod
    - $ npm run mod --target=esp32/m5stack_cores3 ./mods/monologue/manifest.json .
- When the stack chan face appears, press the A button to run.
- [monologue](./monologue/)

## Cheerup: Stack-chan cheerleaders!(windows/Ubuntu/mac)

![face-sync](../docs/images/face-sync.gif)
![Stack-chan Cheerup](../docs/images/cheerup.gif)  
- Connect the PC and Stack-chan One-to-one using BLE.
- A webcam is required on the PC.
- There are still glitches and it cannot support voice support or facial expression changes. Only providing tracking is support.
- The web socket version has not been tested.
- Setting Stack-chan
    - Do not configure Wi-Fi when building the host.
        - $ npm run build --target=esp32/m5stack_cores3
    - Write the program for the host.
        - $ npm run deploy --target=esp32/m5stack_cores3
    - Writing mod
        - $ npm run mod --target=esp32/m5stack_cores3 ./mods/cheerup_ble_lite/manifest.json
- Setting preferences on the PC side.
    - Due to security issues, the only supported browser is Chrome.
    - If you are using windows, you need to install node 18.12 or higher.
        - $ volta install node@18
    - You need to enable the flag for Experimental Web Platform features for Bluetooth access from the browser.
        - Enter chrome://flags in the chrome URL to enable Experimental Web Platform features from stop.
    - Clone the following https://github.com/meganetaaan/suburi-mediapipe.
        - $ git clone https://github.com/meganetaaan/suburi-mediapipe
    - Install the necessary tools.
        - $ sudo apt install -y curl
        - $ curl -sS https://dl.yarnpkg.com/debian/pubkey.gpg | sudo apt-key add -
        - echo "deb https://dl.yarnpkg.com/debian stable main" | sudo tee /etc/apt/sources.list.d/yarn.list
        - Installing yarn tools
            - ubuntu : $ sudo apt update && sudo apt install yarn(if volta is not included)
            - ubuntu : $ sudp apt update && volta install yarn and yarn install(if volta is included)
            - macOS : $ brew install yarn
            - Windows : $ volta install yarn and yarn install
        - $ npm install react react-dom
    - Install google-chrome(in case Chrome does not recognize wls from windows)
        - $ sudo apt update
        - $ sudo sh -c 'echo "deb http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google-chrome.list'
        - $ sudo wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | sudo apt-key add -
        - $ sudo apt install google-chrome-stable
    - The flollowing commands are required for compatibility between the openssl version and the node version.
        - The following command is required every time you open the terminal so you will need to type it each time or add it to your bashrc.
            - $ export NODE_OPTIONS=--openssl-legacy-provider
    - If you get an error that node_module does not have write permission, and write permission to cache.
        - $ sudo chmod 777 /home/ubuntu/suburi-mediapipe/frontend/node_modules/.cache
    - The tool can be started by "docker compose up",but the procedure is the same for each OS.
        - Install node_modules in fronted and backend.
			- $ cd /home/ubuntu/suburi-mediapipe/backend
			- $ npm install react-scripts
			- $ cd /home/ubuntu/suburi-mediapipe/frontend
			- $ npm install react-scripts
        - Two types of terminals are activated: frontend and backend.
        - First terminal
			- $ cd /home/ubuntu/suburi-mediapipe/backend
			- $ yarn start(sudo is required for windows)
        - Second termninal
			- $ cd /home/ubuntu/suburi-mediapipe/frontend
			- $ yarn start(sudo is required for windows)
    - If Chrome does not start automatically, enter in the URL the following: http://localhost:3000/sandboxes/stackchan/facesync
    - When Chrome displays the Stack-chan, change the Connection Method at the bottom from WebSocket to bluetooth and click connect.
    - http://localhost:3000 will ask you to set up a pair; selct stk and pair.
- [cheerup_ble_lite](./cheerup_ble_lite/): BLE version
- [cheerup_ws](./cheerup_ws/): WebSocket version

## Mimic: Manekko mimicing stack chan.  
- You will require 2 Stack-chan units.  
![manekko_stackchan](../docs/images/mimic.gif)  
- [mimic_main](./mimic_main/): the one the user runs  
- [mimic_follow](./mimic_follow/): The one that mimics the user.  

## Face Tracker: Stack-chan that tracks faces.(Windows/Ubuntu/mac)
- You will require Stack-chan and [M5Stack_UnitV2](https://docs.m5stack.com/en/unit/unitv2).
- Setting UnitV2
    - Install the UnitV2 driver; It is not needed to install Ubuntu
        - https://docs.m5stack.com/ja/guide/ai_camera/unitv2/base_functions
    - Setting Wi-Fi.
        - Connect UnitV2 to a PC via USB and login to UnitV2 from a terminal.
            - $ ssh m5stack@10.254.239.1
            - Password is 12345678
        - Convert the password for the SSID to be used into a passphrase and write it in /etc/wpa_supplicant.conf .
        - Command to convert SSID password to passphrase.
            - $ sudo wpa_passphrase Wi-Fi SSID Wi-Fi password
        - Open wpa_supplicant.conf with root privileges and write the passphrase and SSID you generated earlier.
			```console
			network={
				ssid=”Wi-Fi SSID”
				psk=passphrase
			}
			```
    - Open Chrome, and insert the following URL http://10254.239.1
    - Select Face Detector to output face data.
- Setting Stack-chan
    - When building the host, you will need to set up Wi-Fi; Wi-Fi should be connected to 2.4G.
        - $ npm run build --target=esp32/m5stack_cores3 ssid="SSID name" password="SSID password"
    - Write the host program.
        - $ npm run deploy --target=esp32/m5stack_cores3
    - Writing mod
        - $ npm run mod --target=esp32/m5stack_cores3 ./mods/face_tracker/manifest.json
![face tracker stack chan](../docs/images/face-tracker.gif)
- [face_tracker](./face_tracker/)

## Face: Stack-chan facial expression and complexion(Windows/Ubuntu/mac)
- Changees facial expression and complexion in turn.
- How to install the mod
    - You do not need to set up Wi-Fi when building the host.
        - $ npm run build --target=esp32/m5stack_cores3
    - Write the host program.
        - $ npm run deploy --target=esp32/m5stack_cores3
    - Writing mod
        - $npm run mod --target=esp32/m5stack_cores3 ./mods/face/manifest.json

## Chatty stack-chan(Ubuntu)
- ChatGPT is used to talk to the stack properly.
- MacOS is out of scope.
- Windows is not covered because the Wi-Fi bridge does not work properly.
- A paid plan is required to run ChatGPT from the app.
- The node version required by the simple-stt-server is 20 instead of 16.
- Long sentences are not possible, due to not using PSRAM. 
- Configuration on the -PC side
    - Windows requires installation of “pulseaudo” on windows side for the following voice recognition.
        - Installation on Windows 11 side
            - Download and install Pulse Audio On Windows.
                - Click on https://www.freedesktop.org/wiki/Software/PulseAudio/Ports/Windows/Support/ and download the zipfile containing preview binaries.
                - Extract the file to C:\Users\username\pulseaudio-1.1
                - Edit C:\Users\username\pulseaudio-1.1\etc\pulse\default.pa
                    - #Uncomment load-module module-native-protocol-tcp and load-module module-esound-protocol-tcp and add ip address
                        - load-module module-esound-protocol-tcp auth-ip-acl=127.0.0.1;172.16.0.0/12
                        - load-module module-native-protocol-tcp auth-ip-acl=127.0.0.1;172.16.0.0/12
                - Edit C:\UserName\pulseaudio-1.1\etc\pulse\daemon.conf
                    - Remove the semicolon and change the number from 20 to -1.
                        - exit-idle-time = -1
        - Start Pulse Audio
            - Double-click on C:\User\username\puseaudio-1.1\bin\pulseaudio.exe to start it. It will exit immediately the first time. Double-click again to start it. There is an error, but if it does not exit, leave it alone.
            - You will need to start pulseaduio.exe every time you start Windows.
    - Installation on WSL side
        - Install the necessary libraries.
            - $ sudo apt install alsa-utils
            - $ sudo apt install libpulse0
            - $ sudo apt install -y pulseaudio
        - Set up the WebSocket server environment
            - $ git clone https://github.com/meganetaaan/simple-stt-server.git
            - $ cd simple-stt-server
            - Set the node version to 16, it cannot be installed if node is newer. 
                - $ volta install node@16
                - $ npm install
        - Download the VOSK model, create a model folder under simple-stt-server, and copy the downloaded data with the expanded data.
            - Data to download: https://alphacephei.com/vosk/models/vosk-model-ja-0.22.zip
            - To access the simple-stt-server folder from windows, you can access the Linux folder on the left side of Explorer: Linux/Ubuntu-22.04/home/ubuntu/simple-sst-server
        - Set the PULSE_SERVER environment variable. Add the following two lines to the end of ~/.bashrc
            - export HOST_IP="$(ip route |awk ‘/^default/{print $3}’)”
            - export PULSE_SERVER="tcp:$HOST_IP”
    - Ubuntu
        - Install the following required libraries.
            - sudo apt install alsa-utils
            - sudo apt install alsa-tools
        - Prepare WebSocket server environment
            - $ git clone https://github.com/meganetaaan/simple-stt-server.git
            - $ cd simple-stt-server
            - $ npm install
        - Download the VOSK model, create a model folder under simple-stt-server, and copy the downloaded data with the expanded data.
            - Download data https://alphacephei.com/vosk/models/vosk-model-ja-0.22.zip
    - For the rest of this section will be common to WSL and Ubuntu.
        - Activation of voice recognition.
            - Execute the following command at simple-stt-server. 
                - $ npm start -- --device default
        - Clone voicevox_engine, a text-to-speech server that converts the text of the reply from ChatGPT into the speech of the stack chan.
            - $ git clone https://github.com/VOICEVOX/voicevox_engine.git
        - Start using docker; see https://docs.docker.com/engine/install/ubuntu/ for docker installation. 
            - $ sudo chmod 777 /var/run/docker.sock
            - $ docker pull voicevox/voicevox_engine:cpu-ubuntu20.04-0.21.1
            - $ docker run --rm -p 50021:50021 voicevox/voicevox_engine:cpu-ubuntu20.04-0.21.1
- Stack-chan side setting
    - Add or change necessary settings in manifest_local.json (stack-chan/firmware/stackchan/manifest_local.json) config.
        - ChatGPT tokens : ChatGPT tokens you have obtained
        - IP address : IP address assigned to your PC
			```console
			{
    			"include": [
        			"./manifest.json"
    			],
    			"config": {
        			"ai": {
            		"token": "ChatGPT tokens"
        			},
        			"tts": {
            			"type": "voicevox",
            			"host": "IP address",
           	 			"port": 50021
        			}
    			}
			}
			```	
    - Change to the ChatGPT model used for Stack-chan as defined in stack-chan/firmware/mods/chatgpt/mod.js. Here, we will use gpt-40.
		```console
			const STT_HOST = 'stackchan-base.local'
			// const MODEL = 'gpt-4'
			// const MODEL = 'gpt-3.5-turbo'
			const MODEL = 'gpt-4o'
		```
    - When building the host, you will need to set up Wi-Fi; Wi-Fi should be connected to 2.4G.
        - $ npm run build --target=esp32/m5stack_cores3 ssid=“SSID name” password="SSID password”
    - Write the host program.
        - $ npm run deploy --target=esp32/m5stack_cores3
    - Writing mod
        - $ npm run mod --target=esp32/m5stack_cores3 . /mods/chatgpt/manifest.json


