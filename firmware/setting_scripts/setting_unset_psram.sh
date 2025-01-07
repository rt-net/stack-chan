#!/bin/sh

# 設定ファイルパスを取得
SDKCONFIG="$HOME/.local/share/moddable/build/devices/esp32/targets/m5stack_cores3/sdkconfig/sdkconfig.defaults"

# PSRAMを無効化
sed -i 's/CONFIG_SPIRAM=y/CONFIG_SPIRAM=n/' $SDKCONFIG
cat $SDKCONFIG