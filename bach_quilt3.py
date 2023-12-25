import math
import typing
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

inner_padding = 1
inner_border = 1
inner_margin = 1
border_row_height = ROW_HEIGHT//2
outer_margin = 1.5
outer_border = 1

# padding, border 1, margin, main border, margin, border 2
main_offset = (inner_padding + inner_border + inner_margin + border_row_height + outer_margin + outer_border)

total_width = main_width + 2 * main_offset
total_height = main_height + 2 * main_offset

drawing = svg.Drawing(total_width, total_height)
drawing.setRenderSize(f"{total_width / 10}in", f"{total_height / 10}in")

# draw outside border
drawing.append(svg.Rectangle(outer_border/2, outer_border/2,
                             total_width - outer_border, total_height - outer_border,
                             stroke_width=outer_border, stroke="#666666", fill="#ffffff"))
# draw inside border
drawing.append(svg.Rectangle(main_offset - inner_padding - inner_border/2, main_offset - inner_padding - inner_border/2,
                             main_width + 2*inner_padding + inner_border, main_height + 2*inner_padding + inner_border,
                             stroke_width=inner_border, stroke="#666666", fill="#ffffff"))


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
    x, y = minuet_2.draw(main_rows, x + MOVEMENT_SEPARATOR, y)

    _, _, _, gigue = parse_music(data.gigue)
    x, y = gigue.draw(main_rows, x + MOVEMENT_SEPARATOR, y)

    for g in main_rows:
        g.center()

    for g in border_rows:
        g.center()

    yardage_accumulator : typing.Dict[typing.Tuple[str, int, int], float] = defaultdict(float)
    # yardage_accumulator: (color, octave, finished strip width) -> raw half-inches
    prelude.yardage(yardage_accumulator)
    allemande.yardage(yardage_accumulator)
    courante.yardage(yardage_accumulator)
    sarabande.yardage(yardage_accumulator)
    minuet_1.yardage(yardage_accumulator)
    minuet_2.yardage(yardage_accumulator)
    gigue.yardage(yardage_accumulator)

    gray_half_inch_length = yardage_accumulator.pop((COLOR["N"], 1, 1))

    yardage_dict = defaultdict(dict)
    # yardage_dict: note -> (octave, raw strip width (in half inches)) -> (raw inches, strips)
    white_dict : typing.Dict[int, float] = defaultdict(float)
    # white_dict: raw strip width (in half inches) -> strips needed
    white_fullheight = 0
    # white_fullheight in half-inches
    for (color, octave, height), half_inches in yardage_accumulator.items():
        num_strips = strips(half_inches/2)
        if color == "#ffffff":
            white_fullheight += half_inches
        else:
            yardage_dict[REV_COLOR[color]][octave, height + 1] = (half_inches/2, num_strips)
            white_dict[NOTE_BOTTOM[height][REV_COLOR[color], octave] + 1] += num_strips
            white_dict[ROW_HEIGHT - NOTE_BOTTOM[height][REV_COLOR[color], octave] - height + 1] += num_strips
    with open("cutting template.txt", mode="w") as instructions:
        print("Stripsets (raw measurements):", file=instructions)
        for note, d in sorted(yardage_dict.items()):
            for (octave, strip_width), (i, s) in sorted(d.items()):
                white_below = NOTE_BOTTOM[strip_width - 1][note, octave] + 1
                white_above = ROW_HEIGHT - NOTE_BOTTOM[strip_width - 1][note, octave] - strip_width + 2
                if white_above > 1:
                    print(f"{white_above/2}\" white, ", end="", file=instructions)
                print(f"{strip_width/2}\" {note}", end="", file=instructions)
                if white_below > 1:
                    print(f", {white_below/2}\" white", end="", file=instructions)
                print(f": {i}\", {s} strips", file=instructions)
            overall_width = int(math.ceil(sum(h/2 * s for (_, h), (_, s) in d.items())))
            print(note, overall_width / 36, "yards", file=instructions)
            print(file=instructions)

        print("White strips:", file=instructions)
        del white_dict[1] # no half-inch strips please

        # add the movement separators
        white_fullheight += (MOVEMENT_SEPARATOR * 2 + 1) * 5

        # add the row separators
        white_dict[int(ring_spacing*2+1)] += strips(sum(row.max_width for row in main_rows))

        # add the centering
        for row in main_rows + border_rows:
            white_fullheight += (row.max_width - row.right) * 2 + 6

        # add the border gap
        white_fullheight += border_gap * 2

        white_dict[ROW_HEIGHT + 1] = strips(white_fullheight/2)

        # add the borders
        white_dict[int(inner_padding*2+1)] += strips(2*main_width + 2*main_height)
        white_dict[int(inner_margin*2+1)] += strips(2*main_width + 2*main_height + 4*inner_border + 4*inner_margin)
        white_dict[int(outer_margin*2+1)] += strips(2*total_width + 2*total_height)

        for width, s in sorted(white_dict.items()):
            print(f"{width/2}\": {s} strips total", file=instructions)
        print(sum((width / 2 * math.ceil(s)) / 36 for width, s in white_dict.items()), "yards", file=instructions)

        print(f"Center block: {center_width} x {center_height} finished", file=instructions)
        print(file=instructions)

        print("Gray strips:", file=instructions)
        inner_border_length = 2*(main_width+2) + 2*(main_height+2) + 8
        binding_length = 2*total_width + 2*total_height + 8
        center_border_length = 2*(center_width+2) + 2*(center_height+2)
        gray_inch_strips = strips(inner_border_length + center_border_length)
        gray_binding_strips = strips(binding_length)
        gray_half_inch_strips = strips(gray_half_inch_length)
        print(f"1 inch: {gray_half_inch_strips} strips", file=instructions)
        print(f"1.5 inch: {gray_inch_strips} strips", file=instructions)
        print(f"2.5 inch for binding: {gray_binding_strips} strips", file=instructions)
        print ((gray_half_inch_strips + gray_inch_strips * 1.5 + gray_binding_strips * 2.75) / 36, "yards", file=instructions)
        print(file=instructions)

        print("centering amounts", file=instructions)
        for i, row in enumerate(main_rows):
            print(f"main row {i}: nominal width {row.max_width}; actual width {row.right}; centering needed {(row.max_width - row.right) / 2}", file=instructions)
        for i, row in enumerate(border_rows):
            print(f"border row {i}: nominal width {row.max_width}; actual width {row.right}; centering needed {(row.max_width - row.right) / 2}", file=instructions)

        print(file=instructions)
        print("total size", total_width- outer_border*2, total_height - outer_border*2, file=instructions)

drawing.saveSvg("quilt_render3.svg")


