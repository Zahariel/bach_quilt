from collections import defaultdict

import drawSvg as svg
from music import REV_COLOR, parse_music, MusicRow
import data

DEBUG=False

num_rows = 16

main_height = num_rows * 5.5 - 0.5
total_height = main_height + 14
main_width = 80
total_width = main_width + 14


drawing = svg.Drawing(total_width, total_height, origin=(-1, -1))
drawing.setRenderSize(f"{total_width / 10}in", f"{total_height / 10}in")

# draw outside border
drawing.append(svg.Rectangle(-0.5, -0.5, total_width - 1, total_height - 1, stroke_width=1, stroke="#666666", fill="#ffffff"))

# draw inside border
drawing.append(svg.Rectangle(5.5, 5.5, main_width + 1, main_height + 1, stroke_width=1, stroke="#666666", fill="#ffffff"))

main_group = svg.Group(transform=f"translate(6, -6)")
drawing.append(main_group)

main_rows = [MusicRow(svg.Group(), main_width, i * 5.5 - main_height + 5) for i in range(num_rows)]

for i, g in enumerate(main_rows):
    main_group.append(g.group)
    if DEBUG:
        g.group.append(svg.Rectangle(.25, .25, 79.5, 4.5, stroke_width=.5, stroke="#ff0000", fill="#ffffff"))
        g.group.append(svg.Text(str(i), 1, 1, 2))

for i in range(1,num_rows):
    main_group.append(svg.Rectangle(0, i*5.5-0.5, main_width, 0.5, fill="#666666"))

border_groups = [
    (svg.Group(transform=f"translate(5,{7-total_height})"), main_width+2),
    (svg.Group(transform=f"translate({total_width-7},{7-total_height}) rotate(90)"), main_height+2),
    (svg.Group(transform=f"translate({total_width-7},-5) rotate(180)"), main_width+2),
    (svg.Group(transform=f"translate(5, -5) rotate(270)"), main_height+2),
]

border_rows = []
for i, (g, w) in enumerate(border_groups):
    drawing.append(g)
    inner_group = svg.Group()
    g.append(inner_group)
    border_rows.append(MusicRow(inner_group, w, 0))
    if DEBUG:
        inner_group.append(svg.Rectangle(.25, .25, w-0.5, 4.5, stroke_width=.5, stroke="#0000ff", fill="#ffffff"))
        inner_group.append(svg.Text(str(i), 1, 1, 2))


def strips(strip_units):
    return round(strip_units / 80) + 1

if not DEBUG:
    _, _, _, prelude = parse_music(data.prelude)
    prelude.draw(border_rows, 0, 0)

    MOVEMENT_SEPARATOR = 2

    _, _, _, allemande = parse_music(data.allemande)
    x, y = allemande.draw(main_rows, 0, 0)

    _, _, _, courante = parse_music(data.courante)
    x, y = courante.draw(main_rows, x + MOVEMENT_SEPARATOR, y)

    _, _, _, sarabande = parse_music(data.sarabande)
    x, y = sarabande.draw(main_rows, x + MOVEMENT_SEPARATOR, y)

    _, _, _, minuet_1 = parse_music(data.minuet_1)
    x, y = minuet_1.draw(main_rows, x + MOVEMENT_SEPARATOR, y)

    _, _, _, minuet_2 = parse_music(data.minuet_2)
    x, y = minuet_2.draw(main_rows, x + MOVEMENT_SEPARATOR / 2, y)

    _, _, _, gigue = parse_music(data.gigue)
    x, y = gigue.draw(main_rows, x + MOVEMENT_SEPARATOR, y)

    for g in main_rows:
        g.center()

    for g in border_rows:
        g.center()

    yardage_dict = defaultdict(float)
    prelude.yardage(yardage_dict)
    allemande.yardage(yardage_dict)
    courante.yardage(yardage_dict)
    sarabande.yardage(yardage_dict)
    minuet_1.yardage(yardage_dict)
    minuet_2.yardage(yardage_dict)
    gigue.yardage(yardage_dict)

    for color, strip_units in yardage_dict.items():
        num_strips = strips(strip_units)
        print(REV_COLOR[color], num_strips, (num_strips * 2.5) / 36)

    white_units = sum(yardage_dict.values())
    white_strips = strips(white_units)
    print("white", white_strips, (white_strips * 4) / 36)

drawing.saveSvg("quilt_render.svg")


