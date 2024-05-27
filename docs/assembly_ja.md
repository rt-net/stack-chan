# ｽﾀｯｸﾁｬﾝ アールティver. 組み立てマニュアル

ｽﾀｯｸﾁｬﾝ アールティver.で使用するネジは6本で、それ部品の凹凸部のはめ合いで固定するスナップフィットで組み立てます。

## パーツ一覧

ｽﾀｯｸﾁｬﾝの組み立てには以下のパーツを使用します。

1. M5Stack CoreS3
2. 基板
3. シェル
4. バッテリーパック(内)
5. バッテリーパック(外)
6. バッテリー(1セル 450mAh)
7. 足(上)
8. 足(下)
9. サーボブラケット(後)
10. サーボブラケット(前)
11. サーボモータ１
12. サーボモータ２
13. サーボホーン
14. TTLケーブル 2本
15. タップネジ(M2x5) 4本
16. 六角穴付きネジ(M3x14) 2本
17. 六角穴付きネジ(M3x12) 2本

![](images/assembly/all_parts.jpg)

## 使用工具一覧

- プラスドライバー（M2ネジ用）
- マイナスドラバー（先端幅5.5[mm]以下）
- 六角レンチ（M2ネジ用）
- 【オプション】六角レンチ（M3ネジ用）

## 組み立て

以下に示す順番通りに組み立ててください。

### ネジの取り外し

サーボモータ１とサーボモータ２に取り付けられたタップネジ(M2.6x6)を取り外します。

サーボモータ１：青色のシールが貼られたサーボモータ
サーボモータ２：緑色のシールが貼られたサーボモータ


![](images/assembly/disassembling_screw.JPG)

取り外した2本のネジは、この後に使用するので取っておいてください。画像左側のパーツ（『not used』と書かれたパーツ）はｽﾀｯｸﾁｬﾝ アールティver.では使用しません。

![](images/assembly/disassembling_servo.JPG)

### 胴体の組み立て

サーボモータ１とサーボモータ２を画像の通りに接続します。

サーボモータ１とサーボモータ２には、それぞれID1とID2が事前に割り振られており、M5Stackとの通信の際、ソフトウェア上での個体識別として用いています。目印として、ID1に青色、ID2には緑色のシールが貼られています。取り付けが逆にならないように注意してください。

![servo_wired](images/assembly/servo_wired.JPG)

胴体となる部分はサーボモータ１とサーボモータ２をサーボプラケットで固定します。ケーブルを挟まないように注意しつつ、サーボブラケット(前)とサーボブラケット(後)で挟み込みます。
この際、サーボに「DYNAMIXEL XL330-M288-T」と書いてあるラベルが矢印方向に向くようにしてください。


![born_prev](images/assembly/born_purge.JPG)

2つのサーボモータをサーボブラケットで挟んで固定します。

![born](images/assembly/born_base.JPG)


### 足の取り付け

胴体にｽﾀｯｸﾁｬﾝの足を取り付けます。

サーボモータ１の突起と足(上)の接合部の切り欠きの位置を合わせてグッと押して固定してください。

<p>
    <img src="images/assembly/servo_protrusion_focus.JPG" width="35%"> <img src="images/assembly/feet_cutout.JPG" width="60%">
</p>

![](images/assembly/servo_and_feet_protrusions.JPG)

サーボモータ用のネジ（M2.6タップネジ）を締めて固定します。

![](images/assembly/tightening_feet_screw.JPG)

ネジを奥まで締めたら、足(下)を取り付けます。

![](images/assembly/feet_bottom_assembled.JPG)

足を取り付けると以下の画像のようになります。

![](images/assembly/born_feet.JPG)

#### 足の分解方法

足(上)に取り付けた足(下)は4箇所の窪みから取り外すことができます。1箇所ずつ、マイナスドライバーを窪みに差し込み、足(上)のフチを支点としたテコの原理で固定を外します。

![](images/assembly/disassembling_feet.JPG)

### サーボホーンの取り付け

サーボホーンを胴体に取り付けます。

サーボモータ２とサーボホーンが共にギヤの形状となっている部分同士を取り付けます。足の取り付けの際と同様に突起と切り欠きの位置を合わせてグッと押し込んでください。

![](images/assembly/servo_and_horn_protrusions.JPG)

突起の位置を合わせて接合したギヤ部分にM2.6タップネジを締めてください。

![](images/assembly/tightening_horn_screw.JPG.JPG)

### バッテリーパックの取り付け

バッテリーパックを取り付けます。

バッテリーをバッテリーパック(内)の窪みに入れます。パッテリーのコードはスリットを通して外に出してください。

![](images/assembly/battery_into_backpack.JPG)

雷マークが描かれたバッテリーパック(上)を閉めます。

<p>
    <img src="images/assembly/backpack_opening.JPG" width="50%"><img src="images/assembly/backpack_assembled.JPG" width="50%">
</p>

バッテリーパック(内)から出ている突起をサーボブラケット(後)に引っ掛けて固定します。

![](images/assembly/born_backpackd.JPG)

位置を合わせたら矢印方向にスライドしてください。

<p>
    <img src="images/assembly/born_backpack_attaching.JPG" width="50%"><img src="images/assembly/born_backpack_sliding.JPG" width="50%">
</p>


![](images/assembly/born_assembled.JPG)

### 外装の取り付け

ｽﾀｯｸﾁｬﾝの外装となるシェルを取り付けます。

シェルの天板内側にある突起とサーボホーンを取り付けます。バッテリーのコードとサーボモータのTTLケーブルを前に持ってきなからスライドして入れてください。

![](images/assembly/born_shell.JPG)

突起によってｶﾁｯ！と手応えがあるまでスライドさせてください。

![](images/assembly/born_slide_shell.JPG)

取り付けて反対側から見ると以下の画像のようになります。青色のラインはサーボホーンの輪郭です。

![](images/assembly/born_shell_assembled.JPG)

### 基板の取り付け

サーボモータに取り付けたTTLケーブルとバッテリーのケーブルを基板の指定した端子につなげます。

<span style="font-size: 120%; color: red;">バッテリー端子の向きに気をつけてください。間違えると故障の原因となります。</span>

![](images/assembly/cable_connecting.JPG)

画像の通り、基板に取り付けられた青と黒のコネクタが上になるように基板とシェルの穴の位置を合わせてネジ（M2タップネジ）を4つ締めて固定します。スライドスイッチが基板から突出しているため、シェルの側面にある穴に斜めに入れてネジの位置を合わせます。


<span style="font-size: 120%; color: red;">ネジが導体（銀色の箇所）には触れないように注意してください。バッテリの端子が接続されているためショートする恐れがあります。</span>

<p>
    <img src="images/assembly/board_shell_attaching.JPG" width="50%"><img src="images/assembly/board_shell_assembling.JPG" width="50%">
</p>

基板まで取り付けると以下の画像のようになります。

![](images/assembly/board_assembled.JPG)

### M5Stack CoreS3の取り付け

M5Stack CoreS3を基板に対してピンの位置をわせてグッと押し込んでください。

![](images/assembly/m5_attaching.JPG)

無事に取り付けられたらｽﾀｯｸﾁｬﾝの組み立ては完了です。

![](images/assembly/stack-chan_assembled.JPG)


### 【オプション】M5Stack CoreS3の固定

M5Stack CoreS3をしっかり固定したい場合は、キットに付属している4本の六角穴付きネジ（六角ネジ）で固定します。ネジの長さは２種類あるため注意してください。

バッテリーパックをサーボブラケット(後)から取り外し、バッテリーの端子も基板から外します。短いほうの六角ネジ2本をｽﾀｯｸﾁｬﾝの上側に、長いほうの六角ネジ2本を下側に取り付けます。4本のネジを締め終えたらバッテリーパックを再度取り付けます。

![](images/assembly/back_screws.JPG)

![](images/assembly/assembling_back_screws.JPG)

<span style="font-size: 120%; color: red;">六角ネジを取り付ける際は、必ずバッテリーを外してから取り付けてください。ネジを基板上に落とすとショートして壊れる恐れがあります。</span>

<span style="font-size: 120%; color: red;">必ず短い六角ネジを上側、長い六角ネジは下側に取り付けてください。間違えると液晶を壊す恐れがあります。</span>