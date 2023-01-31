import math
from collections import defaultdict

import drawSvg as svg
from music2 import COLOR, NOTE_BOTTOM, REV_COLOR, ROW_HEIGHT, parse_music, MusicRow
import data

DEBUG=False


center_width = 16
center_height = 28
rings = 6
ring_spacing = 0.5

main_width = center_width + 2 * (5+ring_spacing) * rings
main_height = center_height + 2 * (5+ring_spacing) * rings

# padding, border 1, margin, main border, margin, border 2
main_offset = (1 + 1 + 1 + 5 + 1.5 + 1)

total_width = main_width + 2 * main_offset
total_height = main_height + 2 * main_offset

drawing = svg.Drawing(total_width, total_height)
drawing.setRenderSize(f"{total_width / 10}in", f"{total_height / 10}in")

# draw outside border
drawing.append(svg.Rectangle(0.5, 0.5, total_width - 1, total_height - 1, stroke_width=1, stroke="#666666", fill="#ffffff"))
# draw inside border
drawing.append(svg.Rectangle(main_offset - 1.5, main_offset - 1.5, main_width + 3, main_height + 3, stroke_width=1, stroke="#666666", fill="#ffffff"))


main_group = svg.Group(transform=f"translate({main_offset}, {-main_offset})")
drawing.append(main_group)

main_group.append(svg.Rectangle((5+ring_spacing) * rings + 0.5, (5+ring_spacing) * rings + 0.5, center_width - 1, center_height - 1, stroke_width=1, stroke="#666666", fill="#ffffff"))

main_rows = []

for i in range(rings):
    if i == 0:
        top, top_width = svg.Group(transform=f"translate({i * (5+ring_spacing)},{i * (5+ring_spacing) - main_height + 5})"), main_width - i * 2 * (5+ring_spacing) - (5+ring_spacing)
    else:
        top, top_width = svg.Group(transform=f"translate({i * (5+ring_spacing) - (5+ring_spacing)},{i * (5+ring_spacing) - main_height + 5})"), main_width - i * 2 * (5+ring_spacing)
    right, right_width = svg.Group(transform=f"translate({main_width - 5 - i * (5+ring_spacing)},{i * (5+ring_spacing) - main_height}) rotate(90)"), main_height - i * 2 * (5+ring_spacing) - (5+ring_spacing)
    bottom, bottom_width = svg.Group(transform=f"translate({main_width - i * (5+ring_spacing)},{-5 - i * (5+ring_spacing)}) rotate(180)"), main_width - i * 2 * (5+ring_spacing) - (5+ring_spacing)
    if i == rings - 1:
        left, left_width = svg.Group(transform=f"translate({5 + i * (5+ring_spacing)},{-i * (5+ring_spacing)}) rotate(270)"), main_height - i * 2 * (5+ring_spacing) - (5+ring_spacing)
    else:
        left, left_width = svg.Group(transform=f"translate({5 + i * (5+ring_spacing)},{-i * (5+ring_spacing)}) rotate(270)"), main_height - i * 2 * (5+ring_spacing) - 2 * (5+ring_spacing)

    for g, w in [(top, top_width), (right, right_width), (bottom, bottom_width), (left, left_width)]:
        main_group.append(g)
        inner = svg.Group()
        g.append(inner)
        main_rows.append(MusicRow(inner, w, 0))
        if DEBUG:
            inner.append(svg.Rectangle(.25, .25, w - 0.5, 4.5, stroke_width=.5, stroke="#ff0000", fill="#ffffff"))
            inner.append(svg.Text(str(i), 1, 1, 2))


# for i in range(1,num_rows):
#     main_group.append(svg.Rectangle(0, i*5.5-0.5, main_width, 0.5, fill="#666666"))

border_gap = 8

border_groups = [
    (svg.Group(transform=f"translate({main_offset + (main_width + border_gap)/2},{7.5-total_height})"), (main_width+4 - border_gap)/2),
    (svg.Group(transform=f"translate({total_width - main_offset + 3},{main_offset - total_height - 2}) rotate(90)"), main_height+4),
    (svg.Group(transform=f"translate({total_width - main_offset + 2},{-main_offset + 3}) rotate(180)"), main_width+4),
    (svg.Group(transform=f"translate({main_offset - 3},{2 - main_offset}) rotate(270)"), main_height+4),
    (svg.Group(transform=f"translate({main_offset - 2},{7.5-total_height})"), (main_width+4 - border_gap)/2),
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

corner_groups = [
    svg.Group(transform=f"translate(1,{main_offset - total_height - 2})"),
    svg.Group(transform=f"translate({main_offset + main_width + 2},{1 - total_height}) rotate(90)"),
    svg.Group(transform=f"translate({total_width - 1},{-main_offset + 2}) rotate(180)"),
    svg.Group(transform=f"translate({main_offset - 2},{-1}) rotate(270)"),
]


# given inches, round up to nearest half-strip
def strips(inches):
    # don't bother making even half a stripset for less than 6 inches
    if inches < 6:
        return 0
    return (math.ceil(inches / 20)) / 2

if not DEBUG:
    _, _, _, prelude = parse_music(data.prelude)
    prelude.draw(border_rows, 0, 0)

    MOVEMENT_SEPARATOR = 2

    _, _, _, allemande = parse_music(data.allemande)
    x, y = allemande.draw(main_rows, 0, 0)

    _, _, _, courante = parse_music(data.courante)
    x, y = courante.draw(main_rows, x + MOVEMENT_SEPARATOR, y)

    _, _, _, sarabande = parse_music(data.sarabande)
    x, y = sarabande.draw(main_rows, x + MOVEMENT_SEPARATOR, y, measure_width=24)

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

    yardage_accumulator = defaultdict(float)
    prelude.yardage(yardage_accumulator)
    allemande.yardage(yardage_accumulator)
    courante.yardage(yardage_accumulator)
    sarabande.yardage(yardage_accumulator)
    minuet_1.yardage(yardage_accumulator)
    minuet_2.yardage(yardage_accumulator)
    gigue.yardage(yardage_accumulator)

    yardage_dict = defaultdict(dict)
    white_dict = defaultdict(float)
    white_fullheight = 0
    for (color, octave, height), strip_units in yardage_accumulator.items():
        num_strips = strips(strip_units/2)
        if color == "#ffffff":
            white_fullheight += strip_units + 1
        else:
            yardage_dict[REV_COLOR[color]][octave, height] = (strip_units/2, num_strips)
            white_dict[NOTE_BOTTOM[height][REV_COLOR[color], octave] + 1] += num_strips
            white_dict[ROW_HEIGHT - NOTE_BOTTOM[height][REV_COLOR[color], octave] - height + 1] += num_strips

    print("Stripsets:")
    for note, d in sorted(yardage_dict.items()):
        for (octave, height), (i, s) in sorted(d.items()):
            print(note, height, octave, i, s)
        overall_width = int(math.ceil(sum((h+1)/2 * s for (_, h), (_, s) in d.items())))
        print(note, overall_width / 36, "yards")

    # print("White strips:")
    # del white_dict[1] # no half-inch strips please
    # # add the movement separators
    # white_fullheight += MOVEMENT_SEPARATOR * 9 + 5
    # # add the row separators
    # white_dict[2] += strips((num_rows - 1) * (main_width + 2))
    # # add the centering
    # for row in main_rows:
    #     white_fullheight += (row.max_width - row.right) * 2 + 6
    # white_dict[ROW_HEIGHT + 1] = strips(white_fullheight/2)
    # for width, s in sorted(white_dict.items()):
    #     print(width/2, s)
    # print(sum(width / 2 * math.ceil(s) / 36 for width, s in white_dict.items()), "yards")

    print("Gray strips:")
    # gray_half_length = (num_rows - 1) * (main_width + 0.5)
    # gray_half_strips = strips(gray_half_length)
    gray_inch_length = 2*(main_width+2) + 2*(main_height+2) + 8
    gray_binding_length = 2*total_width + 2*total_height + 8
    gray_inch_strips = strips(gray_inch_length)
    gray_binding_strips = strips(gray_binding_length)
    # print(0.5, gray_half_strips)
    print(1, gray_inch_strips)
    print(2.75, gray_binding_strips)
    # print((gray_half_strips * 0.5 + gray_inch_strips) / 36, "yards")
    print ((gray_inch_strips * 1.5 + gray_binding_strips * 2.75) / 36, "yards")
    print()
    print("center amounts")
    for i, row in enumerate(main_rows):
        print("main", i, row.max_width, row.right, (row.max_width - row.right)/2)
    for i, row in enumerate(border_rows):
        print("border", i, row.max_width, row.right, (row.max_width - row.right)/2)

print("total size", total_width-2, total_height-2)
drawing.saveSvg("quilt_render3.svg")


