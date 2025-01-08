# プログラムのビルドと書き込み

[English](./flashing-firmware.md)

## ｽﾀｯｸﾁｬﾝのプログラム構成について

### ホストと MOD

![ｽﾀｯｸﾁｬﾝのプログラム構成](./images/host-and-mod.jpg)

ｽﾀｯｸﾁｬﾝのファームウェアは、ｽﾀｯｸﾁｬﾝの基本動作を提供するプログラム（ホスト）とユーザアプリケーション（MOD）から構成されます。
一度ホストを書き込んでしまえば、ユーザアプリケーションのインストールは短時間で終わるため高速な開発が可能です。
最初にホストを書き込み、必要に応じて MOD の書き込みを行います。

### マニフェストファイル

ホストと MOD はそれぞれ、設定用のマニフェストファイル（manifest.json）、JavaScript モジュールのソースコード、画像や音声などのリソースから構成されます。
マニフェストファイルでは、JavaScript モジュールの名前と場所（modules）や、モジュール内から参照できる設定（config）などを含みます。
また、マニフェストファイルは他のマニフェストファイルを含める（include）こともできます。

全ての設定項目は[Moddable の公式ドキュメント（英語）](https://github.com/Moddable-OpenSource/moddable/blob/public/documentation/tools/manifest.md)を参照してください。

## 設定変更

ｽﾀｯｸﾁｬﾝが使うモータの種類やピンアサインなどをマニフェストファイルから変更できます。
ユーザが変更する設定は[`stack-chan/firmware/stackchan/manifest_local.json`](../stackchan/manifest_local.json)にまとまっています。
`"config"`キーの配下に次のような設定が書けます。

| キー              | 説明                                            | 使用可能な値                                |
| ----------------- | ----------------------------------------------- | ------------------------------------------- |
| driver.type       | モータドライバの種類                            | "dynamixel"           |
| driver.panId      | パン軸（首の横回転）に使うシリアルサーボの ID   | 1~254                                       |
| driver.tiltId     | チルト軸（首の縦回転）に使うシリアルサーボの ID | 1~254                                       |
| tts.type          | [TTS](./text-to-speech_ja.md) の種類            | "local", "voicevox"                         |
| tts.host          | TTS がサーバと通信する場合のホスト名            | "localhost", "ttsserver.local" などの文字列 |
| tts.port          | TTS がサーバと通信する場合のポート番号          | 1~65535                                     |

また、`"include"`キーの配下にリスト形式で他のマニフェストファイルのパスを指定できます。

## 基本プログラム（ホスト）の書き込み

前述の通りｽﾀｯｸﾁｬﾝのファームウェアは基本プログラム（ホスト）とユーザアプリケーション（MOD）から構成されます。

**esp-idfのバージョンが`5.x`からesp32に接続しているPSRAMの扱いが変わっています。デフォルト設定ではスムーズに動かないため一部変更しています。**
**[環境構築の設定変更スクリプト実行時](./getting-started_ja.md#設定の変更)に、`~/.local/share/moddable/build/devices/esp32/targets/m5stack_cores3/sdkconfig/sdkconfig.defaults`に記述された`CONFIG_SPIRAM=y`が`CONFIG_SPIRAM_n`に書き換えています。**

<br>

次のコマンドで基本プログラム（ホスト）の書き込みを行います。

_コマンドに`sudo`をつける必要はありません。_

```console
$ cd ~/stack-chan/firmware
$ npm run build --target=esp32/m5stack_cores3
$ npm run deploy --target=esp32/m5stack_cores3
```

Ubuntuの場合、書き込みポートがReadOnlyになっています。sudo chmod 666 /dev/ttyACM0でモードを書き換えるが、永続的にUSBポートの使用権限を変更する場合は、次のコマンドを実行してPCを再起動します。  

```console
$sudo usermod -aG dialout $USER
```

ビルドしたプログラムは`$MODDABLE/build/`ディレクトリ配下に保存されます。

正しく書き込めていれば起動から数秒後にｽﾀｯｸﾁｬﾝの顔が表示されます。
M5Stack のボタンを押すと次のように変わります。

- A ボタン（CoreS3 の場合は画面左下の領域） ... ｽﾀｯｸﾁｬﾝが 5 秒おきにランダムな方向を見る
- B ボタン（CoreS3 の場合は画面中央下の領域） ... ｽﾀｯｸﾁｬﾝが左、右、下、上を向く
- C ボタン（CoreS3 の場合は画面右下の領域） ... ｽﾀｯｸﾁｬﾝの顔の色が反転する

modを書き込みをした場合、上の動作ができなくなります。初期状態に戻すには、Flashの内容を消去してdeployで書き込む必要があります。

```console
$ ~/.espressif/python_env/idf5.3_py3.12_env/bin/esptool.py erase_flash
$ cd ~/stack-chan/firmware
$ npm run deploy --target=esp32/m5stack_cores3
```


## デバッグ

次のコマンドでプログラムのデバッグが可能です

```console
$ npm run debug --target=esp32/m5stack_cores3
```

このコマンドはModdableのデバッガ`xsbug`を開き、M5Stackと接続します。

![xsbug](./images/xsbug.png)

`xsbug`を使うとログの確認やブレークポイントの設定（プログラムの特定行で一時停止する）、ステップ実行（プログラムを1行ずつ実行する）などができます。
`xsbug`の詳しい使い方は[公式ドキュメント（英語）](https://github.com/Moddable-OpenSource/moddable/blob/public/documentation/xs/xsbug.md)を参照してください。

## ユーザアプリケーション（MOD）の書き込み

次のコマンドでユーザアプリケーション（MOD）の書き込みを行います。

_コマンドに`sudo`をつける必要はありません。_  
書き込みが完了するとcompleteのメッセージが表示されます。  
表示されない場合は、書き込みができない可能性か高いです。  
そのときはｽﾀｯｸﾁｬﾝをリセットし、素早くmodを書き込むがリセットボタンを3秒以上押し続けて強制書き込みモードにする必要があります。  


```console
$ npm run mod --target=esp32/m5stack_cores3 [modのマニフェストファイルのパス]
```

**例: [`mods/look_around`](../mods/look_around/)をインストールする**

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

ポートが見つからず "/bin/sh: 1: [[ not found"のメッセージが表示され書き込みができないことがあります。その時は、npmの前にポートを指定します。  
以下はwindows(WLS2)の[`mods/cherrup_ble_lite`](../mods/cheerup_ble_lite/)を書き込むときの例です。
```console
$  UPLOAD_PORT=/dev/ttyACM0 npm run mod --target=esp32/m5stack_cores3 ./mods/cheerup_ble_lite/manifest.json
```

## 次のステップ

- [mods/README_ja.md](../mods/README_ja.md): 同梱のサンプル MOD の紹介です。
- [API](./api_ja.md): ｽﾀｯｸﾁｬﾝの API ドキュメントです。
