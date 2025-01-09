#!/bin/sh

# 設定ファイルパスを取得
SDKCONFIG="$HOME/.local/share/moddable/build/devices/esp32/targets/m5stack_cores3/sdkconfig/sdkconfig.defaults"

# macOS と Linux の sed コマンドの互換性を考慮
if [ "$(uname)" = "Darwin" ]; then
    # macOS 用
    sed -i '' 's/CONFIG_SPIRAM=y/CONFIG_SPIRAM=n/' "$SDKCONFIG"
else
    # Linux 用
    sed -i 's/CONFIG_SPIRAM=y/CONFIG_SPIRAM=n/' "$SDKCONFIG"
fi

# 結果を表示
cat "$SDKCONFIG"
