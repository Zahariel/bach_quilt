import math
import os
from collections import defaultdict

import drawsvg as svg
from music2 import NOTE_TOP, REV_COLOR, ROW_HEIGHT, parse_music, MusicRow
import data


pages = []
blocks_rows = []
BLOCKS_ROWS_PER_PAGE = 4
BLOCKS_SCALE = 1/3
blocks_width = 7.5 / BLOCKS_SCALE
blocks_height = 10 / BLOCKS_SCALE
NUM_PAGES = 25
for page in range(NUM_PAGES):
    page_drawing = svg.Drawing(8/BLOCKS_SCALE, blocks_height, origin=(-1, 0))
    page_drawing.set_render_size("8in", "10in")
    page_drawing.append(svg.Rectangle(-1, 0, 8/BLOCKS_SCALE, blocks_height, fill="#ffffff", stroke="#000000", stroke_width=0.1))
    pages.append(page_drawing)
    page_rows = [MusicRow(svg.Group(), blocks_width, i * 6 + 5) for i in range(BLOCKS_ROWS_PER_PAGE)]
    blocks_rows += page_rows
    for r in page_rows:
        page_drawing.append(r.group)

def draw_movement(music, page, name):
    x, y = music.draw(blocks_rows, 0, page * BLOCKS_ROWS_PER_PAGE, separate_measures=2, measure_border="#cccccc")
    last_page = y // BLOCKS_ROWS_PER_PAGE
    if y % BLOCKS_ROWS_PER_PAGE == 0 and x == 0:
        last_page -= 1
    for p in range(page, last_page + 1):
        pages[p].append(svg.Text(f"{name} (Page {p - page +1})", 2, 4/BLOCKS_SCALE-1, 2, center=True))
    return last_page + 1

_, _, _, prelude = parse_music(data.prelude)
page = draw_movement(prelude, 0, "Prelude")

_, _, _, allemande = parse_music(data.allemande)
page = draw_movement(allemande, page, "Allemande")

_, _, _, courante = parse_music(data.courante)
page = draw_movement(courante, page, "Courante")

_, _, _, sarabande = parse_music(data.sarabande)
page = draw_movement(sarabande, page, "Sarabande")

_, _, _, minuet_1 = parse_music(data.minuet_1)
page = draw_movement(minuet_1, page, "Minuet I")

_, _, _, minuet_2 = parse_music(data.minuet_2)
page = draw_movement(minuet_2, page, "Minuet II")

_, _, _, gigue = parse_music(data.gigue)
page = draw_movement(gigue, page, "Gigue")


os.makedirs("blocks", exist_ok=True)
for i, page in enumerate(pages):
    page.save_svg(f"blocks/page{i+1:03}.svg")

