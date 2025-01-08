# Getting Started (MacOS/Linux)

[日本語](./getting-started_ja.md)

Stack-chan can be developed on Windows 11, MacOS, and Linux. For Windows 11, please refer to the setup instructions using WSL2 (Japanese only). Here, we will outline the development environment setup for MacOS/Linux.

* **[(WSL2) Windows 11 Stack-chan Environment Setup Manual (Japanese)](./getting-started-wsl2_ja.md)**

## Prerequisites

* Host PC
    * Tested on Linux (Ubuntu 22.04 or Ubuntu24.04)
    * Tested on MaxOS (Sonoma 14 Apple silicon)
* [Stack-chan RT ver.](https://rt-net.jp/products/rt-stackchan/) or its compatible product
* USB type-C cable
* [git](https://git-scm.com/)
* [Node.js](https://nodejs.org/en/)
  * As for the mod for cherrup_ble_lite, you need to use V18.x.x as it does not support the new Node.js.
  * I've confirmed that other mods work with v22.8.x.
* The operation has been confirmed with Python 3.12. (Please download and install macOS from https://www.python.org instead of installing it with brew.)) 
* xcode-select (macOS only)

## Clone the Stack-chan repository and install the module on node

```console
$ git clone https://github.com/rt-net/stack-chan.git
$ cd stack-chan/firmware
$ npm install
```

## Setting up ModdableSDK

On the host PC, install [ModdableSDK](https://github.com/Moddable-OpenSource/moddable) and
Install [ESP-IDF](https://docs.espressif.com/projects/esp-idf/en/latest/esp32/get-started/index.html) on the host PC.
There are two ways to do this.

- Using the xs-dev(CLI) (recommended)
- Set up manually

### Using xs-dev(CLI) (recommended)
Stack-chan has npm scripted setup instructions.

In the `stack-chan/firmware` directory, run the following command:

Immediately after executing the first command shown below, you will be asked to enter the password set in Ubuntu.  
After entering the password, the password will not be requested even if the same command is executed for a certain period of time.   

For the second command, run it before you are prompted for a password again. If, for some reason, it takes a long time to execute the first command, please start over from the execution of the first command.

```console
$ sudo echo "emporary SuperUser Grant"
$ npm run setup
$ npm run setup -- --device=esp32
```

For macOS, when installing npm run setup -- --device=esp32, if the version of xcode-select is outdated, it may stop at "Error: Command failed with exit code 1: python3 -m pip install pyserial". In that case, manually remove xcode-select and install xcode-select (xcord-select –install) again.  
You can remove xcode-select with "sudo rm -rf /Library/Developer/CommandLineTools".   
Internally, [`xs-dev`](https://github.com/HipsterBrown/xs-dev)  is used to automate the setup of ModdableSDK and ESP-IDF.

The moddable configuration script xs-dev-export.sh is not automatically loaded when starting the terminal.   
Add source ~/.local/share/xs-dev-export.sh to ~/.bashrc or ~/.zshrc.

The script internally uses [`xs-dev`](https://github.com/HipsterBrown/xs-dev) to automate the setup of ModdableSDK and ESP-IDF.

## Set up Manual

Follow the instructions on the [official website (English)](https://github.com/Moddable-OpenSource/moddable/blob/public/documentation/Moddable%20SDK%20-%20Getting%20Started.md) to install ModdableSDK and ESP-IDF.
If you cannot setup xs-dev(CLI) properly, please do this.

- **Stack-chan RT version assumes that Moddable SDK 4.9.5 and ESP-IDF 5.3.0 will work.**
- **We have confirmed that intel mac works with Moddable SDK 4.7.0 + ESP-IDF 5.1.0 python 3.9.0. To use it on Intel Macs, you can install it by changing "setup": "xs-dev setup --target-branch 4.9.5" to "setup": "xs-dev setup --target-branch 4.7.0" in firmware/package.json, but it is not supported.**

## Set up PSRAM and Environment Variable

To configure the PSRAM settings, execute the following command.

```console
$ ./setting_scripts/setting_unset_psram.sh
```

Next, run the following command to automatically add source `~/.local/share/xs-dev-export.sh` to your shell's configuration file. This ensures that the necessary environment variables are set each time the shell is started.

```console
$ ./setting_scripts/setting_xs-dev_env.sh 
```

By completing these steps, your shell environment will be configured correctly for the Moddable SDK and ESP-IDF.

## Test the environment

You can test your environment with the `npm run doctor` command.   
If the installation is successful, 4.9.5 will be displayed as the version of Moddable SDK as shown below, and esp32 will be displayed in Supported target devices.

```console
$ npm run doctor

> stack-chan@0.2.1 doctor
> echo stack-chan environment info: && git rev-parse HEAD && git rev-parse --show-toplevel && xs-dev doctor

stack-chan environment info:
55d005ac9f0764a4ebc561b7d0a2a29a66ee5199
/home/ubuntu/stack-chan
xs-dev environment info:
  CLI Version                0.32.3
  OS                         Linux
  Arch                       x64
  Shell                      /bin/bash
  NodeJS Version             v22.8.0 (/home/ubuntu/.nvm/versions/node/22.8.0/bin/node)
  Python Version             3.12.3 (/usr/bin/python)
  Moddable SDK Version       4.9.5 (/home/ubuntu/.local/share/moddable)
  Supported target devices   lin, esp32
  ESP32 IDF Directory        /home/ubuntu/.local/share/esp32/esp-idf
```


You can check the PARAM settings for the M5Stack CoreS3 with the `$ cat $MODDABLE/build/devices/esp32/targets/m5stack_cores3/sdkconfig/sdkconfig.defaults` command.
If the settings are correctly configured, you will find a line stating `CONFIG_SPIRAM=n`.

```console
$ cat $MODDABLE/build/devices/esp32/targets/m5stack_cores3/sdkconfig/sdkconfig.defaults

CONFIG_ESP_CONSOLE_UART_DEFAULT=y
CONFIG_ESP_CONSOLE_UART=y
CONFIG_CONSOLE_UART_NUM=0
CONFIG_ESP_CONSOLE_UART_BAUDRATE=115200

CONFIG_ESP_SYSTEM_PANIC_GDBSTUB=n
CONFIG_ESP_COREDUMP_ENABLE_TO_UART=n
CONFIG_ESP_COREDUMP_ENABLE=n

# CONFIG_ESPTOOLPY_FLASHSIZE_4MB=y
# CONFIG_ESPTOOLPY_FLASHSIZE="4MB"
CONFIG_ESPTOOLPY_FLASHSIZE_16MB=y
CONFIG_ESPTOOLPY_FLASHSIZE="16MB"

#CONFIG_ESPTOOLPY_FLASHMODE_QIO=y
#CONFIG_FLASHMODE_QIO=y

CONFIG_ESPTOOLPY_FLASHMODE_DIO=y

CONFIG_SPIRAM=n
CONFIG_SPIRAM_MODE_OCT=n
CONFIG_SPIRAM_MODE_QUAD=y
CONFIG_SPIRAM_SPEED_120M=n
CONFIG_SPIRAM_SPEED_80M=n
CONFIG_SPIRAM_SPEED_40M=y
CONFIG_SPIRAM_TYPE_AUTO=y
CONFIG_SPIRAM_IGNORE_NOTFOUND=y
CONFIG_SPIRAM_USE_MALLOC=y
# CONFIG_SPIRAM_MEMTEST=y

# CONFIG_BOOTLOADER_LOG_LEVEL_VERBOSE=y
```

## Next step

- [Build and Flash firmware](./flashing-firmware.md)
