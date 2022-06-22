import math
from collections import defaultdict

import drawSvg as svg
from music2 import NOTE_BOTTOM, REV_COLOR, ROW_HEIGHT, parse_music, MusicRow
import data


BLOCKS_SCALE = 2/5
blocks_width = 7.6 / BLOCKS_SCALE
blocks_height = 10 / BLOCKS_SCALE
blocks_drawing = svg.Drawing(blocks_width+1, blocks_height, origin=(-0.5, 0))
blocks_drawing.setRenderSize("8in", "10in")
blocks_drawing.append(svg.Rectangle(-0.5, 0, blocks_width+1, blocks_height, fill="#ffffff"))
BLOCKS_ROWS_PER_PAGE = 4
blocks_rows = [MusicRow(svg.Group(), blocks_width, i * 6 - blocks_height + 6) for i in range(BLOCKS_ROWS_PER_PAGE)]

for r in blocks_rows:
    blocks_drawing.append(r.group)

try:
    _, _, _, prelude = parse_music(data.prelude)
    x, y = prelude.draw(blocks_rows, 0, 0, separate_measures=2, measure_border="#cccccc")
except:
    pass

blocks_drawing.saveSvg("blocks_render.svg")

