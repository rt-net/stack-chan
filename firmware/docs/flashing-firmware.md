## Build and flash firmware

[日本語](./flashing-firmware_ja.md)

## Firmware architecture

### Host and MOD

![firmware architecture](./images/host-and-mod.jpg)

Stack-chan's firmware consists of a program that provide the basic operation of Stack-chan (host), and a user application (mod).
Once the host is written, the mod can be installed in a short time for fast development.
First write the host, and then write the mods as needed.

### Manifest File

The host and the MOD each consist of a manifest file (manifest.json), source code for JavaScript modules, and resources such as images and audio. The manifest file includes the names and locations of the JavaScript modules (`modules`) , as well as the configurations that can be referenced within the modules (`config`). Additionally, the manifest file can include other manifest files (`include`).

For all configuration items, please refer to the [Moddable official documentation](https://github.com/Moddable-OpenSource/moddable/blob/public/documentation/tools/manifest.md).

## Configuration

StackChan can change settings such as motor types and pin assignments from the manifest file. You can modify [`stack-chan/firmware/stackchan/manifest_local.json`](../stackchan/manifest_local.json) for local settings. The following settings can be written under the `"config"` key.

| Key               | Description                                                                | Available values                     |
| ----------------- | -------------------------------------------------------------------------- | ------------------------------------ |
| driver.type       | Type of motor driver                                                       | "dynamixel"    |
| driver.panId      | ID of the serial servo used for pan axis (horizontal rotation of the neck) | 1~254                                |
| driver.tiltId     | ID of the serial servo used for tilt axis (vertical rotation of the neck)  | 1~254                                |
| tts.type          | [TTS](./text-to-speech.md) type                                            | "local", "voicevox"                  |
| tts.host          | Host name when TTS communicates with server                                | "localhost", "ttsserver.local", etc. |
| tts.port          | Port number when TTS communicates with server                              | 1~65535                              |

Additionally, you can specify the paths of other manifest files in a list format under the `"include"` key.

## Writing the base program (hosts)

As stated above, Stack-chan's firmware comprises a base program (host) and a user application (MOD).  

**The handling of PSRAM connected to esp32 has changed from esp-idf version 5.x. The default settings do not work smoothly, so we changed some of them.**
**When [setting the PSRAM environment variables](./getting-started.md#set-up-manual), `CONFIG_SPIRAM=y` in `~/.local/share/moddable/build/devices/esp32/targets/m5stack_cores3/sdkconfig/sdkconfig.defaults` is rewritten to `CONFIG_SPIRAM=n`.**

The following commands are used to build and write a host.

_No `sudo` required for the command._

```console
$ npm run build --target=esp32/m5stack_cores3
$ npm run deploy --target=esp32/m5stack_cores3
```

In the case of Ubuntu, the write port is now ReadOnly. If you want to rewrite the mode with sudo chmod 666 /dev/ttyACM0 but permanently change the usage permissions of the USB port, run the following command to restart your PC:
```console
$sudo usermod -aG dialout $USER
```

The program will be saved under the `$MODDABLE/build/` directory.

If you can write correctly, the face of the stack-chan will be displayed a few seconds after startup. When you press the button on the M5Stack, it changes to the following:  
- **A Button** (in the case of CoreS3, the bottom-left area of the screen) ... Stack-chan will look in a random direction every 5 seconds.
- **B Button** (in the case of CoreS3, the bottom-center area of the screen) ... Stack-chan will look left, right, down, and up.
- **C Button** (in the case of CoreS3, the bottom-right area of the screen) ... The color of Stack-chan's face will invert. 

If you write a mod, you will not be able to perform the above operation. To return to the initial state, you need to erase the contents of Flash and write it with deploy.
```console
$ ~/.espressif/python_env/idf5.3_py3.12_env/bin/esptool.py erase_flash
$ cd ~/stack-chan/firmware
$ npm run deploy --target=esp32/m5stack_cores3
```

## Debugging

You can debug the program using the following commands:

```
$ npm run debug --target=esp32/m5stack_cores3
```

These commands will open Moddable's debugger `xsbug` and connect it to the M5Stack.

![xsbug](./images/xsbug.png)

Using `xsbug`, you can check logs, set breakpoints (temporarily pause the program at specific lines), and perform step-by-step execution.
For detailed instructions on how to use `xsbug`, please refer to the [official documentation](https://github.com/Moddable-OpenSource/moddable/blob/public/documentation/xs/xsbug.md).

## Writing user application (mods)

The following command is used to build and write a mod.

_No `sudo` required for the command._  
When the writing is completed, the message "COMPLETE" is displayed.   
If you don't see it, it's likely that you can't write to it.   
In that case, you need to reset the stack-chan and quickly flash the mod, but hold down the reset button for at least 3 seconds to enter forced write mode.

```console
$ npm run mod --target=esp32/m5stack_cores3 [mod manifest file path]
```


**Example: Installing [`mods/look_around`](../mods/look_around/)**

```console
$ npm run mod --target=esp32/m5stack_cores3 ./mods/look_around/manifest.json

> stack-chan@0.2.1 mod
> mcrun -d -m -p ${npm_config_target=esp32/m5stack} ${npm_argument} "./mods/look_around/manifest.json"

# xsc mod.xsb
# xsc check.xsb
# xsc mod/config.xsb
# xsl look_around.xsa
Installing mod...complete
```

The port may not be found, and the message "/bin/sh: 1: [[ not found" may be displayed and writing may not be possible. At that time, specify the port before npm.   
The following is an example of writing mods/cherrup_ble_lite for windows (WLS2).
```console
$  UPLOAD_PORT=/dev/ttyACM0 npm run mod --target=esp32/m5stack_cores3 ./mods/cheerup_ble_lite/manifest.json
```

## Next Step

- [mods/README.md](../mods/README.md): The list of example mods
- [API](./api.md): API document
