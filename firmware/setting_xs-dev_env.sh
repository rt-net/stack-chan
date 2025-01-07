#!/bin/sh

# 追記するコマンドを設定
XS_DEV_SH="source ~/.local/share/xs-dev-export.sh"

# 現在のシェルを取得
CURRENT_SHELL=$(basename "$SHELL")

# 設定ファイルを決定
if [ "$CURRENT_SHELL" = "bash" ]; then
    CONFIG_FILE="$HOME/.bashrc"
elif [ "$CURRENT_SHELL" = "zsh" ]; then
    CONFIG_FILE="$HOME/.zshrc"
else
    echo "Unsupported shell: $CURRENT_SHELL"
    exit 1
fi

# 設定ファイルが存在しない場合は作成
if [ ! -f "$CONFIG_FILE" ]; then
    touch "$CONFIG_FILE"
    echo "# Created $CONFIG_FILE for $CURRENT_SHELL settings" >> "$CONFIG_FILE"
    echo "$CONFIG_FILE was created."
fi

# ファイルに追記
if grep -Fxq "$XS_DEV_SH" "$CONFIG_FILE"; then
    echo "The string '$XS_DEV_SH' already exists in $CONFIG_FILE. No changes made."
else
    echo "$XS_DEV_SH" >> "$CONFIG_FILE"
    echo "The string '$XS_DEV_SH' has been added to $CONFIG_FILE."
fi