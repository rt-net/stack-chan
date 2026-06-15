# このリポジトリについて
これは、RT版およびタカオ版ｽﾀｯｸﾁｬﾝのサンプルプログラムです。

[m5stack-avatar](https://github.com/stack-chan/m5stack-avatar)と[stackchan-arduino](https://github.com/stack-chan/stackchan-arduino)をベースに使用して、GoogleAPIを利用した対話機能を付加したものです。

RT版ｽﾀｯｸﾁｬﾝのArduino版のベースとして開発しています。

プログラムのビルドは、PlatformIOを使って下さい。

## 主な機能

- Webサーバー機能（REST-APIによる制御、コンテンツ作成 etc.）
- GoogleSpeechAPIを使った音声認識、音声合成
- Voicevoxを使った音声合成（独自Serverの対応）
- Vodkを使った音声認識（独自Serverの対応）
- Gemini InteractionAPIを使った対話生成（顔の表情と動作 MPCの実装）
- ChatGPT ResponseAPIを使った対話生成
- 内蔵カメラによるストリーミング
- タッチパネル上のボタン生成機能
- 割り込みタイマーによるランダムな表情変更および動作生成
- 時刻表示およびバッテリー状態表示
- フリック動作による簡易モーション

## 使用しているライブラリ
> [!IMPORTANT]
 注意：
> このプログラムを利用するには、ArduinoJson var.7 を使用しているため m5stack-avatarとstackchan-arduinoを修正したものを使用しています。オフィシャルのライブラリでは、不具合が発生する可能性があります。

- M5Unified
- ArduinoJson@7.2.2
- M5CoreS3@1.0.1
- [stachchan-arduino](https://github.com/haraisao/stackchan-arduino/tree/dev)
    - ESP32Servo
    - ServoEasing
    - ArduinoJson
    - Dynamixel2Arduino
    - YAMLDuino
    - SCServo
    - M5GFX
- [m5stack-avatar](https://github.com/haraisao/m5stack-avatar/tree/dev)

## インストール＆セットアップ
このリポジトリは、RT版のｽﾀｯｸﾁｬﾝをデフォルト設定としています。
このソフトウェアをインストールする場合には、PlatformIOの開発環境が必要ですので、事前にセットアップしてください。

簡単な導入方法は、[「Visual Studio Codeを用いたM5Unifiedの導入方法」](https://docs.m5stack.com/ja/arduino/m5unified/intro_vscode)を参考にしてください。

### リポジトリのダウンロード
PlatformIOの準備が整ったら、gitコマンドでリポジトリのソースコードをダウントードします。
リポジトリのダウンロードは、任意のディレクトリで大丈夫です。（ここでは、C:\Work　の下に作成します）
ターミナルを開いて、下記のように実行します。
```
PS> cd C:/Work
PS C:\Work> git clone -b arduino https://github.com/rt-net/stack-chan
```
### VS Codeでリポジトリを開く
リポジトリのダウンロードが終了したら、VS Code でフォルダを開きます。
ターミナルから下記のコマンドを実行します。
```
PS> cd C:/Work/stack-chan/platformio
PS C:\Work\stac-chan\platfoemio> code .
```
これで VS Codeが起動し、PlatformIOでビルドするために必要なファイル群がダウンロードされます。

### 設定ファイルの修正
このソフトウェアの設定ファイルは、 data/yaml/SC_BasicConfig.yaml と wlan.json、apikey.txt です。

- **SC_BasicConfig.yaml**は、RT版ｽﾀｯｸﾁｬﾝの設定にしていますが、ご自身のｽﾀｯｸﾁｬﾝの設定に合わせて修正してください。
- **wlan.json**は、無線LANアクセスポイントの設定です。これは、UiFlow2版のｽﾀｯｸﾁｬﾝと同じにしています。このファイルには、Home, Work, Mobileの3つのアクセスポイントの設定を入力することができます。
- **apikey.txt**は、音声認識、音声合成、対話生成に必要なAPIキーです。現在のところ、音声認識と音声合成は GoogleSpeechAPI（GOOGLE_SPEECH_KEY）、対話生成は Gemini（GEMINI_KEY）のみに対応しています。それぞのAPIキーを作成して、このファイルに転記してください。

### ファイルのアップロード
このソフトウェアでは、設定ファイルやHTMLファイル等をLittleFSまたはSDカード上にあることを想定しています。SDカードを使用する場合には、dataフォルダ以下のファイルをすべてコピーしてください。
LittleFSを使う場合には、PlatformIOの **'m5stack-cores3/Platform/Upload Filesystem Image'** でファイルをアップロードしてください。

### ビルドとインストール
準備が整ったら、ソフトウェアのビルドとインストールを実行してください。
Wifiアクセスポイントに接続完了すれば、「ピッポッ」とトーン音が鳴ります。Wifiアクセスポイントへの接続が失敗した場合には、「ピッピッ」とトーン音がなり、アクセスポイントとして動作しています。

#　その他の情報
Ardino版ｽﾀｯｸﾁｬﾝのプログラムの開発に関わる情報として、Zennに記事を書いています。

- [Arduino版ｽﾀｯｸﾁｬﾝ](https://zenn.dev/haraisao/articles/afa65dab1c9209)
- [PlatformIOで作るｽﾀｯｸﾁｬﾝ](https://zenn.dev/haraisao/articles/6095fcb10a717b)
