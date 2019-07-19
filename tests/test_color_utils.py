import pytest
from generalUtils.color_utils import colorList, rgb_to_hex, hex_to_rgb, findColor


def test_rgb_vs_hex():
    # check all colors in colorList
    for c in colorList:
        # make sure conversions work
        assert '#'+rgb_to_hex(c[2]) == c[1]
        assert hex_to_rgb(c[1]) == c[2]


def test_findColor():
    # check all colors in colorList
    for C in colorList:
        # possible identifiers are all names in C[0], hex string in C[1], and rgb tuple in C[2]
        clist = C[0] + list((C[1], C[2]))

        # each identifier returns correct color
        for c in clist:
            assert findColor(c) == C

    # check all colors in colorList
    for c in colorList:
        # adjust rgb values slightly to test the search algorithm (which gets closest by rgb tuple_distance)
        assert c == findColor((c[2][0]+2, c[2][1]-2, c[2][2]))
        assert c == findColor((c[2][0], c[2][1]+2, c[2][2]-2))
        assert c == findColor((c[2][0]-2, c[2][1], c[2][2]+2))
