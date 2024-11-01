# Getting Started (MacOS/Linux)

[日本語](./getting-started_ja.md)

Stack-chan can be developed on Windows 11, MacOS, and Linux. For Windows 11, please refer to the setup instructions using WSL2 (Japanese only). Here, we will outline the development environment setup for MacOS/Linux (operation on MacOS has not been verified).

* **[(WSL2) Windows 11 Stack-chan Environment Setup Manual (Japanese)](./getting-started-wsl2_ja.md)**

## Prerequisites

* Host PC
    * Tested on Linux (Ubuntu 22.04)
* [Stack-chan RT ver.](https://rt-net.jp/products/rt-stackchan/) or its compatible product
* USB type-C cable
* [git](https://git-scm.com/)
* [Node.js](https://nodejs.org/en/)
    * Tested with v20.11.0

## Clone the repository

Clone this repository with the `--recursive` option.

```console
$ git clone --recursive https://github.com/rt-net/stack-chan.git
$ cd stack-chan/firmware
$ npm i
```

## Setting up ModdableSDK

On the host PC, install [ModdableSDK](https://github.com/Moddable-OpenSource/moddable) and
Install [ESP-IDF](https://docs.espressif.com/projects/esp-idf/en/latest/esp32/get-started/index.html) on the host PC.
There are two ways to do this.

- Using the xs-dev(CLI) (recommended)
- Set up manually

### Using xs-dev(CLI) (recommended)

Stack-Chan has npm scripting of the setup procedure.
Run the following command in the `stack-chan/firmware` directory.

```console
$ npm run setup
$ npm run setup -- --device=esp32
```

The script internally uses [`xs-dev`](https://github.com/HipsterBrown/xs-dev) to automate the setup of ModdableSDK and ESP-IDF.

### Set up Manual

Follow the instructions on the [official website (English)](https://github.com/Moddable-OpenSource/moddable/blob/public/documentation/Moddable%20SDK%20-%20Getting%20Started.md) to install ModdableSDK and ESP-IDF.
If you cannot setup xs-dev(CLI) properly, please do this.

**The Stack-chan RT version is designed to operate with Moddable SDK 4.1**

## Test the environment

You can test the environment with the `npm run doctor` command.
If the installation was successful, the version of Moddable SDK will be displayed as follows, and esp32 will be displayed in Supported target devices.

```console
$ npm run doctor

> stack-chan@0.2.1 doctor
> echo stack-chan environment info: && git rev-parse HEAD && git rev-parse --show-toplevel && xs-dev doctor

stack-chan environment info:
55d005ac9f0764a4ebc561b7d0a2a29a66ee5199
/home/kurasawa/Projects/stack-chan
xs-dev environment info:
  CLI Version                0.28.1
  OS                         Linux
  Arch                       x64
  Shell                      /bin/bash
  NodeJS Version             v20.11.0 (/home/ubuntu/.volta/tools/image/node/20.11.0/bin/node)
  Python Version             3.10.12 (/home/ubuntu/.rye/shims/python)
  Moddable SDK Version       4.1 (/home/ubuntu/.local/share/moddable)
  Supported target devices   lin, esp32
  ESP32 IDF Directory        /home/ubuntu/.local/share/esp32/esp-idf
```

## Next step

- [Build and Flash firmware](./flashing-firmware.md)
