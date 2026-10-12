#!/usr/bin/env python3
"""
wa_wa_engine.py — FILES=off single-file game engine

WA WA ENGINE — a tiny Mario Maker-style editor with three style packs:
  * MINECRAFT   (blocks, grass, dirt, stone)
  * EARTHBOUND  (SNES JRPG overworld tiles)
  * SMB3        (Super Mario Bros. 3 style blocks)

Everything drawn procedurally in pygame. No PNG/JPG/sprite sheets.
No internet. No subprocesses. One .py, one window, ~60 FPS.

Python 3.14+ / pygame-ce
[C] Fan meme tribute, 2026 — FILES=off demo
Minecraft (C) Mojang. EarthBound (C) Nintendo / HAL. SMB3 (C) Nintendo.
"""
import os, sys, math, random, json
os.environ.setdefault("PYGAME_HIDE_SUPPORT_PROMPT", "1")
try:
    import pygame
except ImportError:
    print("pip install pygame-ce", file=sys.stderr); sys.exit(1)

# ---------------------------------------------------------------- constants
W, H = 1024, 640
FPS = 60
TILE = 32
GRID_W, GRID_H = 24, 14         # visible edit area
PALETTE_TILES = 10

BLACK   = (18, 18, 24)
WHITE   = (240, 240, 240)
GRAY    = (110, 110, 120)
GRAY_DK = (60, 60, 70)
GRAY_LT = (180, 180, 190)
UI_BG   = (30, 30, 44)
UI_PANEL= (44, 44, 60)
UI_HI   = (90, 90, 120)
UI_TEXT = (230, 230, 240)
UI_ACC  = (250, 200, 60)

# --- Minecraft pack ---
MC_GRASS_TOP = (95, 159, 53)
MC_GRASS_SIDE= (134, 96, 67)
MC_DIRT      = (134, 96, 67)
MC_DIRT_DK   = (110, 78, 52)
MC_STONE     = (128, 128, 128)
MC_STONE_DK  = (100, 100, 100)
MC_WOOD      = (156, 112, 66)
MC_WOOD_DK   = (120, 84, 48)
MC_LEAF      = (60, 130, 60)
MC_LEAF_DK   = (40, 100, 40)
MC_SAND      = (219, 207, 163)
MC_SAND_DK   = (190, 178, 130)
MC_WATER     = (60, 100, 200)
MC_WATER_DK  = (40, 70, 160)
MC_LAVA      = (220, 90, 30)
MC_LAVA_DK   = (160, 60, 20)
MC_PLANK     = (170, 130, 80)

# --- EarthBound pack ---
EB_GRASS     = (110, 180, 90)
EB_GRASS_DK  = (80, 150, 60)
EB_DIRT      = (190, 140, 90)
EB_DIRT_DK   = (150, 110, 70)
EB_PATH      = (220, 200, 160)
EB_PATH_DK   = (180, 160, 120)
EB_WATER     = (60, 140, 220)
EB_WATER_DK  = (40, 100, 180)
EB_TREE      = (50, 100, 50)
EB_TREE_DK   = (30, 70, 30)
EB_HOUSE     = (220, 190, 140)
EB_HOUSE_DK  = (170, 140, 90)
EB_ROOF      = (200, 80, 80)
EB_ROOF_DK   = (150, 50, 50)
EB_FLOWER    = (250, 220, 100)
EB_SIGN      = (180, 130, 80)

# --- SMB3 pack ---
SMB_GND_TOP  = (220, 130, 60)
SMB_GND      = (200, 100, 40)
SMB_GND_DK   = (150, 70, 20)
SMB_BRICK    = (200, 90, 30)
SMB_BRICK_DK = (140, 60, 20)
SMB_QBLOCK   = (250, 200, 60)
SMB_QBLOCK_DK= (200, 150, 40)
SMB_USED     = (170, 120, 60)
SMB_PIPE     = (60, 180, 80)
SMB_PIPE_DK  = (40, 130, 60)
SMB_CLOUD    = (250, 250, 250)
SMB_CLOUD_DK = (200, 200, 210)
SMB_BUSH     = (60, 160, 60)

# ---------------------------------------------------------------- tile packs
# Each pack is a list of (id, display_name, draw_fn)
# draw_fn(surface, x, y, size)

def _frame(s, x, y, sz, col, col_dk=None, border=True):
    s.fill(col, (x, y, sz, sz))
    if col_dk and border:
        pygame.draw.rect(s, col_dk, (x, y, sz, sz), 2)

def draw_mc_grass(s, x, y, sz):
    _frame(s, x, y, sz, MC_GRASS_SIDE)
    s.fill(MC_GRASS_TOP, (x, y, sz, sz // 3))
    for i in range(0, sz, 4):
        s.set_at((x + i, y + sz // 3), MC_GRASS_TOP)

def draw_mc_dirt(s, x, y, sz):
    _frame(s, x, y, sz, MC_DIRT)
    for _ in range(6):
        px = x + random.randint(2, sz - 3)
        py = y + random.randint(2, sz - 3)
        s.set_at((px, py), MC_DIRT_DK)

def draw_mc_stone(s, x, y, sz):
    _frame(s, x, y, sz, MC_STONE)
    for _ in range(8):
        px = x + random.randint(2, sz - 3)
        py = y + random.randint(2, sz - 3)
        s.set_at((px, py), MC_STONE_DK)

def draw_mc_wood(s, x, y, sz):
    _frame(s, x, y, sz, MC_WOOD)
    s.fill(MC_WOOD_DK, (x, y, sz, 3))
    s.fill(MC_WOOD_DK, (x, y + sz - 3, sz, 3))
    s.fill(MC_WOOD_DK, (x + sz // 2 - 1, y, 2, sz))

def draw_mc_leaf(s, x, y, sz):
    _frame(s, x, y, sz, MC_LEAF)
    for _ in range(10):
        px = x + random.randint(2, sz - 3)
        py = y + random.randint(2, sz - 3)
        s.set_at((px, py), MC_LEAF_DK)

def draw_mc_sand(s, x, y, sz):
    _frame(s, x, y, sz, MC_SAND)
    for _ in range(6):
        px = x + random.randint(2, sz - 3)
        py = y + random.randint(2, sz - 3)
        s.set_at((px, py), MC_SAND_DK)

def draw_mc_water(s, x, y, sz):
    _frame(s, x, y, sz, MC_WATER)
    s.fill(MC_WATER_DK, (x, y + sz - 4, sz, 2))

def draw_mc_lava(s, x, y, sz):
    _frame(s, x, y, sz, MC_LAVA)
    s.fill(MC_LAVA_DK, (x, y + sz - 4, sz, 2))

def draw_mc_plank(s, x, y, sz):
    _frame(s, x, y, sz, MC_PLANK)
    s.fill(MC_WOOD_DK, (x, y + sz // 2 - 1, sz, 2))

def draw_mc_empty(s, x, y, sz):
    pass

def draw_eb_grass(s, x, y, sz):
    _frame(s, x, y, sz, EB_GRASS)
    for _ in range(6):
        px = x + random.randint(2, sz - 3)
        py = y + random.randint(2, sz - 3)
        s.set_at((px, py), EB_GRASS_DK)

def draw_eb_dirt(s, x, y, sz):
    _frame(s, x, y, sz, EB_DIRT)
    for _ in range(4):
        px = x + random.randint(2, sz - 3)
        py = y + random.randint(2, sz - 3)
        s.set_at((px, py), EB_DIRT_DK)

def draw_eb_path(s, x, y, sz):
    _frame(s, x, y, sz, EB_PATH)
    for _ in range(4):
        px = x + random.randint(2, sz - 3)
        py = y + random.randint(2, sz - 3)
        s.set_at((px, py), EB_PATH_DK)

def draw_eb_water(s, x, y, sz):
    _frame(s, x, y, sz, EB_WATER)
    s.fill(EB_WATER_DK, (x, y + sz - 4, sz, 2))

def draw_eb_tree(s, x, y, sz):
    _frame(s, x, y, sz, EB_TREE)
    s.fill(EB_TREE_DK, (x + sz // 2 - 2, y + sz - 6, 4, 6))

def draw_eb_house(s, x, y, sz):
    _frame(s, x, y, sz, EB_HOUSE)
    s.fill(EB_HOUSE_DK, (x, y + sz - 4, sz, 4))

def draw_eb_roof(s, x, y, sz):
    _frame(s, x, y, sz, EB_ROOF)
    s.fill(EB_ROOF_DK, (x, y + sz - 4, sz, 4))

def draw_eb_flower(s, x, y, sz):
    _frame(s, x, y, sz, EB_GRASS)
    pygame.draw.circle(s, EB_FLOWER, (x + sz // 2, y + sz // 2), sz // 4)

def draw_eb_sign(s, x, y, sz):
    _frame(s, x, y, sz, EB_SIGN)
    s.fill(EB_DIRT_DK, (x + 2, y + 2, sz - 4, 2))

def draw_eb_empty(s, x, y, sz):
    pass

def draw_smb_ground(s, x, y, sz):
    _frame(s, x, y, sz, SMB_GND)
    s.fill(SMB_GND_TOP, (x, y, sz, 3))
    s.fill(SMB_GND_DK, (x, y + sz - 3, sz, 3))

def draw_smb_brick(s, x, y, sz):
    _frame(s, x, y, sz, SMB_BRICK)
    s.fill(SMB_BRICK_DK, (x, y + sz // 2 - 1, sz, 2))
    s.fill(SMB_BRICK_DK, (x + sz // 2 - 1, y, 2, sz))

def draw_smb_qblock(s, x, y, sz):
    _frame(s, x, y, sz, SMB_QBLOCK)
    s.fill(SMB_QBLOCK_DK, (x + 3, y + 3, sz - 6, 2))
    s.fill(SMB_QBLOCK_DK, (x + 3, y + sz - 5, sz - 6, 2))

def draw_smb_used(s, x, y, sz):
    _frame(s, x, y, sz, SMB_USED)

def draw_smb_pipe(s, x, y, sz):
    _frame(s, x, y, sz, SMB_PIPE)
    s.fill(SMB_PIPE_DK, (x, y, 4, sz))
    s.fill(SMB_PIPE_DK, (x + sz - 4, y, 4, sz))

def draw_smb_cloud(s, x, y, sz):
    s.fill(SKY_BLUE, (x, y, sz, sz))
    pygame.draw.circle(s, SMB_CLOUD, (x + sz // 2, y + sz // 2), sz // 3)
    pygame.draw.circle(s, SMB_CLOUD_DK, (x + sz // 2, y + sz // 2), sz // 3, 1)

def draw_smb_bush(s, x, y, sz):
    s.fill(SKY_BLUE, (x, y, sz, sz))
    pygame.draw.circle(s, SMB_BUSH, (x + sz // 2, y + sz // 2), sz // 3)

def draw_smb_empty(s, x, y, sz):
    pass

SKY_BLUE = (107, 178, 250)

# Tiles: (id, name, draw_fn, solid)
MC_TILES = [
    ("Empty",   draw_mc_empty,  False),
    ("Grass",   draw_mc_grass,  True),
    ("Dirt",    draw_mc_dirt,   True),
    ("Stone",   draw_mc_stone,  True),
    ("Wood",    draw_mc_wood,   True),
    ("Leaf",    draw_mc_leaf,   False),
    ("Sand",    draw_mc_sand,   True),
    ("Water",   draw_mc_water,  False),
    ("Lava",    draw_mc_lava,   False),
    ("Plank",   draw_mc_plank,  True),
]
EB_TILES = [
    ("Empty",   draw_eb_empty,  False),
    ("Grass",   draw_eb_grass,  False),
    ("Dirt",    draw_eb_dirt,   False),
    ("Path",    draw_eb_path,   False),
    ("Water",   draw_eb_water,  False),
    ("Tree",    draw_eb_tree,   True),
    ("House",   draw_eb_house,  True),
    ("Roof",    draw_eb_roof,   False),
    ("Flower",  draw_eb_flower, False),
    ("Sign",    draw_eb_sign,   False),
]
SMB_TILES = [
    ("Empty",   draw_smb_empty, False),
    ("Ground",  draw_smb_ground,True),
    ("Brick",   draw_smb_brick, True),
    ("? Block", draw_smb_qblock,True),
    ("Used",    draw_smb_used,  True),
    ("Pipe",    draw_smb_pipe,  True),
    ("Cloud",   draw_smb_cloud, False),
    ("Bush",    draw_smb_bush,  False),
    ("Ground2", draw_smb_ground,True),
    ("Brick2",  draw_smb_brick, True),
]

PACKS = [
    ("MINECRAFT", MC_TILES, MC_SKY if False else (110, 160, 220)),
    ("EARTHBOUND", EB_TILES, (60, 120, 200)),
    ("SMB3", SMB_TILES, SKY_BLUE),
]

# ---------------------------------------------------------------- world model
class World:
    def __init__(self, w, h):
        self.w = w
        self.h = h
        self.grid = [[0] * w for _ in range(h)]  # tile id per cell
        self.pack = 0
    def set(self, x, y, tid):
        if 0 <= x < self.w and 0 <= y < self.h:
            self.grid[y][x] = tid
    def get(self, x, y):
        if 0 <= x < self.w and 0 <= y < self.h:
            return self.grid[y][x]
        return 0

# ---------------------------------------------------------------- UI layout
VIEW_X, VIEW_Y = 200, 60
VIEW_W, VIEW_H = GRID_W * TILE, GRID_H * TILE     # 768 x 448
VIEW_RECT = pygame.Rect(VIEW_X, VIEW_Y, VIEW_W, VIEW_H)

PALETTE_X = 10
PALETTE_Y = 60
PALETTE_W = 180
PALETTE_H = GRID_H * TILE
PALETTE_RECT = pygame.Rect(PALETTE_X, PALETTE_Y, PALETTE_W, PALETTE_H)

TOOLBAR_H = 40
TOOLBAR_RECT = pygame.Rect(0, H - TOOLBAR_H, W, TOOLBAR_H)

# ---------------------------------------------------------------- engine
class WaWaEngine:
    def __init__(self):
        pygame.init()
        try:
            pygame.mixer.init(22050, -16, 1, 256)
        except Exception:
            pass
        self.screen = pygame.display.set_mode((W, H))
        pygame.display.set_caption("WA WA ENGINE — FILES=off")
        self.clock = pygame.time.Clock()
        self.font_sm = pygame.font.Font(None, 20)
        self.font_md = pygame.font.Font(None, 24)
        self.font_lg = pygame.font.Font(None, 32)
        self.font_xl = pygame.font.Font(None, 64)
        self.world = World(GRID_W, GRID_H)
        self.pack_idx = 0
        self.selected_tile = 0
        self.mode = "edit"           # edit | play
        self.player_x = 2.0
        self.player_y = 2.0
        self.player_vx = 0.0
        self.player_vy = 0.0
        self.player_on_ground = False
        self.running = True
        self._tile_cache = {}
        self._rebuild_tile_cache()
        # chomp beep for place
        self._place_beep = self._make_beep(440, 0.03, 4000)
        self._jump_beep  = self._make_beep(720, 0.05, 5000)

    def _make_beep(self, freq, dur, amp):
        try:
            import array
            if not pygame.mixer.get_init(): return None
            buf = array.array("h")
            for i in range(int(22050 * dur)):
                buf.append(int(amp * math.sin(2 * math.pi * freq * i / 22050)))
            return pygame.mixer.Sound(buffer=buf)
        except Exception:
            return None

    def _rebuild_tile_cache(self):
        self._tile_cache.clear()
        for pname, tiles, _sky in PACKS:
            for tid, (tname, dfn, solid) in enumerate(tiles):
                surf = pygame.Surface((TILE, TILE))
                dfn(surf, 0, 0, TILE)
                self._tile_cache[(pname, tid)] = surf

    @property
    def current_pack(self):
        return PACKS[self.pack_idx]

    @property
    def current_sky(self):
        return self.current_pack[2]

    @property
    def current_tiles(self):
        return self.current_pack[1]

    def tile_surface(self, pack_name, tid):
        return self._tile_cache.get((pack_name, tid))

    def is_solid(self, tx, ty):
        tid = self.world.get(tx, ty)
        if tid == 0: return False
        try:
            return self.current_tiles[tid][2]
        except Exception:
            return False

    def grid_to_screen(self, gx, gy):
        return VIEW_X + gx * TILE, VIEW_Y + gy * TILE

    def screen_to_grid(self, sx, sy):
        if not VIEW_RECT.collidepoint(sx, sy): return None
        return (sx - VIEW_X) // TILE, (sy - VIEW_Y) // TILE

    # ------------------------------------------------ input
    def handle_event(self, e):
        if e.type == pygame.QUIT:
            self.running = False
        elif e.type == pygame.KEYDOWN:
            if e.key == pygame.K_ESCAPE:
                if self.mode == "play":
                    self.mode = "edit"
                else:
                    self.running = False
            elif e.key == pygame.K_TAB:
                self.pack_idx = (self.pack_idx + 1) % len(PACKS)
                self.selected_tile = 0
            elif e.key == pygame.K_RETURN:
                if self.mode == "edit":
                    self.mode = "play"
                    self.player_x, self.player_y = 2.0, 2.0
                    self.player_vx = self.player_vy = 0.0
                else:
                    self.mode = "edit"
            elif e.key == pygame.K_c and self.mode == "edit":
                self.world.grid = [[0] * self.world.w for _ in range(self.world.h)]
            elif e.key == pygame.K_f and self.mode == "edit":
                # fill bottom row with ground
                for gx in range(self.world.w):
                    self.world.set(gx, self.world.h - 1, 1)
        elif e.type == pygame.MOUSEBUTTONDOWN:
            mx, my = e.pos
            if self.mode == "edit":
                if PALETTE_RECT.collidepoint(mx, my):
                    idx = (my - PALETTE_Y) // TILE
                    if 0 <= idx < len(self.current_tiles):
                        self.selected_tile = idx
                elif VIEW_RECT.collidepoint(mx, my):
                    g = self.screen_to_grid(mx, my)
                    if g:
                        if e.button == 1:
                            self.world.set(g[0], g[1], self.selected_tile)
                            if self._place_beep: self._place_beep.play()
                        elif e.button == 3:
                            self.world.set(g[0], g[1], 0)
            elif self.mode == "play":
                self.mode = "edit"
        elif e.type == pygame.MOUSEMOTION:
            if self.mode == "edit" and e.buttons[0]:
                g = self.screen_to_grid(*e.pos)
                if g:
                    self.world.set(g[0], g[1], self.selected_tile)
            elif self.mode == "edit" and e.buttons[2]:
                g = self.screen_to_grid(*e.pos)
                if g:
                    self.world.set(g[0], g[1], 0)

    # ------------------------------------------------ play physics
    def update_play(self, dt):
        keys = pygame.key.get_pressed()
        speed = 6.0
        accel = 40.0
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.player_vx -= accel * dt
        elif keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.player_vx += accel * dt
        else:
            self.player_vx *= max(0.0, 1.0 - 12.0 * dt)
        self.player_vx = max(-speed, min(speed, self.player_vx))
        on_ground = self.player_on_ground
        if (keys[pygame.K_SPACE] or keys[pygame.K_UP] or keys[pygame.K_w]) and on_ground:
            self.player_vy = -12.0
            on_ground = False
            if self._jump_beep: self._jump_beep.play()
        self.player_vy += 30.0 * dt
        if self.player_vy > 20: self.player_vy = 20

        # move X
        nx = self.player_x + self.player_vx * dt
        if self._can_move(nx, self.player_y):
            self.player_x = nx
        else:
            self.player_vx = 0
        # move Y
        ny = self.player_y + self.player_vy * dt
        if self._can_move(self.player_x, ny):
            self.player_y = ny
            self.player_on_ground = False
        else:
            if self.player_vy > 0:
                self.player_on_ground = True
            self.player_vy = 0

    def _can_move(self, x, y):
        # player is 0.8 x 1.0 tiles, top-left anchored
        pw, ph = 0.8, 1.0
        x0, y0 = int(x), int(y)
        x1, y1 = int(x + pw - 0.001), int(y + ph - 0.001)
        for ty in range(y0, y1 + 1):
            for tx in range(x0, x1 + 1):
                if self.is_solid(tx, ty):
                    return False
        return True

    # ------------------------------------------------ draw
    def draw_edit(self):
        s = self.screen
        s.fill(UI_BG)
        # top bar
        pygame.draw.rect(s, UI_PANEL, (0, 0, W, 50))
        title = self.font_lg.render("WA WA ENGINE", True, UI_ACC)
        s.blit(title, (14, 10))
        pack_name = self.current_pack[0]
        pack_img = self.font_md.render(f"PACK: {pack_name}   [TAB] cycle", True, UI_TEXT)
        s.blit(pack_img, (230, 16))
        hint = self.font_sm.render("LMB paint  RMB erase  [C] clear  [F] fill ground  [ENTER] play  [ESC] quit",
                                    True, UI_TEXT)
        s.blit(hint, (700 - hint.get_width() // 2 + 160, 18))
        # palette
        pygame.draw.rect(s, UI_PANEL, PALETTE_RECT)
        pygame.draw.rect(s, UI_HI, PALETTE_RECT, 2)
        for i, (tname, dfn, solid) in enumerate(self.current_tiles):
            py = PALETTE_Y + i * TILE
            if py + TILE > PALETTE_Y + PALETTE_H: break
            # selected highlight
            if i == self.selected_tile:
                pygame.draw.rect(s, UI_ACC, (PALETTE_X + 2, py + 2, TILE - 4, TILE - 4), 2)
            surf = self.tile_surface(pack_name, i)
            if surf: s.blit(surf, (PALETTE_X + 4, py + 4))
        # canvas
        pygame.draw.rect(s, self.current_sky, VIEW_RECT)
        for gy in range(GRID_H):
            for gx in range(GRID_W):
                tid = self.world.get(gx, gy)
                if tid:
                    surf = self.tile_surface(pack_name, tid)
                    if surf:
                        s.blit(surf, (VIEW_X + gx * TILE, VIEW_Y + gy * TILE))
        pygame.draw.rect(s, UI_HI, VIEW_RECT, 2)
        # grid lines
        for gx in range(GRID_W + 1):
            pygame.draw.line(s, (50, 50, 70), (VIEW_X + gx * TILE, VIEW_Y),
                             (VIEW_X + gx * TILE, VIEW_Y + VIEW_H), 1)
        for gy in range(GRID_H + 1):
            pygame.draw.line(s, (50, 50, 70), (VIEW_X, VIEW_Y + gy * TILE),
                             (VIEW_X + VIEW_W, VIEW_Y + gy * TILE), 1)

        # bottom toolbar
        pygame.draw.rect(s, UI_PANEL, TOOLBAR_RECT)
        pygame.draw.rect(s, UI_HI, TOOLBAR_RECT, 2)
        tip = self.font_md.render("WA WA ENGINE — FILES=off — procedurally drawn — pygame-ce",
                                   True, UI_TEXT)
        s.blit(tip, (W // 2 - tip.get_width() // 2, H - TOOLBAR_H + 10))

    def draw_play(self):
        s = self.screen
        s.fill(self.current_sky)
        pack_name = self.current_pack[0]
        for gy in range(GRID_H):
            for gx in range(GRID_W):
                tid = self.world.get(gx, gy)
                if tid:
                    surf = self.tile_surface(pack_name, tid)
                    if surf:
                        s.blit(surf, (VIEW_X + gx * TILE, VIEW_Y + gy * TILE))
        # player — WA WA guy
        px, py = self.grid_to_screen(self.player_x, self.player_y)
        pygame.draw.rect(s, (250, 200, 60), (px + 4, py + 4, TILE - 8, TILE - 8))
        pygame.draw.rect(s, BLACK, (px + 8, py + 10, 4, 4))
        pygame.draw.rect(s, BLACK, (px + 20, py + 10, 4, 4))
        pygame.draw.rect(s, BLACK, (px + 10, py + 22, 12, 3))
        # overlay
        bar = pygame.Surface((W, 40)); bar.set_alpha(180); bar.fill(BLACK)
        s.blit(bar, (0, 0))
        info = self.font_md.render("[PLAY]  ARROWS/WASD move  SPACE jump  ESC/ENTER to edit",
                                   True, WHITE)
        s.blit(info, (14, 10))

    def draw(self):
        if self.mode == "edit":
            self.draw_edit()
        else:
            self.draw_play()
        pygame.display.flip()

    def run(self):
        while self.running:
            dt = self.clock.tick(FPS) / 1000.0
            for e in pygame.event.get():
                self.handle_event(e)
            if self.mode == "play":
                self.update_play(dt)
            self.draw()
        pygame.quit()
        return 0


if __name__ == "__main__":
    raise SystemExit(WaWaEngine().run())