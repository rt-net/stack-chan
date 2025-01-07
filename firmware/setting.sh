#!/bin/sh

# Deactivate SPIRAM
sed -i 's/CONFIG_SPIRAM=y/CONFIG_SPIRAM=n/' $HOME/.local/share/moddable/build/devices/esp32/targets/m5stack_cores3/sdkconfig/sdkconfig.defaults
cat $HOME/.local/share/moddable/build/devices/esp32/targets/m5stack_cores3/sdkconfig/sdkconfig.defaults