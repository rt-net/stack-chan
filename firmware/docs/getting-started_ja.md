# 環境構築（MacOS/Linux）マニュアル

[English](./getting-started.md)

ｽﾀｯｸﾁｬﾝはWindows11、MacOS、Linuxで開発ができます。Windows 11の場合はWSL2を使った環境構築手順を参照してください。ここでは、MacOS/Linuxでの開発環境の方法を示します。

* **[Windows 11 のｽﾀｯｸﾁｬﾝ環境構築マニュアル（WSL2）](./getting-started-wsl2_ja.md)**

## 開発に必要なもの

* ホストPC
    * Linux(Ubuntu22.04 or Ubuntu24.04)でテスト済み
    * MacOS(Sonoma 14 Appleシリコン)でテスト済み
* [ｽﾀｯｸﾁｬﾝ アールティver.](https://rt-net.jp/products/rt-stackchan/) または その互換品
* USB type-Cケーブル
* 事前にインストールしておくアプリ
  * [cmake](https://cmake.org/)
  * [git](https://git-scm.com/)
  * [Node.js](https://nodejs.org/en/)
    * cherrup_ble_liteのmodに関しては、新しいNode.jsに対応していないためV18.x.xを使用する必要があります。
    * その他のmodはv22.8.xで動作することは確認しています。
  * Python3.12で動作確認ができています。(macOSはbrewでインストールするのではなく[https://www.python.org](https://www.python.org)からダウンロードしインストールしてください。)
  * xcode-select(macOSのみ)  

## ｽﾀｯｸﾁｬﾝリポジトリのクローンとnodeのmoduleのインストール

```console
$ git clone https://github.com/rt-net/stack-chan.git
$ cd stack-chan/firmware
$ npm install
```

## ModdableSDKのセットアップ

ホストPCで[ModdableSDK](https://github.com/Moddable-OpenSource/moddable)と
[ESP-IDF](https://docs.espressif.com/projects/esp-idf/en/latest/esp32/get-started/index.html)をインストールします。
次の2通りの方法があります。

- xs-dev（CLI）を使う（推奨）
- 手動でセットアップする

### xs-dev（CLI）を使う（推奨）

ｽﾀｯｸﾁｬﾝはセットアップ手順をnpmスクリプト化しています。
`stack-chan/firmware`ディレクトリで次のコマンドを実行します。

以下に示す１つ目のコマンドの実行直後、Ubuntuに設定したパスワードの入力が要求されますので入力してください。 パスワード入力後、一定時間は同様のコマンドを実行してもパスワードは要求されません。

２つ目のコマンドでは、再度パスワードが要求されない内に実行してください。 もし、何らかの理由で１つめのコマンド実行から時間がかかってしまった場合は１つ目のコマンドの実行からやり直してください。

```console
$ sudo echo "emporary SuperUser Grant"
$ npm run setup
$ npm run setup -- --device=esp32
```

macOSの場合は、npm run setup -- --device=esp32のインストールの時、xcode-selectのバージョンが古いと"Error: Command failed with exit code 1: python3 -m pip install pyserial"で止まることがあります。その場合は、xcode-selectを手動で削除してから再度xcode-select(xcord-select –install)をインストールしてください。 
xcode-selectの削除は"sudo rm -rf /Library/Developer/CommandLineTools"でできます。  
内部で[`xs-dev`](https://github.com/HipsterBrown/xs-dev)を使ってModdableSDKやESP-IDFのセットアップを自動化しています。  


### 手動でセットアップする

[公式サイトの手順（英語）](https://github.com/Moddable-OpenSource/moddable/blob/public/documentation/Moddable%20SDK%20-%20Getting%20Started.md)に従ってModdableSDKとESP-IDFをインストールします。
xs-dev（CLI）でうまくセットアップできない場合はこちらを行ってください。

- **ｽﾀｯｸﾁｬﾝ アールティver.では、Moddable SDK 4.9.5、ESP-IDF 5.3.0 での動作を想定しています。**
- **intel macはModdable SDK 4.7.0 + ESP-IDF 5.1.0 python3.9.0で動作することは確認しています。intel macで使用するには`firmware/package.json`の`"setup": "xs-dev setup --target-branch 4.9.5"`を`"setup": "xs-dev setup --target-branch 4.7.0"`にすることでインストールできますがサポート対象外になります。**

### PSRAMと環境変数のセットアップ

次のコマンドを実行して、PSRAMの設定をします。

```console
$ ./setting_scripts/unset_psram.sh
```

次のコマンドを実行し、Shellの設定ファイルに`source ~/.local/share/xs-dev-export.sh`を追加します。これにより、Shellの起動時に環境変数を設定されます。

```console
$ ./setting_scripts/set_xs-dev_env.sh 
```

## 環境のテスト

`npm run doctor`コマンドで環境のテストができます。
インストールに成功していれば次のようにModdable SDKのバージョンとして4.9.5が表示され、Supported target devicesにesp32が表示されます。

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

`grep CONFIG_SPIRAM= $MODDABLE/build/devices/esp32/targets/m5stack_cores3/sdkconfig/sdkconfig.defaults`コマンドでM5Stack CoreS3のPARAMの設定を確認できます。
設定が完了していれば、`CONFIG_SPIRAM=n`と出力されます。

```console
$ grep CONFIG_SPIRAM= $MODDABLE/build/devices/esp32/targets/m5stack_cores3/sdkconfig/sdkconfig.defaults
CONFIG_SPIRAM=n
```

## 次のステップ

- [プログラムのビルドと書き込み](./flashing-firmware_ja.md)
