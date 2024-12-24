import os
import sys
import time
import pygame as pg
import random

os.chdir(os.path.dirname(os.path.abspath(__file__)))

# 定数
WIDTH, HEIGHT = 800, 600  # 画面の幅と高さ
GRAVITY = 0.4  # 重力の強さ
JUMP_POWER = -11  # ジャンプの力
BLOCK_SPEED = 7  # ブロックの移動速度
NUM_BLOCKS = 3  # ブロックの数
BLOCK_INTERVAL = 350  # ブロック間の間隔
SPIKE_HEIGHT = 9  # トゲの高さ（赤い線の太さ）
ENEMY_SPEED = 13          # 敵の移動速度
ENEMY_WARNING_TIME = 120  # 予告線の表示時間
WARNING_FLASH_INTERVAL = 7  # 点滅の間隔
WARNING_ALPHA = 100  # 予告線の透明度（0〜255）

def SE(sound, vol=0.7):
    sound_effect = pg.mixer.Sound(sound)
    sound_effect.set_volume(vol)  # 音量を設定
    sound_effect.play()


def create_random_block(previous_x: int) -> tuple[pg.Rect, pg.Rect]:
    """
    ランダムにブロックを作成し、ブロックの下に赤い線（トゲ）をつける。
    引数:
        previous_x (int): 前のブロックの右端のX座標。
    戻り値:
        tuple[pg.Rect, pg.Rect]: ブロックの矩形、赤い線（トゲ）の矩形。
    """
    block_width = random.randint(100, 250)  # ブロックの幅をランダムに設定
    block_height = 20  # ブロックの高さ
    block_x = previous_x + BLOCK_INTERVAL  # ブロックのX座標を前のブロックから等間隔を開ける
    block_y = random.randint(HEIGHT - 450, HEIGHT - 200)  # ブロックのY座標をランダムに設定

    block = pg.Rect(block_x, block_y, block_width, block_height)  # ブロックの矩形を作成
    spike = pg.Rect(block_x, block_y + block_height, block_width, SPIKE_HEIGHT)  # ブロックの下に表示される赤い線(トゲの矩形)を作成
    return block, spike

def update_blocks(blocks: list[pg.Rect], spikes: list[pg.Rect]) -> None:
    """
    ブロックとトゲを移動させ、画面外になったら再生成する。
    引数:
        blocks (list[pg.Rect]): ブロックのリスト。
        spikes (list[pg.Rect]): トゲのリスト。
    """
    for i, block in enumerate(blocks):
        block.move_ip(-BLOCK_SPEED, 0)  # ブロックを左に移動
        spikes[i].move_ip(-BLOCK_SPEED, 0)  # トゲも左に移動
        if block.right < 0:  # ブロックが画面外に出たら
            blocks[i], spikes[i] = create_random_block(blocks[i - 1].right)  # 新しいブロックとトゲを作成

def check_collision(
    kk_rct: pg.Rect, vy: float, blocks: list[pg.Rect],
    jump_count: int, can_double_jump: bool
) -> tuple[float, bool, int, bool]:
    """
    「こうかとん」とブロック、トゲの衝突を判定。
    引数:
        kk_rct (pg.Rect): 「こうかとん」の矩形。
        vy (float): 縦方向の速度。
        blocks (list[pg.Rect]): ブロックのリスト。
        jump_count (int): 現在のジャンプ回数。
        can_double_jump (bool): ダブルジャンプが可能かどうか。
    戻り値:
        tuple[float, bool, int, bool]: 更新された速度、ブロック上の状態、ジャンプ回数、ダブルジャンプの可否。
    """
    on_block = False  # 「こうかとん」がブロック上にいるかどうか
    for i, block in enumerate(blocks):
        if kk_rct.colliderect(block):  # 「こうかとん」がブロックと衝突した場合
            if kk_rct.bottom - 10 <= block.top + 10:  # 「こうかとん」がブロックの上に乗っている場合
                kk_rct.bottom = block.top  # 「こうかとん」の底をブロックの頂点に合わせる
                vy = 0  
                on_block = True 
                jump_count = 0  
                can_double_jump = True  
            elif kk_rct.top+5 >= block.bottom:  # 「こうかとん」がブロックの下から衝突した場合
                pg.mixer.music.stop()
                SE("sound/clash.mp3", 1.5)
                time.sleep(0.5)
                SE("sound/scream.mp3", 1.5)
                time.sleep(2)
                print("ゲームオーバー")
                pg.quit()
                sys.exit()
            else:  # その他の衝突
                pg.mixer.music.stop()
                SE("sound/clash.mp3", 1.5)
                time.sleep(0.5)
                SE("sound/scream.mp3", 1.5)
                time.sleep(2)
                print("ゲームオーバー2")
                pg.quit()
                sys.exit()
    return vy, on_block, jump_count, can_double_jump


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
    pg.init()
    screen = pg.display.set_mode((WIDTH, HEIGHT))  
    clock = pg.time.Clock() 

    bg_img = pg.image.load("fig/pg_bg1.jpg")
    bg_img2 = pg.transform.flip(bg_img, True, False)
    kk_img = pg.transform.flip(pg.image.load("fig/3.png"), True, False)
    kk_rct = kk_img.get_rect(midbottom=(100, 200))

    blocks = [pg.Rect(0, 200, 100 + i * 300, 20) for i in range(NUM_BLOCKS)] #初期足場のリストを作成
    spikes = [pg.Rect(0, 200 + 20, 100 + i * 300, SPIKE_HEIGHT) for i in range(NUM_BLOCKS)] #初期足場に対応するトゲのリストを作成

    vy = 0  #初期速度
    tmr = 0  # タイマー
    can_double_jump = True  # ダブルジャンプの可否
    jump_count = 0  # ジャンプ回数

    alive = True

    pg.mixer.music.load("sound/BGM_MusMus.mp3")
    pg.mixer.music.set_volume(0.3)
    # 音楽をループ再生（-1は無限ループ）
    pg.mixer.music.play(-1)

    # 敵(ビーム)の初期化
    enemies = []  # 敵オブジェクトを格納するリスト
    enemy_spawn_timer = 0  # 敵生成タイマー

    while True:
        for event in pg.event.get():
            if event.type == pg.QUIT: 
                return
            elif event.type == pg.KEYDOWN:
                if event.key == pg.K_SPACE:  
                    if jump_count < 2:  
                        vy = JUMP_POWER
                        SE("sound/jump.mp3")
                        jump_count += 1

        vy += GRAVITY  
        kk_rct.move_ip(0, vy)  

        update_blocks(blocks, spikes)  # ブロックとトゲを更新
        # 衝突判定
        vy, on_block, jump_count, can_double_jump = check_collision(kk_rct, vy, blocks, jump_count, can_double_jump) 

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
        if kk_rct.top >= HEIGHT and alive == True:
            pg.mixer.music.stop()
            SE("sound/scream.mp3")
            alive = False
    
        for block in blocks:
            pg.draw.rect(screen, (0, 255, 0), block) 
        for spike in spikes:
            pg.draw.rect(screen, (255, 0, 0), spike)  

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