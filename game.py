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
ENEMY_SPEED = 13          # 敵の移動速度
ENEMY_WARNING_TIME = 120  # 予告線の表示時間
WARNING_FLASH_INTERVAL = 7  # 点滅の間隔
WARNING_ALPHA = 100  # 予告線の透明度（0〜255）
   
def create_random_block(offset=0):
    """ ランダムな位置と長さのブロックを生成する関数 """
    block_width = random.randint(50, 200)  # ブロックの幅（50〜200ピクセル）
    block_height = 20  # ブロックの高さ（固定）
    block_x = WIDTH + offset + random.randint(0, 300)  # X座標をランダムに設定（オフセット付き）
    block_y = random.randint(GROUND - 300, GROUND - 50)  # Y座標は地面から少し上の範囲
    return pg.Rect(block_x, block_y, block_width, block_height)

class Enemy:
    def __init__(self):
        """敵オブジェクトを初期化"""
        self.image = pg.image.load("fig/beam.png")  # ビーム画像を読み込む(fig/beam.png)
        self.image = pg.transform.flip(self.image, True, False)  # 画像を左右反転
        self.rect = self.image.get_rect()  # 画像の矩形を取得
        self.rect.x = WIDTH  # 初期位置を画面外に（右端から）
        self.rect.y = random.randint(50, HEIGHT - 300)  # Y座標はランダム
        self.warning_time = ENEMY_WARNING_TIME  # 予告線表示時間
        self.flash_timer = WARNING_FLASH_INTERVAL  # 点滅のタイマー
        self.flash_visible = True  # 点滅の表示状態

    def update(self):
        """敵の移動処理"""
        self.rect.move_ip(-ENEMY_SPEED, 0)  # 左方向に移動

    def draw(self, screen):
        """敵を描画"""
        screen.blit(self.image, self.rect)  # ビームを描画

    def draw_warning(self, screen):
        """予告線を描画"""
        if self.warning_time > 0:  # 予告線を表示中の場合
            if self.flash_timer <= 0:  # 点滅タイマーが切れたら点滅状態を切り替え
                self.flash_visible = not self.flash_visible  # 表示/非表示を切り替え
                self.flash_timer = WARNING_FLASH_INTERVAL  # タイマーをリセット
            else:
                self.flash_timer -= 1

            if self.flash_visible:  # 表示状態のときのみ予告線を描画
                # 半透明サーフェスを用意
                warning_surface = pg.Surface((WIDTH, 15), pg.SRCALPHA)
                warning_surface.fill((255, 0, 0, WARNING_ALPHA))  # 赤色で半透明
                screen.blit(warning_surface, (0, self.rect.y + self.rect.height // 2 - 5))  # 真ん中を通る予告線(-5で真ん中に調整)

            self.warning_time -= 1  # 表示時間を減少


def main():
    pg.display.set_caption("はばたけ！こうかとん")
    screen = pg.display.set_mode((WIDTH, HEIGHT))
    clock = pg.time.Clock()

    # 画像読み込み
    bg_img = pg.image.load("fig/pg_bg.jpg")
    bg_img2 = pg.transform.flip(bg_img, True, False)
    kk_img = pg.image.load("fig/3.png")
    kk_img = pg.transform.flip(kk_img, True, False)
    kk_rct = kk_img.get_rect()
    kk_rct.midbottom = 100, GROUND  # 初期位置

    # ブロックの初期生成
    blocks = [create_random_block(i * 400) for i in range(5)]

    # 速度変数
    vy = 0  # 縦方向速度

    # 敵(ビーム)の初期化
    enemies = []  # 敵オブジェクトを格納するリスト
    enemy_spawn_timer = 0  # 敵生成タイマー

    tmr = 0
    while True:
        for event in pg.event.get():
            if event.type == pg.QUIT:
                return

        # キー入力の取得
        key_lst = pg.key.get_pressed()

        # ジャンプ処理（スペースキー）
        if key_lst[pg.K_SPACE]:
            vy = JUMP_POWER  # ジャンプ初速を設定

        # 重力による縦移動
        vy += GRAVITY
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

        # 敵の生成処理
        enemy_spawn_timer -= 1
        if enemy_spawn_timer <= 0:  # 一定時間経過後に敵を生成
            enemies.append(Enemy())
            enemy_spawn_timer = random.randint(120, 240)  # 次の敵出現タイマー(敵出現頻度を変えるならここ)

        # 背景スクロール
        x = -(tmr % 3200)
        screen.blit(bg_img, [x, 0])
        screen.blit(bg_img2, [x + 1600, 0])
        screen.blit(bg_img, [x + 3200, 0])
        screen.blit(bg_img2, [x + 4800, 0])

        # 敵の更新と予告線・当たり判定処理
        for enemy in enemies:
            if enemy.warning_time > 0:
                enemy.draw_warning(screen)  # 予告線を描画
            else:
                enemy.update()
                if kk_rct.colliderect(enemy.rect):  # こうかとんと敵の衝突
                    print("Game Over!")  # 確認用
                    return
                if enemy.rect.right < 0:  # 画面外に出た敵を削除
                    enemies.remove(enemy)

        # キャラクターの描画
        screen.blit(kk_img, kk_rct)

        # ブロックの描画
        for block in blocks:
            pg.draw.rect(screen, (0, 255, 0), block)  # 緑色のブロック

        # 敵の描画
        for enemy in enemies:
            if enemy.warning_time <= 0:  # 予告線が終了した後に敵を描画
                enemy.draw(screen)

        pg.display.update()
        tmr += 10  # 背景スクロールの速度
        clock.tick(60)  # フレームレート設定

if __name__ == "__main__":
    pg.init()
    main()
    pg.quit()
    sys.exit()