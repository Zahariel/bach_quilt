import drawSvg as svg

from music import parse_music

drawing = svg.Drawing(82,91, origin=(1,1))
drawing.setRenderSize("8.2in", "9.1in")

music_str = "T3/2 O1 L2 G# O3 D C < B [ O1 A > E > C6 ] < B A G F# E < | [ ( R B > C < A B ) O2 D10 ] E F# G A > C < B G | D G A F# G8 < G8"
_, _, _, music = parse_music(music_str)
print(music)
music.draw(drawing, 0, 84, separate_measures=2)


music_str3 = "T6/8 O2 F# A D E F D F# D G D G# D A D Bb D | B D > C < D > C# < D > D < D > Eb < D > E < D > F < D > F# < D > | G < B D B > G < B > G < B > G < B D B > G < B > G < B > | G < A D A > G < A > G < A > G < A D A > G < A > G < A | "
music_str3 += "CR O3 F# C < D > C F# C F# C F# C < D > C F# C F# C | [ O1 G2 > B16 > G16 ]"
_, _, _, music = parse_music(music_str3)
print(music)
music.draw(drawing, 0, 78, separate_measures=2)

drawing.saveSvg("test.svg")
