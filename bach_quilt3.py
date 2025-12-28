import math
import typing
from collections import defaultdict

import drawsvg as svg
from music2 import COLOR, NOTE_TOP, REV_COLOR, ROW_HEIGHT, parse_music, MusicRow
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
outer_padding = 1.5
outer_border = 1

# padding, border 1, margin, main border, margin, border 2
main_offset = (inner_padding + inner_border + inner_margin + border_row_height + outer_padding + outer_border)

total_width = main_width + 2 * main_offset
total_height = main_height + 2 * main_offset

drawing = svg.Drawing(total_width, total_height)
drawing.set_render_size(f"{total_width / 10}in", f"{total_height / 10}in")

# draw outside border
drawing.append(svg.Rectangle(outer_border/2, outer_border/2,
                             total_width - outer_border, total_height - outer_border,
                             stroke_width=outer_border, stroke="#666666", fill="#ffffff"))
# draw inside border
drawing.append(svg.Rectangle(main_offset - inner_padding - inner_border/2, main_offset - inner_padding - inner_border/2,
                             main_width + 2*inner_padding + inner_border, main_height + 2*inner_padding + inner_border,
                             stroke_width=inner_border, stroke="#666666", fill="#ffffff"))


main_group = svg.Group(transform=f"translate({main_offset}, {main_offset})")
drawing.append(main_group)

main_group.append(svg.Rectangle((5+ring_spacing) * rings + 0.5, (5+ring_spacing) * rings + 0.5, center_width - 1, center_height - 1, stroke_width=1, stroke="#666666", fill="#ffffff"))

main_rows = []

for i in range(rings):
    if i == 0:
        top, top_width = svg.Group(transform=f"translate({i * (5+ring_spacing)},{i * (5+ring_spacing)})"), main_width - i * 2 * (5+ring_spacing) - (5+ring_spacing)
    else:
        top, top_width = svg.Group(transform=f"translate({i * (5+ring_spacing) - (5+ring_spacing)},{i * (5+ring_spacing)})"), main_width - i * 2 * (5+ring_spacing)
    right, right_width = svg.Group(transform=f"translate({main_width - i * (5+ring_spacing)},{i * (5+ring_spacing)}) rotate(90)"), main_height - i * 2 * (5+ring_spacing) - (5+ring_spacing)
    bottom, bottom_width = svg.Group(transform=f"translate({main_width - i * (5+ring_spacing)},{main_height - i * (5+ring_spacing)}) rotate(180)"), main_width - i * 2 * (5+ring_spacing) - (5+ring_spacing)
    if i == rings - 1:
        left, left_width = svg.Group(transform=f"translate({i * (5+ring_spacing)},{main_height - i * (5+ring_spacing)}) rotate(270)"), main_height - i * 2 * (5+ring_spacing) - (5+ring_spacing)
    else:
        left, left_width = svg.Group(transform=f"translate({i * (5+ring_spacing)},{main_height - i * (5+ring_spacing)}) rotate(270)"), main_height - i * 2 * (5+ring_spacing) - 2 * (5+ring_spacing)

    for id, g, w in [("T", top, top_width), ("R", right, right_width), ("B", bottom, bottom_width), ("L", left, left_width)]:
        main_group.append(g)
        inner = svg.Group()
        g.append(inner)
        main_rows.append(MusicRow(inner, w, 0))
        if DEBUG:
            inner.append(svg.Rectangle(.25, .25, w - 0.5, 4.5, stroke_width=.5, stroke="#ff0000", fill="#ffffff"))
            inner.append(svg.Text(f"{id}{i}", 1, 1, 2))


border_gap = 8

border_groups = [
    (svg.Group(transform=f"translate({main_offset + (main_width + border_gap)/2},{outer_border + outer_padding})"), (main_width + 2 * (inner_padding + inner_border) - border_gap) / 2),
    (svg.Group(transform=f"translate({total_width - outer_border - outer_padding},{main_offset - inner_border - inner_padding}) rotate(90)"), main_height + 2 * (inner_padding + inner_border)),
    (svg.Group(transform=f"translate({total_width - main_offset + inner_border + inner_padding},{total_height - outer_border - outer_padding}) rotate(180)"), main_width + 2 * (inner_padding + inner_border)),
    (svg.Group(transform=f"translate({outer_border + outer_padding},{total_height - main_offset + inner_border + inner_padding}) rotate(270)"), main_height + 2 * (inner_padding + inner_border)),
    (svg.Group(transform=f"translate({main_offset - inner_padding - inner_border},{outer_border + outer_padding})"), (main_width + 2 * (inner_padding + inner_border) - border_gap) / 2),
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
            white_dict[NOTE_TOP[height][REV_COLOR[color], octave] + 1] += num_strips
            white_dict[ROW_HEIGHT - NOTE_TOP[height][REV_COLOR[color], octave] - height + 1] += num_strips
    with open("cutting template.txt", mode="w") as instructions:
        print("Stripsets (raw measurements):", file=instructions)
        for note, d in sorted(yardage_dict.items()):
            for (octave, strip_width), (i, s) in sorted(d.items()):
                white_above = NOTE_TOP[strip_width - 1][note, octave] + 1
                white_below = ROW_HEIGHT - NOTE_TOP[strip_width - 1][note, octave] - strip_width + 2
                if white_above > 1:
                    print(f"{white_above/2}\" white, ", end="", file=instructions)
                print(f"{strip_width/2}\" {note}", end="", file=instructions)
                if white_below > 1:
                    print(f", {white_below/2}\" white", end="", file=instructions)
                print(f": {i}\", {s} strips", file=instructions)
            overall_width = int(math.ceil(sum(h/2 * s for (_, h), (_, s) in d.items())))
            print(note, overall_width / 36, "yards", file=instructions)
            print(file=instructions)

        # add the row separators
        row_spacing_strips = strips(sum(row.max_width for row in main_rows))
        print(f"Between rows (1\" white): {row_spacing_strips} strips", file=instructions)
        white_dict[int(ring_spacing*2+1)] += row_spacing_strips

        # add the movement separators
        movement_separator_size = (MOVEMENT_SEPARATOR * 2 + 1) * 5
        print(f"Between movements (5.5\" white): {movement_separator_size/2}\"", file=instructions)
        white_fullheight += movement_separator_size

        # add the centering
        centering = 0
        for row in main_rows + border_rows:
            centering += (row.max_width - row.right) * 2 + 6
        print(f"centering (5.5\" white): {centering/2}\"", file=instructions)
        white_fullheight += centering

        # add the border gap
        print(f"border gap (5.5\" white): {border_gap * 2}\"", file=instructions)
        white_fullheight += border_gap * 2

        white_dict[ROW_HEIGHT + 1] = strips(white_fullheight/2)

        # add the borders
        inner_padding_strips = strips(2 * main_width + 2 * main_height)
        print(f"inner padding ({inner_padding + 0.5}\" white): {inner_padding_strips} strips", file=instructions)
        white_dict[int(inner_padding*2+1)] += inner_padding_strips

        inner_margin_strips = strips(2 * main_width + 2 * main_height + 4 * inner_border + 4 * inner_margin)
        print(f"inner margin ({inner_margin + 0.5}\" white): {inner_margin_strips} strips", file=instructions)
        white_dict[int(inner_margin*2+1)] += inner_margin_strips

        outer_padding_strips = strips(2 * total_width + 2 * total_height)
        print(f"outer padding ({outer_padding + 0.5}\" white): {outer_padding_strips} strips", file=instructions)
        white_dict[int(outer_padding * 2 + 1)] += outer_padding_strips

        del white_dict[1] # no half-inch strips please

        print("Total white strips:", file=instructions)
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
        print((gray_half_inch_strips + gray_inch_strips * 1.5 + gray_binding_strips * 2.75) / 36, "yards", file=instructions)
        print(file=instructions)

        print("centering amounts", file=instructions)
        for i, row in enumerate(main_rows):
            print(f"main row {i}: nominal width {row.max_width}; actual width {row.right}; centering needed {(row.max_width - row.right) / 2}", file=instructions)
        for i, row in enumerate(border_rows):
            print(f"border row {i}: nominal width {row.max_width}; actual width {row.right}; centering needed {(row.max_width - row.right) / 2}", file=instructions)

        print(file=instructions)
        print("total size", total_width- outer_border*2, total_height - outer_border*2, file=instructions)

drawing.save_svg("quilt_render3.svg")
