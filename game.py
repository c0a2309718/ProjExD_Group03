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

class MP:
    """
    生存時間に応じてMPを獲得するクラス
    1秒 = 1MP
    """
    def __init__(self):
        self.font = pg.font.Font(None, 50)
        self.color = (174, 0, 45)
        self.value = 0
        self.image = self.font.render(f"Score: {self.value}", 0, self.color)
        self.rect = self.image.get_rect()
        self.rect.center = 100, HEIGHT-50
        self.counter = 0

    def count(self):
        self.counter += 1
        if self.counter == 100:
            self.counter = 0
            self.value += 10

    def update(self, screen: pg.Surface):
        self.image = self.font.render(f"MP: {self.value}", 0, self.color)
        screen.blit(self.image, self.rect)


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
                SE("sound/danger.mp3", 0.2)
            else:
                self.flash_timer -= 1

            if self.flash_visible:  # 表示状態のときのみ予告線を描画
                # 半透明サーフェスを用意
                warning_surface = pg.Surface((WIDTH, 15), pg.SRCALPHA)
                warning_surface.fill((255, 0, 0, WARNING_ALPHA))  # 赤色で半透明
                screen.blit(warning_surface, (0, self.rect.y + self.rect.height // 2 - 5))  # 真ん中を通る予告線(-5で真ん中に調整)

            self.warning_time -= 1  # 表示時間を減少


class Fly(pg.sprite.Sprite):

    def __init__(self):
        self.counter = 0

    def flying(self, key_lst: list, mp: MP, vy: float):
        """
        滞空を操作する
        引数1:押されているキーのリスト
        """
        if self.counter > 0:
            self.counter -= 1
            return vy + GRAVITY
        if key_lst[pg.K_f]:
            if mp.value >= 1:
                mp.value -= 1
                return 0
            else:
                y = vy + GRAVITY
                return y
        else:
            y = vy + GRAVITY
            return y
        

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
    jump_count: int, can_double_jump: bool, screen, time_counter
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
                gameover(screen, time_counter)
                SE("sound/clash.mp3", 1.5)
                time.sleep(0.5)
                SE("sound/scream.mp3", 1.5)
                time.sleep(3)
                pg.quit()
                sys.exit()
            else:  # その他の衝突
                pg.mixer.music.stop()
                gameover(screen, time_counter)
                SE("sound/clash.mp3", 1.5)
                time.sleep(0.5)
                SE("sound/scream.mp3", 1.5)
                time.sleep(3)
                pg.quit()
                sys.exit()
    return vy, on_block, jump_count, can_double_jump
        


class Startkoukaton:
    """
    スタート画面のこうかとんと下線に関するクラス
    """
    img = pg.image.load("fig/2.png")  # こうかとんの画像
    img = pg.transform.scale(img, (40, 40))  # こうかとんを縮小
    sikaku = pg.Surface((WIDTH, HEIGHT))  # 下線Surfaceを生成
    pg.draw.rect(sikaku, (34, 139, 34), (360, 300, 130, 5))
    sikaku.set_colorkey((0, 0, 0))

    def __init__(self, xy: tuple[int, int]):
        """
        こうかとん画像Surfaceを生成する
        引数 xy：こうかとん画像の初期位置座標タプル
        """
        self.img = __class__.img
        self.sikaku = __class__.sikaku
        self.rct: pg.Rect = self.img.get_rect() #こうかとんrectを取得する
        self.rect: pg.Rect = self.sikaku.get_rect()  # 下線rectを取得する
        self.rct.center = xy  # こうかとんの初期座標
        self.rect.center = 365, 400  # 下線の初期座標

    def update(self, key_lst: list[bool], screen: pg.Surface):
        """
        押下キーに応じてこうかとんと下線を移動させる
        引数1 key_lst：押下キーの真理値リスト
        引数2 screen：画面Surface
        """
        if key_lst[pg.K_UP]:
            self.rct.center = 300, 385
            self.rect.center = 365, 400
        if key_lst[pg.K_DOWN]:
            self.rct.center = 300, 455
            self.rect.center = 365, 470
        screen.blit(self.img, self.rct)
        screen.blit(self.sikaku, self.rect)


def start(screen: pg.Surface) -> None:
    """
    ゲーム開始時に、スタート画面を表示する関数
    引数：screen
    """
    fonto1 = pg.font.SysFont("hgp創英角ﾎﾟｯﾌﾟ体", 50)
    fonto2 = pg.font.SysFont("hgp創英角ﾎﾟｯﾌﾟ体", 80)
    fonto3 = pg.font.SysFont("hgp創英角ﾎﾟｯﾌﾟ体", 25)
    txt1 = fonto1.render("駆けろ！", True, (50, 205, 50))
    txt1kage = fonto1.render("駆けろ！", True, (0, 0, 0))
    txt2 = fonto2.render("こうかとん", True, (50, 205, 50))
    txt2kage = fonto2.render("こうかとん", True, (0, 0, 0))
    sentaku1 = fonto3.render("ゲーム開始", True, (0, 0, 0))
    sentaku2 = fonto3.render("あそびかた", True, (0, 0, 0))
    botan = fonto3.render("＊スペースで決定", True, (0, 0, 0))
    
    screen.blit(txt1kage, [205, HEIGHT//2-130])
    screen.blit(txt1, [200, HEIGHT//2-135])
    screen.blit(txt2kage, [205, HEIGHT//2-75])
    screen.blit(txt2, [200, HEIGHT//2-80])
    screen.blit(sentaku1, [325, HEIGHT//2+70])
    screen.blit(sentaku2, [325, HEIGHT//2+140])
    screen.blit(botan, [280, HEIGHT//2+250])


def asobikata(screen: pg.Surface) -> None:
    """
    ゲームのルールや操作方法を表示する関数
    引数：screen
    """
    pg.draw.rect(screen, (224, 255, 255), (75, HEIGHT//2-275, 660, 250))
    pg.draw.rect(screen, (135, 206, 250), (80, HEIGHT//2-270, 650, 240))
    pg.draw.rect(screen, (224, 255, 255), (75, HEIGHT//2, 660, 230))
    pg.draw.rect(screen, (135, 206, 250), (80, HEIGHT//2+5, 650, 220))
    pg.draw.rect(screen, (224, 255, 255), (307, HEIGHT//2+242, 166, 46))
    pg.draw.rect(screen, (135, 206, 250), (310, HEIGHT//2+245, 160, 40))
    fonto1 = pg.font.SysFont("hgp創英角ﾎﾟｯﾌﾟ体", 35)
    fonto2 = pg.font.SysFont("hgp創英角ﾎﾟｯﾌﾟ体", 20)
    midasi1 = fonto1.render("＊ルール＊", True, (0, 0, 0))
    rule1 = fonto2.render("・ジャンプしてブロックを渡ろう", True, (0, 0, 0))
    rule2 = fonto2.render("・ブロックにぶつかったり落ちたらゲームオーバー", True, (0, 0, 0))
    rule3 = fonto2.render("・右側からくるビームに当たったらゲームオーバー", True, (0, 0, 0))
    midasi2 = fonto1.render("＊操作方法＊", True, (0, 0, 0))
    sousa1 = fonto2.render("・スペースでジャンプ（2段ジャンプまで）", True, (0, 0, 0))
    sousa2 = fonto2.render("・MPを消費してFキーを押し続けるとその場に浮遊し続ける", True, (0, 0, 0))
    modoru = fonto2.render("右シフトで戻る", True, (0, 0, 0))
    
    screen.blit(midasi1, [315, HEIGHT//2-265])
    screen.blit(rule1, [160, HEIGHT//2-180])
    screen.blit(rule2, [160, HEIGHT//2-140])
    screen.blit(rule3, [160, HEIGHT//2-100])
    screen.blit(midasi2, [305, HEIGHT//2+15])
    screen.blit(sousa1, [160, HEIGHT//2+100])
    screen.blit(sousa2, [160, HEIGHT//2+140])
    screen.blit(modoru, [320, HEIGHT//2+255])
    pg.display.update()



class Timecount:
    """
    タイムをカウントし表示するクラス
    """
    def __init__(self):
        self.font = pg.font.SysFont("hgp創英角ﾎﾟｯﾌﾟ体", 40)
        self.color = (255, 255, 255)
        self.start_ticks = pg.time.get_ticks()
        self.final_time = 0

    def update(self, screen):
        """
        経過時間を計算し、画面に表示する
        """
        elapsed_time = (pg.time.get_ticks() - self.start_ticks) / 1000
        self.final_time = elapsed_time  # ゲームオーバー時に最終タイムを記録
        time_surface = self.font.render(f"Time: {elapsed_time:.2f} 秒", True, self.color)
        screen.blit(time_surface, (10, 10))


def gameover(screen, time_counter):
    """
    ゲームオーバー画面を表示する関数
    """
    overlay = pg.Surface((WIDTH, HEIGHT))
    overlay.set_alpha(180)  # 透明度を設定
    overlay.fill((0, 0, 0))  # 黒色で塗りつぶす
    screen.blit(overlay, (0, 0))

    font = pg.font.SysFont("hgp創英角ﾎﾟｯﾌﾟ体", 72)
    gameover_text = font.render("Game Over", True, (255, 0, 0))
    text_rect = gameover_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 50))
    screen.blit(gameover_text, text_rect)

    font_small = pg.font.SysFont("hgp創英角ﾎﾟｯﾌﾟ体", 48)
    time_text = font_small.render(f"Time: {time_counter.final_time:.2f} 秒", True, (255, 255, 255))
    time_rect = time_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 20))
    screen.blit(time_text, time_rect)
    pg.display.update()

def main():
    pg.init()
    screen = pg.display.set_mode((WIDTH, HEIGHT))
    clock = pg.time.Clock()
    mp = MP()
    fly = Fly()
    
    # 画像読み込み
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

    stbird = Startkoukaton((300, 385))
    scene = 0  # 画面の切り替え判定 0:スタート画面, 1:ゲーム画面, 2:遊び方画面
    sentaku = 0  # 選択肢の切り替え判定
    
    font = pg.font.Font(None, 40)  # デフォルトフォント、サイズ50
    text = font.render("BGM:MusMus", True, (255, 255, 255))  # テキストを描画（白色）
    
    while True:
        key_lst = pg.key.get_pressed()
        # スタート画面
        if scene == 0:
            for event in pg.event.get():
                if event.type == pg.QUIT: 
                    return
            screen.blit(bg_img, [0, 0])  # 背景画像を表示
            start(screen)
            stbird.update(key_lst, screen)
            pg.display.update()
            if key_lst[pg.K_UP]:
                sentaku = 0  # ゲーム開始を選択
            if key_lst[pg.K_DOWN]:
                sentaku = 1  # あそびかたを選択
            if key_lst[pg.K_SPACE]:  # スペースキーで決定
                if sentaku == 0:
                    scene = 1  # ゲーム画面へ移動
                    # タイムカウントクラスのインスタンス作成
                    time_counter = Timecount()
                if sentaku == 1:
                    scene = 2  # あそびかた画面へ移動

        # あそびかた画面
        elif scene == 2:
            for event in pg.event.get():
                if event.type == pg.QUIT: 
                    return
            screen.blit(bg_img, [0, 0])  # 背景画像を表示
            asobikata(screen)
            if key_lst[pg.K_RSHIFT]:
                scene = 0  # スタート画面へ移動

        # ゲーム画面
        elif scene == 1:
            for event in pg.event.get():
                if event.type == pg.QUIT: 
                    return
                elif event.type == pg.KEYDOWN:      
                    if event.key == pg.K_SPACE: 
                        if jump_count < 2:  
                            vy = JUMP_POWER
                            SE("sound/jump.mp3")
                            fly.counter = 10
                            jump_count += 1
            
            vy = fly.flying(key_lst, mp, vy)
            kk_rct.move_ip(0, vy)  

            update_blocks(blocks, spikes)  # ブロックとトゲを更新
            # 衝突判定
            vy, on_block, jump_count, can_double_jump = check_collision(kk_rct, vy, blocks, jump_count, can_double_jump, screen, time_counter) 

            # 敵の生成処理
            enemy_spawn_timer -= 1
            if enemy_spawn_timer <= 0:  # 一定時間経過後に敵を生成
                enemies.append(Enemy())
                enemy_spawn_timer = random.randint(120, 240)  # 次の敵出現タイマー(敵出現頻度を変えるならここ)

            # 敵の更新と予告線・当たり判定処理
            for enemy in enemies:
                if enemy.warning_time > 0:
                    enemy.draw_warning(screen)  # 予告線を描画
                else:
                    enemy.update()
                    if kk_rct.colliderect(enemy.rect):  # こうかとんと敵の衝突
                        pg.mixer.music.stop()
                        gameover(screen, time_counter)
                        SE("sound/exp.mp3", 1)
                        time.sleep(3)
                        return
                    if enemy.rect.right < 0:  # 画面外に出た敵を削除
                        enemies.remove(enemy)

            # キャラクターの描画
            screen.blit(kk_img, kk_rct)
            if kk_rct.top >= HEIGHT+20 and alive == True:
                gameover(screen, time_counter)
                pg.mixer.music.stop()
                SE("sound/scream.mp3", 1.5)
                alive = False
                time.sleep(3)
                return

            for block in blocks:
                pg.draw.rect(screen, (0, 255, 0), block) 
            for spike in spikes:
                pg.draw.rect(screen, (255, 0, 0), spike)  

            # 敵の描画
            for enemy in enemies:
                if enemy.warning_time <= 0:  # 予告線が終了した後に敵を描画
                    enemy.draw(screen)

            mp.count()
            mp.update(screen)
            # タイムの表示
            time_counter.update(screen)  
            pg.display.update()
            tmr += 10  # 背景スクロールの速度
            clock.tick(60)  # フレームレート設定

            # 背景スクロール
            x = -(tmr % 3200)
            screen.blit(bg_img, [x, 0])
            screen.blit(bg_img2, [x + 1600, 0])
            screen.blit(bg_img, [x + 3200, 0])
            screen.blit(bg_img2, [x + 4800, 0])

            screen.blit(text, (WIDTH-200, HEIGHT-40))

if __name__ == "__main__":
    pg.init()
    main()
    pg.quit()
    sys.exit()