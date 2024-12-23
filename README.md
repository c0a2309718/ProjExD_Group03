# 駆けろ！こうかとん

## 実行環境の必要条件
* python >= 3.10
* pygame >= 2.1

## ゲームの概要
* プレイヤーは「こうかとん」を操作し、障害物を避けながら地面に落ちないように足場を飛び移り、スコアを稼いでいくゲームです。
* 参考URL：[スクラッチでスーパーマリオランの作り方](https://bingo-ojisan.xyz/2024/07/20/supermariorun/)

## ゲームの遊び方
* スペースキー：こうかとんをジャンプさせる。ジャンプ中にさらにスペースキーを押すことで、もう一度ジャンプ（2段ジャンプ）することができる。
* 「こうかとん」が地面に落ちるとゲームオーバーになる。

## ゲームの実装
### 共通基本機能
* 背景画像とこうかとんの描画
* 流れてくるブロックの描画
* 無限にジャンプが可能

### 分担追加機能
* ブロックに関する関数・２段ジャンプの追加（担当：武末）：ランダムなブロックを生成する関数、ブロックの移動のための関数、ブロックとの衝突判定をする関数、２段ジャンプ機能の導入、効果音の追加
* 
* 
* 
* 

### ToDo
- [ ] ブロックの上に障害物の追加
- [ ] ジャンプ音などの追加

### メモ
