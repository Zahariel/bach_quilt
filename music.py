import re
import typing
import drawSvg as svg


DEFAULT_SCALE = 0.5

NOTE_HEIGHT = 4
NOTE_BOTTOM = {
    ("C", 1): 0,
    ("C#", 1): 0,
    ("Db", 1): 0,
    ("D", 1): 0,
    ("D#", 1): 0,
    ("Eb", 1): 0,
    ("E", 1): 0,
    ("F", 1): 1,
    ("F#", 1): 1,
    ("Gb", 1): 1,
    ("G", 1): 1,
    ("G#", 1): 1,
    ("Ab", 1): 1,
    ("A", 1): 1,
    ("A#", 1): 2,
    ("Bb", 1): 2,
    ("B", 1): 2,
    ("C", 2): 2,
    ("C#", 2): 2,
    ("Db", 2): 2,
    ("D", 2): 3,
    ("D#", 2): 3,
    ("Eb", 2): 3,
    ("E", 2): 3,
    ("F", 2): 3,
    ("F#", 2): 4,
    ("Gb", 2): 4,
    ("G", 2): 4,
    ("G#", 2): 4,
    ("Ab", 2): 4,
    ("A", 2): 4,
    ("A#", 2): 5,
    ("Bb", 2): 5,
    ("B", 2): 5,
    ("C", 3): 5,
    ("C#", 3): 5,
    ("Db", 3): 5,
    ("D", 3): 5,
    ("D#", 3): 6,
    ("Eb", 3): 6,
    ("E", 3): 6,
    ("F", 3): 6,
    ("F#", 3): 6,
    ("Gb", 3): 6,
    ("G", 3): 6,
}

ROW_HEIGHT = NOTE_HEIGHT + max(NOTE_BOTTOM.values())

DIVIDER_HEIGHT = 1

COLOR = {
    "C": "#cc3333",
    "C#": "#ff99cc",
    "Db": "#ff99cc",
    "D": "#ff6633",
    "D#": "#ffff00",
    "Eb": "#ffff00",
    "E": "#99ff33",
    "F": "#ccffcc",
    "F#": "#006600",
    "Gb": "#006600",
    "G": "#0099cc",
    "G#": "#6699ff",
    "Ab": "#6699ff",
    "A": "#000099",
    "A#": "#660099",
    "Bb": "#660099",
    "B": "#990066",
    "R": "#ffffff",
}

REV_COLOR = dict()
for name, color in COLOR.items():
    REV_COLOR[color] = name

class MusicRow:
    def __init__(self, group:svg.Group, max_width, translate_y):
        self.group = group
        self.max_width = max_width
        self.translate_y = translate_y
        self.right = 0
        if self.translate_y != 0:
            self.group.args["transform"] = f"translate(0, {self.translate_y})"


    def center(self):
        self.group.args["transform"] = f"translate({(self.max_width-self.right)/2},{self.translate_y})"


class Drawable:
    def draw(self, rows:typing.Sequence[MusicRow], x, row, **kwargs):
        raise NotImplemented

    def yardage(self, yardage_dict):
        pass

    def top_y(self):
        raise NotImplemented

    def bottom_y(self):
        raise NotImplemented

    def length(self):
        raise NotImplemented


class Note(Drawable):
    def __init__(self, pitch, octave, duration):
        self.pitch = pitch
        self.octave = octave
        self.duration = duration

    def length(self):
        return self.duration

    def draw(self, rows:typing.Sequence[MusicRow], x, row, *, scale=DEFAULT_SCALE, **kwargs):
        if self.pitch != "R":
            dy = self.bottom_y() * scale
            rect = svg.Rectangle(x, dy, self.duration * scale, NOTE_HEIGHT * scale, fill=COLOR[self.pitch])
            rows[row].group.append(rect)
            rows[row].right = x + self.duration * scale
        return x + self.duration * scale, row

    def yardage(self, yardage_dict):
        yardage_dict[COLOR[self.pitch], self.octave] += self.duration + 1

    def bottom_y(self):
        if self.pitch == "R": return ROW_HEIGHT - NOTE_HEIGHT
        return NOTE_BOTTOM[self.pitch, self.octave]

    def top_y(self):
        if self.pitch == "R": return NOTE_HEIGHT
        return NOTE_BOTTOM[self.pitch, self.octave] + NOTE_HEIGHT

    def __repr__(self):
        return f"Note({self.pitch}, {self.octave}, {self.duration})"


class NextLine(Drawable):
    def __init__(self):
        pass

    def draw(self, rows:typing.Sequence[MusicRow], x, row, *, scale=0.5, **kwargs):
        return 0, row + 1

    def __repr__(self):
        return "NextLine()"


class BarLine(Drawable):
    def __init__(self):
        pass

    def draw(self, rows:typing.Sequence[MusicRow], x, row, *, scale=DEFAULT_SCALE,
             separate_measures=0, measure_width=None, **kwargs):
        if measure_width and x + (separate_measures + measure_width) * scale > rows[row].max_width + scale/2:
            return 0, row+1
        return x + separate_measures * scale, row

    def __repr__(self):
        return "BarLine()"


TIME_BARS = {
    1: [[(3,4)]],
    2: [[(0,3), (7,3)]],
    3: [[(0,2), (4,2), (8,2)]],
    4: [[(0,1), (3,1), (6,1), (9,1)]],
    6: [[(2,2), (6,2)], [(0,2), (8,2)], [(2,2), (6,2)]]
}


class TimeSignature(Drawable):
    def __init__(self, top, bottom):
        self.top = top
        self.bottom = bottom

    def draw(self, rows:typing.Sequence[MusicRow], x, row, *, scale=0.5, **kwargs):
        width = 16 // self.bottom
        for column in TIME_BARS[self.top]:
            for start, height in column:
                rect = svg.Rectangle(x, start*scale, width*scale, height*scale, fill="#000000")
                rows[row].group.append(rect)
            x += width*scale
        rows[row].right = x
        return x, row

    def __repr__(self):
        return f"TimeSignature({self.top}, {self.bottom})"


class Repeat(BarLine):
    def __init__(self, left, right):
        super().__init__()
        self.left = left
        self.right = right

    def draw(self, rows:typing.Sequence[MusicRow], x, row, *, scale=0.5, **kwargs):
        if self.left:
            rows[row].group.append(svg.Rectangle(x, 3*scale, scale, scale, fill="#000000"))
            rows[row].group.append(svg.Rectangle(x, (ROW_HEIGHT - 4)*scale, scale, scale, fill="#000000"))
        x += scale
        rows[row].group.append(svg.Rectangle(x, 0, 2*scale, ROW_HEIGHT*scale, fill="#000000"))
        x += 2*scale
        rows[row].right = x
        x, row = super().draw(rows, x, row, scale=scale, **kwargs)
        if self.right:
            if x == 0:
                # barline forced a new line
                rows[row].group.append(svg.Rectangle(x, 0, 2*scale, ROW_HEIGHT*scale, fill="#000000"))
                x += 2*scale
            rows[row].group.append(svg.Rectangle(x, 3*scale, scale, scale, fill="#000000"))
            rows[row].group.append(svg.Rectangle(x, (ROW_HEIGHT-4)*scale, scale, scale, fill="#000000"))
            x += scale
            rows[row].right = x
        else:
            if x != 0:
                # leave space for the right side even though it's not there, so that it ends up an even number
                # of blocks wide
                x += scale
        return x, row

    def __repr__(self):
        return f"Repeat({self.left}, {self.right})"


class Trill(Note):
    def __init__(self, first, octave_adj, second, octave, duration):
        super().__init__(second, octave, duration)
        self.first = first
        self.octave_adj = octave_adj

    def draw(self, rows:typing.Sequence[MusicRow], x, row, *, scale=DEFAULT_SCALE, **kwargs):
        new_x, new_row = super(Trill, self).draw(rows, x, row, scale=scale, **kwargs)
        first_height = NOTE_BOTTOM[self.first, self.octave + 1 if self.octave_adj else self.octave]
        for dx in range(self.duration):
            for dy in range(NOTE_HEIGHT):
                if (dx + dy) % 2 != (first_height+NOTE_HEIGHT) % 2 or (dy == NOTE_HEIGHT-1 and first_height != self.bottom_y()):
                    rows[row].group.append(svg.Rectangle(x + dx*scale, (first_height + dy)*scale, scale, scale, fill=COLOR[self.first]))
        return new_x, new_row

    def yardage(self, yardage_dict):
        super(Trill, self).yardage(yardage_dict)
        yardage_dict[COLOR[self.first], self.octave + (1 if self.octave_adj else 0)] += self.duration + 1

    def top_y(self):
        return NOTE_BOTTOM[self.first, self.octave + 1 if self.octave_adj else self.octave] + NOTE_HEIGHT

    def __repr__(self):
        return f"Trill({self.first}, {self.octave_adj}, {self.pitch}, {self.octave}, {self.duration})"


class MusicBlock(Drawable):
    def __init__(self, notes:typing.Sequence[Drawable]):
        self.notes = list(notes)

    def length(self):
        return sum(note.length() for note in self.notes)

    def bottom_y(self):
        return min(note.bottom_y() for note in self.notes)

    def top_y(self):
        return max(note.top_y() for note in self.notes)

    def draw(self, rows:typing.Sequence[MusicRow], x, row, *, measure_width=16, **kwargs):
        for note in self.notes:
            x, row = note.draw(rows, x, row, measure_width=measure_width, **kwargs)
            if type(note) == TimeSignature:
                measure_width = note.top * (16 // note.bottom)
        return x, row

    def yardage(self, yardage_dict):
        for note in self.notes:
            note.yardage(yardage_dict)

    def __repr__(self):
        return f"MusicBlock({self.notes})"


class Chord(Drawable):
    def __init__(self, lines:typing.Sequence[Drawable], inverted:bool):
        self.lines = list(lines)
        self.inverted = inverted

    def length(self):
        return max(line.length() for line in self.lines)

    def bottom_y(self):
        return min(line.bottom_y() for line in self.lines)

    def top_y(self):
        return max(line.top_y() for line in self.lines)

    def draw(self, rows:typing.Sequence[MusicRow], x, row, *, scale=DEFAULT_SCALE, **kwargs):
        prev_y_offset = None
        for line in reversed(self.lines):
            if prev_y_offset is not None:
                clip = svg.ClipPath()
                width = line.length() * scale
                if self.inverted:
                    y_offset = line.top_y() * scale
                    clip.append(svg.Lines(x, line.bottom_y()*scale,
                                          x + width, prev_y_offset,
                                          x + width, y_offset,
                                          x, y_offset,
                                          close=True))
                else:
                    y_offset = line.bottom_y() * scale
                    clip.append(svg.Lines(x, y_offset,
                                          x + width, y_offset,
                                          x + width, prev_y_offset,
                                          x, line.top_y()*scale,
                                          close=True))
                group = svg.Group(clip_path=clip)
                line.draw([MusicRow(group, rows[row].max_width, 0)], x, 0, scale=scale, **kwargs)
                rows[row].group.append(group)
            else:
                y_offset = line.top_y()*scale if self.inverted else line.bottom_y()*scale
                line.draw(rows, x, row, scale=scale, **kwargs)
            prev_y_offset = y_offset
        x += self.length() * scale
        rows[row].right = x
        return x, row

    def yardage(self, yardage_dict):
        for line in self.lines:
            line.yardage(yardage_dict)

    def __repr__(self):
        return f"Chord({self.lines})"


def parse_note(token, octave, length):
    note = None
    if token[0] == "O":
        octave = int(token[1])
    elif token == "<":
        octave -= 1
    elif token == ">":
        octave += 1
    elif token == "CR":
        note = NextLine()
    elif token == "|":
        note = BarLine()
    elif token[0] == "T":
        top, bottom = re.match(r"T(\d+)/(\d+)", token).groups()
        note = TimeSignature(int(top), int(bottom))
    elif "/" in token:
        left = token[0] == ":"
        right = token[-1] == ":"
        note = Repeat(left, right)
    elif token[0] == "~":
        first, octave_adj, second, duration = re.match(r"~(.[b#]?)('?)~(.[b#]?)(\d*)", token).groups()
        note = Trill(first, bool(octave_adj), second, octave, int(duration or length))
    else:
        pitch, duration = re.match(r"(.[b#]?)(\d*)", token).groups()
        if pitch == "L":
            length = int(duration)
        else:
            note = Note(pitch, octave, int(duration or length))
    return octave, length, note


def parse_chord(music, pos, octave, length):
    lines = []
    inverted = False
    while pos < len(music):
        token = music[pos]
        if token == "(":
            pos, octave, length, line = parse_music(music, pos + 1, octave, length)
            lines.append(line)
        elif token == "]":
            pos += 1
            break
        elif token == "}":
            pos += 1
            inverted = True
            break
        else:
            octave, length, note = parse_note(token, octave, length)
            pos += 1
            if note is not None:
                lines.append(note)
    return pos, octave, length, Chord(lines, inverted)


def parse_music(music:typing.Union[str, typing.Sequence[str]], pos=0, octave=1, length=1):
    if type(music) == str:
        music = music.split()
    notes = []
    while pos < len(music):
        token = music[pos]
        if token == "[" or token == "{":
            pos, octave, length, chord = parse_chord(music, pos + 1, octave, length)
            notes.append(chord)
        elif token == ")":
            pos += 1
            break
        else:
            octave, length, note = parse_note(token, octave, length)
            if note is not None:
                notes.append(note)
            pos += 1

    return pos, octave, length, MusicBlock(notes)

