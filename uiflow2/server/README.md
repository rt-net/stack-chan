# 音声認識サーバーおよび音声合成サーバー
## 音声認識サーバー

ローカルPC上で動作する音声認識サーバーです。Voskというライブラリを使用しています。
このサーバーは、スタックチャンと連携することを念頭に、REST APIで動作するように実装したものです。

この音声認識サーバーを動作させるには、VOSKの[日本語音声認識モデル](https://alphacephei.com/vosk/models) (vosk-model-small-ja-0.22 または vosk-model-ja-0.22)が必要です。

### インストール
VOSKは、pipコマンドでインストールすることができます。
Ubuntu-24.04以降では、pipコマンドでライブラリをインストールする場合には、venvを用いた仮想環境で実行することが推奨されています。

ここでは、venvを使った仮想環境を使った例を示します。
以下のように、venvを作成して、voskの動作に必要なライブラリをインストールします。

```
 $ python3 -m venv vosk
 $ source vosk/bin/activate
 (vosk)$ pip install -r requirements_vosk.txt
```
インストールが完了したら、vosk-model-ja-0.22をダウンロードし、vosk-server.pyと同じディレクトリに配置してください。

### 起動
音声認識サーバーを起動するには、以下のコマンドを入力します。

```
$ source vosk/bin/activate
(vosk) $ python3 vosk-server.py
```

以上で、音声認識サーバが起動します。
音声認識サーバーのデフォルトのポート番号は、```8000```にしています。

## 音声合成サーバー
音声合成サーバーは、voicevoxを使用します。voicevoxのREST APIをサポートしたサーバーは、dockerで公開されていますので、そちらを使用します。

dockerコンテナは、以下のものです。
- voicevox/vicevox_engine:cpu-ubuntu20.04-latest

### インストール
voicevox_engineのdockerのセットアップは、以下のコマンドを入力します。

```
 $ voicevox/setup_docker.sh
```

### 起動
セットアップ終了後、voicevox_engineを起動します。
```
 $ voicevox/run_voicevox.sh
```
以上で、音声合成サーバが起動します。
音声合成サーバーのデフォルトのポート番号は、```50021```にしています。

