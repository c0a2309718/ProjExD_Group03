import os
import sys
import pygame as pg
import random  # ランダム生成用

os.chdir(os.path.dirname(os.path.abspath(__file__)))

# 定数の設定
WIDTH, HEIGHT = 800, 600
GRAVITY = 0.4           # 重力加速度
JUMP_POWER = -10        # ジャンプの初速
MOVE_SPEED = 10         # 横移動の速度
GROUND = HEIGHT - 100   # 地面の高さ
BLOCK_SPEED = 7         # ブロックの流れる速度

def create_random_block(offset=0):
    """ ランダムな位置と長さのブロックを生成する関数 """
    block_width = random.randint(50, 200)  # ブロックの幅（50〜200ピクセル）
    block_height = 20  # ブロックの高さ（固定）
    block_x = WIDTH + offset + random.randint(0, 300)  # X座標をランダムに設定（オフセット付き）
    block_y = random.randint(GROUND - 300, GROUND - 50)  # Y座標は地面から少し上の範囲
    return pg.Rect(block_x, block_y, block_width, block_height)

class Fly(pg.sprite.Sprite):
    """
    Fキーを押し続けている間滞空するクラス
    """
    
    def __init__(self):
        self.gravity = GRAVITY

    def flying(self, key_lst: list, mp: int, vy: float):
        """
        滞空を操作する
        引数1:押されているキーのリスト
        """
        if key_lst[pg.K_f]:
            if mp >= 1:
                return mp-1, 0
            else:
                y = vy + GRAVITY
                return mp, y
        else:
            y = vy + GRAVITY
            return mp, y 


def main():
    pg.display.set_caption("はばたけ！こうかとん")
    screen = pg.display.set_mode((WIDTH, HEIGHT))
    clock = pg.time.Clock()
    gravity = GRAVITY
    mp = 100
    fly = Fly()

    # 画像読み込み
    bg_img = pg.image.load("fig/pg_bg.jpg")
    bg_img2 = pg.transform.flip(bg_img, True, False)
    kk_img = pg.image.load("fig/3.png")
    kk_img = pg.transform.flip(kk_img, True, False)
    kk_rct = kk_img.get_rect()
    kk_rct.midbottom = 100, GROUND  # 初期位置

    # ブロックの初期生成（ランダムなオフセットを加えて生成）
    blocks = [create_random_block(i * 400) for i in range(5)]  # 初期ブロック5つ

    # 速度変数
    vy = 0  # 縦方向速度

    tmr = 0
    while True:
        key_lst = pg.key.get_pressed()
        for event in pg.event.get():
            if event.type == pg.QUIT:
                return     
            
        # ジャンプ処理（スペースキー）
        if key_lst[pg.K_SPACE]:
            vy = JUMP_POWER  # ジャンプ初速を設定

        # 重力による縦移動
        mp,vy = fly.flying(key_lst, mp, vy)
        kk_rct.move_ip(0, vy)

        # ブロックの移動処理と再生成
        for i, block in enumerate(blocks):
            block.move_ip(-BLOCK_SPEED, 0)  # ブロックを左に移動
            if block.right < 0:  # 画面外に出たらランダムに再生成
                blocks[i] = create_random_block(random.randint(200, 600))  # 次のブロックをランダム位置で再生成

        # キャラクターとブロックの当たり判定
        on_block = False
        for block in blocks:
            if kk_rct.colliderect(block) and vy > 0:  # キャラクターがブロックに乗る
                kk_rct.bottom = block.top
                vy = 0  # 落下を止める
                on_block = True
                break

        # 地面の処理（着地判定）
        if not on_block:  # ブロックの上にいない場合のみ地面を確認
            if kk_rct.bottom > GROUND:
                kk_rct.bottom = GROUND
                vy = 0  # 着地したら速度リセット

        # 背景スクロール
        x = -(tmr % 3200)
        screen.blit(bg_img, [x, 0])
        screen.blit(bg_img2, [x + 1600, 0])
        screen.blit(bg_img, [x + 3200, 0])
        screen.blit(bg_img2, [x + 4800, 0])

        # キャラクターの描画
        screen.blit(kk_img, kk_rct)

        # ブロックの描画
        for block in blocks:
            pg.draw.rect(screen, (0, 255, 0), block)  # 緑色のブロック

        pg.display.update()
        tmr += 10  # 背景スクロールの速度
        clock.tick(60)  # フレームレート設定

if __name__ == "__main__":
    pg.init()
    main()
    pg.quit()
    sys.exit()