# 環境構築

[English](./getting-started.md)

ｽﾀｯｸﾁｬﾝはWindows11、MacOS、Linuxで開発ができます。Windows 11の場合はWSL2を使った環境構築手順を参照してください

* **[Windows 11 のｽﾀｯｸﾁｬﾝ環境構築マニュアル（WSL2）](./getting-started-wsl2_ja.md)**

## 開発に必要なもの

* ホストPC
    * Linux(Ubuntu22.04)でテスト済み
* M5Stack CoreS3
* USB type-Cケーブル
* [git](https://git-scm.com/)
* [Node.js](https://nodejs.org/en/)
    * v20.11.0でテスト済み

## ｽﾀｯｸﾁｬﾝリポジトリのクローン

`--recursive`オプションをつけて本リポジトリをクローンします。

```console
$ git clone --recursive https://github.com/rt-net/stack-chan.git
$ cd stack-chan/firmware
$ npm i
```

## ModdableSDKのセットアップ

ホストPCで[ModdableSDK](https://github.com/Moddable-OpenSource/moddable)と
[ESP-IDF](https://docs.espressif.com/projects/esp-idf/en/latest/esp32/get-started/index.html)をインストールします。
次の3通りの方法があります。

- CLIを使う（推奨）
- 手動でセットアップする

### xs-devを使う（推奨）

ｽﾀｯｸﾁｬﾝはセットアップ手順をnpmスクリプト化しています。
`stack-chan/firmware`ディレクトリで次のコマンドを実行します。

```console
$ npm run setup
$ npm run setup -- --device=esp32
```

内部で[`xs-dev`](https://github.com/HipsterBrown/xs-dev)を使ってModdableSDKやESP-IDFのセットアップを自動化しています。

#### ターミナルから

`stack-chan/firmware`ディレクトリで次のコマンドを実行します。

```console
$ ./docker/build-container.sh
$ ./docker/launch-container.sh

# コンテナ内で以下を実行
$ npm install
```

#### VSCodeから

VSCodeのDevContainer用設定を同梱しています。
以下のコマンドでコンテナ内でプロジェクトを開けます。

* コマンドパレットを開く(ctrl+shift+p)
* `>Remote-Containers: Reopen in Container`を実行する

### 手動で行う

[公式サイトの手順（英語）](https://github.com/Moddable-OpenSource/moddable/blob/public/documentation/Moddable%20SDK%20-%20Getting%20Started.md)に従ってModdableSDKとESP-IDFをインストールします。
CLIやDockerがうまくセットアップできない場合はこちらを行ってください。

## 環境のテスト

`npm run doctor`コマンドで環境のテストができます。
インストールに成功していれば次のようにModdable SDKのバージョンが表示され、Supported target devicesにesp32が表示されます。

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

## 次のステップ

- [プログラムのビルドと書き込み](./flashing-firmware_ja.md)
