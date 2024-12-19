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


class Startkoukaton:

    img = pg.image.load("fig/2.png")
    img = pg.transform.scale(img, (40, 40))
    sikaku = pg.Surface((WIDTH, HEIGHT))
    pg.draw.rect(sikaku, (34, 139, 34), (360, 300, 130, 5))
    sikaku.set_colorkey((0, 0, 0))

    def __init__(self, xy: tuple[int, int]):
        self.img = __class__.img
        self.sikaku = __class__.sikaku
        self.rct: pg.Rect = self.img.get_rect() #こうかとんrectを取得する
        self.rect: pg.Rect = self.sikaku.get_rect()  # 下線rectを取得する
        self.rct.center = xy  # こうかとんの初期座標
        self.rect.center = 365, 400  # 下線の初期座標

    def update(self, key_lst: list[bool], screen: pg.Surface):
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
    txt1 = fonto1.render("翔けろ！", True, (50, 205, 50))
    txt1kage = fonto1.render("翔けろ！", True, (0, 0, 0))
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
    pg.draw.rect(screen, (224, 255, 255), (337, HEIGHT//2+242, 166, 46))
    pg.draw.rect(screen, (135, 206, 250), (340, HEIGHT//2+245, 160, 40))
    fonto1 = pg.font.SysFont("hgp創英角ﾎﾟｯﾌﾟ体", 35)
    fonto2 = pg.font.SysFont("hgp創英角ﾎﾟｯﾌﾟ体", 20)
    midasi1 = fonto1.render("＊ルール＊", True, (0, 0, 0))
    rule11 = fonto2.render("・こうかとんを操作して、ブロックに飛び移りながら進もう", True, (0, 0, 0))
    rule2 = fonto2.render("・こうかとんが地面についたらゲームオーバー", True, (0, 0, 0))
    midasi2 = fonto1.render("＊操作方法＊", True, (0, 0, 0))
    sousa1 = fonto2.render("・スペースでジャンプ", True, (0, 0, 0))
    modoru = fonto2.render("右シフトで戻る", True, (0, 0, 0))
    
    screen.blit(midasi1, [315, HEIGHT//2-265])
    screen.blit(rule11, [100, HEIGHT//2-200])
    screen.blit(rule2, [100, HEIGHT//2-160])
    screen.blit(midasi2, [305, HEIGHT//2+15])
    screen.blit(sousa1, [305, HEIGHT//2+80])
    screen.blit(modoru, [350, HEIGHT//2+255])
    pg.display.update()


def main():
    pg.display.set_caption("翔けろ！こうかとん")
    screen = pg.display.set_mode((WIDTH, HEIGHT))
    clock = pg.time.Clock()

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

    stbird = Startkoukaton((300, 385))
    scene = 0  # 画面の切り替え判定
    sentaku = 0  # 選択肢の切り替え判定
    tmr = 0
    while True:
        for event in pg.event.get():
            if event.type == pg.QUIT:
                return

        # キー入力の取得
        key_lst = pg.key.get_pressed()

        # スタート画面
        if scene == 0:
            screen.blit(bg_img, [0, 0])
            start(screen)
            stbird.update(key_lst, screen)
            pg.display.update()
            if key_lst[pg.K_UP]:
                sentaku = 0
            if key_lst[pg.K_DOWN]:
                sentaku = 1
            if key_lst[pg.K_SPACE]:
                if sentaku == 0:
                    scene = 1
                if sentaku == 1:
                    scene = 2


        # あそびかた画面
        if scene == 2:
            screen.blit(bg_img, [0, 0])
            asobikata(screen)
            if key_lst[pg.K_RSHIFT]:
                scene = 0
        
        # ゲーム画面
        if scene == 1:
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