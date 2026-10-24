
import pygame
import random

pygame.init()

CELL = 30
COLS, ROWS = 10, 20
WIDTH, HEIGHT = COLS * CELL, ROWS * CELL
FPS = 60

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("TETRIS")
clock = pygame.time.Clock()

font = pygame.font.SysFont("consolas", 22, bold=True)
small_font = pygame.font.SysFont("consolas", 16)
big_font = pygame.font.SysFont("consolas", 32, bold=True)

BG = (18, 20, 30)
GRID = (43, 46, 62)
WHITE = (240, 242, 250)

SHAPES = [
    ([(0, 1), (1, 1), (2, 1), (3, 1)], (65, 220, 235)),
    ([(0, 0), (0, 1), (1, 1), (2, 1)], (75, 105, 235)),
    ([(2, 0), (0, 1), (1, 1), (2, 1)], (240, 155, 65)),
    ([(1, 0), (2, 0), (1, 1), (2, 1)], (245, 220, 75)),
    ([(1, 0), (2, 0), (0, 1), (1, 1)], (90, 220, 120)),
    ([(1, 0), (0, 1), (1, 1), (2, 1)], (185, 100, 235)),
    ([(0, 0), (1, 0), (1, 1), (2, 1)], (235, 85, 105)),
]


def new_piece():
    shape, color = random.choice(SHAPES)
    return {
        "shape": shape[:],
        "color": color,
        "x": COLS // 2 - 2,
        "y": 0,
    }


def positions(piece, dx=0, dy=0, shape=None):
    shape = piece["shape"] if shape is None else shape
    return [
        (piece["x"] + x + dx, piece["y"] + y + dy)
        for x, y in shape
    ]


def valid(piece, dx=0, dy=0, shape=None):
    for x, y in positions(piece, dx, dy, shape):
        if x < 0 or x >= COLS or y >= ROWS:
            return False

        if y >= 0 and board[y][x] is not None:
            return False

    return True


def rotate_piece():
    rotated = [(y, -x) for x, y in piece["shape"]]

    min_x = min(x for x, y in rotated)
    min_y = min(y for x, y in rotated)

    rotated = [
        (x - min_x, y - min_y)
        for x, y in rotated
    ]

    for shift in (0, -1, 1, -2, 2):
        if valid(piece, dx=shift, shape=rotated):
            piece["shape"] = rotated
            piece["x"] += shift
            return


def clear_lines():
    global score, lines, level

    remaining = [
        row for row in board
        if any(cell is None for cell in row)
    ]

    cleared = ROWS - len(remaining)

    if cleared:
        board[:] = (
            [[None for _ in range(COLS)] for _ in range(cleared)]
            + remaining
        )

        score += [0, 100, 300, 500, 800][cleared] * level
        lines += cleared
        level = lines // 10 + 1


def lock_piece():
    global piece, game_over

    for x, y in positions(piece):
        if y < 0:
            game_over = True
            return

        board[y][x] = piece["color"]

    clear_lines()

    piece_holder = next_piece
    piece_holder["x"] = COLS // 2 - 2
    piece_holder["y"] = 0

    piece_data = piece_holder.copy()
    piece_data["shape"] = piece_holder["shape"][:]
    piece = piece_data

    generate_next_piece()

    if not valid(piece):
        game_over = True


def generate_next_piece():
    global next_piece
    next_piece = new_piece()


def restart():
    global board, piece, next_piece
    global score, lines, level, game_over, fall_timer

    board = [[None for _ in range(COLS)] for _ in range(ROWS)]

    score = 0
    lines = 0
    level = 1
    game_over = False
    fall_timer = 0

    piece = new_piece()
    next_piece = new_piece()


def draw_block(x, y, color, size=CELL):
    rect = pygame.Rect(x * size, y * size, size, size)

    pygame.draw.rect(
        screen,
        color,
        rect.inflate(-2, -2),
        border_radius=4,
    )

    lighter = tuple(min(255, c + 35) for c in color)

    pygame.draw.line(
        screen,
        lighter,
        (rect.x + 5, rect.y + 5),
        (rect.right - 6, rect.y + 5),
        2,
    )


def draw():
    screen.fill(BG)

    for y in range(ROWS):
        for x in range(COLS):
            rect = (x * CELL, y * CELL, CELL, CELL)

            pygame.draw.rect(screen, GRID, rect, 1)

            if board[y][x] is not None:
                draw_block(x, y, board[y][x])

    if not game_over:
        ghost_y = 0

        while valid(piece, dy=ghost_y + 1):
            ghost_y += 1

        for x, y in positions(piece, dy=ghost_y):
            if y >= 0:
                pygame.draw.rect(
                    screen,
                    piece["color"],
                    (
                        x * CELL + 5,
                        y * CELL + 5,
                        CELL - 10,
                        CELL - 10,
                    ),
                    2,
                    border_radius=3,
                )

        for x, y in positions(piece):
            if y >= 0:
                draw_block(x, y, piece["color"])

    panel_x = 10

    screen.blit(
        font.render(f"SCORE: {score}", True, WHITE),
        (panel_x, 8),
    )

    screen.blit(
        small_font.render(
            f"LINES: {lines}   LEVEL: {level}",
            True,
            WHITE,
        ),
        (panel_x, 35),
    )

    if game_over:
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        screen.blit(overlay, (0, 0))

        title = big_font.render("GAME OVER", True, WHITE)
        restart_text = font.render("Press R to restart", True, WHITE)

        screen.blit(
            title,
            title.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 20)),
        )

        screen.blit(
            restart_text,
            restart_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 20)),
        )

    pygame.display.flip()


restart()
running = True

while running:
    dt = clock.tick(FPS)
    fall_timer += dt

    fall_delay = max(80, 650 - (level - 1) * 55)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                running = False

            elif event.key == pygame.K_r:
                restart()

            elif not game_over:
                if event.key == pygame.K_LEFT and valid(piece, dx=-1):
                    piece["x"] -= 1

                elif event.key == pygame.K_RIGHT and valid(piece, dx=1):
                    piece["x"] += 1

                elif event.key == pygame.K_UP:
                    rotate_piece()

                elif event.key == pygame.K_DOWN:
                    if valid(piece, dy=1):
                        piece["y"] += 1
                        score += 1

                elif event.key == pygame.K_SPACE:
                    distance = 0

                    while valid(piece, dy=distance + 1):
                        distance += 1

                    piece["y"] += distance
                    score += distance * 2

                    lock_piece()
                    fall_timer = 0

    if not game_over and fall_timer >= fall_delay:
        if valid(piece, dy=1):
            piece["y"] += 1
        else:
            lock_piece()

        fall_timer = 0

    draw()

pygame.quit()
