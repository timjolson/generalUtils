from types import MethodType, FunctionType, LambdaType
from math import sqrt
from types import SimpleNamespace
import re


def isFunc(func):
    """Check if 'func' is an instance of (MethodType, FunctionType, LambdaType)

    :param func: thing to check if it's a function
    :return: bool, whether 'func' is an instance of (MethodType, FunctionType, LambdaType)
    """
    return isinstance(func, (MethodType, FunctionType, LambdaType))


def getAllFuncs(localDict):
    """Get names of all functions in a dictionary. Uses isFunc.
    Ignores names starting with dunder '__'

    :param localDict: dictionary to check for functions
    :return: [strings], names of functions in localDict where isFunc()==True
    """
    return [x[0] for x in filter(lambda x: isFunc(x[1]), localDict.items()) if not x[0].startswith('__')]


def getAllClasses(localDict):
    """Get names of all classes in a dictionary.
    Ignores names starting with dunder '__'

    :param localDict: dictionary to check for classes
    :return: [strings], names of functions in localDict where isinstance(obj, type)==True
    """
    return [x[0] for x in filter(lambda x: isinstance(x[1], type), localDict.items()) if not x[0].startswith('__')]


def tupleDistance(x, y):
    """Calculate tupleDistance between tuple values.

    :param x: (int, int, int), rgb tuple
    :param y: (int, int, int), rgb tuple
    :return: float, sum of distances between each pair of elements
    """
    assert len(x)==len(y)
    sum = 0
    for i in range(len(x)):
        sum += (x[i]-y[i])**2
    sum = sqrt(sum)
    return sum


def exprIsSafe(expr_string):
    """Returns whether the string is safe to 'eval()'.
    Detects improper use of '.' attribute access

    :param expr_string: string to check for safety
    :return: True if safe, False otherwise
    """
    assert isinstance(expr_string, str), 'Provide a string expression to verify is safe'
    string = 'expr_string'
    for r in '()+-*/':
        if r in expr_string:
            string += ".replace('" + r + "', ' " + r + " ')"
    expr_string = eval(string, globals(), {'expr_string':expr_string})

    # return re.search(r"((\d*((?=\D)\S)+\d*)+[.])|([.](\d*((?=\D)\S)+))", expr_string) is None
    # return re.search(r"((((?=\D)\S)+\d*)+[.])|([.]\d*((?=[\D])\S)+)", expr_string) is None
    return re.search(r"(((?=\D)\S)+\d*)+[.]|[.]\d*((?=[\D])\S)+", expr_string) is None


def applyDefaultArgs(kwargs, defaultargs):
    """Returns (dict, namespace) of defaultargs overridden by kwargs. Any keys in kwargs not in defaultargs
    raise a TypeError

    :param kwargs: dict of kwargs to process
    :param defaultargs: dict of defaults
    :return: dict, SimpleNamespace
    """
    unknown_args = kwargs.keys() - defaultargs.keys()
    if unknown_args:
        raise TypeError(f"Unknown argument(s): {unknown_args}")
    a = defaultargs.copy()
    a.update(kwargs)
    return a, SimpleNamespace(**a)


@property
def loggableQtName(self):
    """Property to identify instance when logging or when searching in Qt for this widget.
    See objectName for Qt Objects.

    :return: string, f"{type(self).__name__}:{self.objectName()}:"
        e.g. 'DraggableWidget:objectName:'
    """
    return f"{type(self).__name__}:{self.objectName()}:"


colorList = \
[(['aliceblue'], '#F0F8FF', (240, 248, 255)),
 (['antiquewhite'], '#FAEBD7', (250, 235, 215)),
 (['aqua', 'cyan'], '#00FFFF', (0, 255, 255)),
 (['aquamarine'], '#7FFFD4', (127, 255, 212)),
 (['azure'], '#F0FFFF', (240, 255, 255)),
 (['beige'], '#F5F5DC', (245, 245, 220)),
 (['bisque'], '#FFE4C4', (255, 228, 196)),
 (['black'], '#000000', (0, 0, 0)),
 (['blanchedalmond'], '#FFEBCD', (255, 235, 205)),
 (['blue'], '#0000FF', (0, 0, 255)),
 (['blueviolet'], '#8A2BE2', (138, 43, 226)),
 (['brown'], '#A52A2A', (165, 42, 42)),
 (['burlywood'], '#DEB887', (222, 184, 135)),
 (['cadetblue'], '#5F9EA0', (95, 158, 160)),
 (['chartreuse'], '#7FFF00', (127, 255, 0)),
 (['chocolate'], '#D2691E', (210, 105, 30)),
 (['coral'], '#FF7F50', (255, 127, 80)),
 (['cornflowerblue'], '#6495ED', (100, 149, 237)),
 (['cornsilk'], '#FFF8DC', (255, 248, 220)),
 (['crimson'], '#DC143C', (220, 20, 60)),
 (['darkblue'], '#00008B', (0, 0, 139)),
 (['darkcyan'], '#008B8B', (0, 139, 139)),
 (['darkgoldenrod'], '#B8860B', (184, 134, 11)),
 (['darkgray', 'darkgrey'], '#A9A9A9', (169, 169, 169)),
 (['darkgreen'], '#006400', (0, 100, 0)),
 (['darkkhaki'], '#BDB76B', (189, 183, 107)),
 (['darkmagenta'], '#8B008B', (139, 0, 139)),
 (['darkolivegreen'], '#556B2F', (85, 107, 47)),
 (['darkorange'], '#FF8C00', (255, 140, 0)),
 (['darkorchid'], '#9932CC', (153, 50, 204)),
 (['darkred'], '#8B0000', (139, 0, 0)),
 (['darksalmon'], '#E9967A', (233, 150, 122)),
 (['darkseagreen'], '#8FBC8F', (143, 188, 143)),
 (['darkslateblue'], '#483D8B', (72, 61, 139)),
 (['darkslategray', 'darkslategrey'], '#2F4F4F', (47, 79, 79)),
 (['darkturquoise'], '#00CED1', (0, 206, 209)),
 (['darkviolet'], '#9400D3', (148, 0, 211)),
 (['deeppink'], '#FF1493', (255, 20, 147)),
 (['deepskyblue'], '#00BFFF', (0, 191, 255)),
 (['dimgray', 'dimgrey'], '#696969', (105, 105, 105)),
 (['dodgerblue'], '#1E90FF', (30, 144, 255)),
 (['firebrick'], '#B22222', (178, 34, 34)),
 (['floralwhite'], '#FFFAF0', (255, 250, 240)),
 (['forestgreen'], '#228B22', (34, 139, 34)),
 (['gainsboro'], '#DCDCDC', (220, 220, 220)),
 (['ghostwhite'], '#F8F8FF', (248, 248, 255)),
 (['gold'], '#FFD700', (255, 215, 0)),
 (['goldenrod'], '#DAA520', (218, 165, 32)),
 (['gray', 'grey'], '#808080', (128, 128, 128)),
 (['green'], '#008000', (0, 128, 0)),
 (['greenyellow'], '#ADFF2F', (173, 255, 47)),
 (['honeydew'], '#F0FFF0', (240, 255, 240)),
 (['hotpink'], '#FF69B4', (255, 105, 180)),
 (['indianred'], '#CD5C5C', (205, 92, 92)),
 (['indigo'], '#4B0082', (75, 0, 130)),
 (['ivory'], '#FFFFF0', (255, 255, 240)),
 (['khaki'], '#F0E68C', (240, 230, 140)),
 (['lavender'], '#E6E6FA', (230, 230, 250)),
 (['lavenderblush'], '#FFF0F5', (255, 240, 245)),
 (['lawngreen'], '#7CFC00', (124, 252, 0)),
 (['lemonchiffon'], '#FFFACD', (255, 250, 205)),
 (['lightblue'], '#ADD8E6', (173, 216, 230)),
 (['lightcoral'], '#F08080', (240, 128, 128)),
 (['lightcyan'], '#E0FFFF', (224, 255, 255)),
 (['lightgoldenrodyellow'], '#FAFAD2', (250, 250, 210)),
 (['lightgray', 'lightgrey'], '#D3D3D3', (211, 211, 211)),
 (['lightgreen'], '#90EE90', (144, 238, 144)),
 (['lightpink'], '#FFB6C1', (255, 182, 193)),
 (['lightsalmon'], '#FFA07A', (255, 160, 122)),
 (['lightseagreen'], '#20B2AA', (32, 178, 170)),
 (['lightskyblue'], '#87CEFA', (135, 206, 250)),
 (['lightslategray', 'lightslategrey'], '#778899', (119, 136, 153)),
 (['lightsteelblue'], '#B0C4DE', (176, 196, 222)),
 (['lightyellow'], '#FFFFE0', (255, 255, 224)),
 (['lime'], '#00FF00', (0, 255, 0)),
 (['limegreen'], '#32CD32', (50, 205, 50)),
 (['linen'], '#FAF0E6', (250, 240, 230)),
 (['magenta', 'fuchsia'], '#FF00FF', (255, 0, 255)),
 (['maroon'], '#800000', (128, 0, 0)),
 (['mediumaquamarine'], '#66CDAA', (102, 205, 170)),
 (['mediumblue'], '#0000CD', (0, 0, 205)),
 (['mediumorchid'], '#BA55D3', (186, 85, 211)),
 (['mediumpurple'], '#9370DB', (147, 112, 219)),
 (['mediumseagreen'], '#3CB371', (60, 179, 113)),
 (['mediumslateblue'], '#7B68EE', (123, 104, 238)),
 (['mediumspringgreen'], '#00FA9A', (0, 250, 154)),
 (['mediumturquoise'], '#48D1CC', (72, 209, 204)),
 (['mediumvioletred'], '#C71585', (199, 21, 133)),
 (['midnightblue'], '#191970', (25, 25, 112)),
 (['mintcream'], '#F5FFFA', (245, 255, 250)),
 (['mistyrose'], '#FFE4E1', (255, 228, 225)),
 (['moccasin'], '#FFE4B5', (255, 228, 181)),
 (['navajowhite'], '#FFDEAD', (255, 222, 173)),
 (['navy'], '#000080', (0, 0, 128)),
 (['oldlace'], '#FDF5E6', (253, 245, 230)),
 (['olive'], '#808000', (128, 128, 0)),
 (['olivedrab'], '#6B8E23', (107, 142, 35)),
 (['orange'], '#FFA500', (255, 165, 0)),
 (['orangered'], '#FF4500', (255, 69, 0)),
 (['orchid'], '#DA70D6', (218, 112, 214)),
 (['palegoldenrod'], '#EEE8AA', (238, 232, 170)),
 (['palegreen'], '#98FB98', (152, 251, 152)),
 (['paleturquoise'], '#AFEEEE', (175, 238, 238)),
 (['palevioletred'], '#DB7093', (219, 112, 147)),
 (['papayawhip'], '#FFEFD5', (255, 239, 213)),
 (['peachpuff'], '#FFDAB9', (255, 218, 185)),
 (['peru'], '#CD853F', (205, 133, 63)),
 (['pink'], '#FFC0CB', (255, 192, 203)),
 (['plum'], '#DDA0DD', (221, 160, 221)),
 (['powderblue'], '#B0E0E6', (176, 224, 230)),
 (['purple'], '#800080', (128, 0, 128)),
 (['red'], '#FF0000', (255, 0, 0)),
 (['rosybrown'], '#BC8F8F', (188, 143, 143)),
 (['royalblue'], '#4169E1', (65, 105, 225)),
 (['saddlebrown'], '#8B4513', (139, 69, 19)),
 (['salmon'], '#FA8072', (250, 128, 114)),
 (['sandybrown'], '#F4A460', (244, 164, 96)),
 (['seagreen'], '#2E8B57', (46, 139, 87)),
 (['seashell'], '#FFF5EE', (255, 245, 238)),
 (['sienna'], '#A0522D', (160, 82, 45)),
 (['silver'], '#C0C0C0', (192, 192, 192)),
 (['skyblue'], '#87CEEB', (135, 206, 235)),
 (['slateblue'], '#6A5ACD', (106, 90, 205)),
 (['slategray', 'slategrey'], '#708090', (112, 128, 144)),
 (['snow'], '#FFFAFA', (255, 250, 250)),
 (['springgreen'], '#00FF7F', (0, 255, 127)),
 (['steelblue'], '#4682B4', (70, 130, 180)),
 (['tan'], '#D2B48C', (210, 180, 140)),
 (['teal'], '#008080', (0, 128, 128)),
 (['thistle'], '#D8BFD8', (216, 191, 216)),
 (['tomato'], '#FF6347', (255, 99, 71)),
 (['turquoise'], '#40E0D0', (64, 224, 208)),
 (['violet'], '#EE82EE', (238, 130, 238)),
 (['wheat'], '#F5DEB3', (245, 222, 179)),
 (['white'], '#FFFFFF', (255, 255, 255)),
 (['whitesmoke'], '#F5F5F5', (245, 245, 245)),
 (['yellow'], '#FFFF00', (255, 255, 0)),
 (['yellowgreen'], '#9ACD32', (154, 205, 50)),
 (['disabled-gray', 'disabled-grey'], '#F0F0F0', (240, 240, 240))
 ]


def hex_to_rgb(hex):
    """Convert a hex string to rgb tuple.

    :param hex: string, e.g. '#F0F0F0' or '0xf0f0f0'
    :return: (r, g, b)
    """
    hex = hex.split('#')[-1].split('0x')[-1]
    r = int(hex[:2], 16)
    g = int(hex[2:4], 16)
    b = int(hex[4:6], 16)
    return r, g, b


def rgb_to_hex(rgb):
    """Convert an rgb tuple to a hex string.

    :param rgb: (int, int, int), rgb tuple
    :return: string, hex color string, e.g. 'F0F0F0'
    """
    r, g, b = rgb[0], rgb[1], rgb[2]
    r, g, b = hex(r), hex(g), hex(b)
    r, g, b = r.split('0x')[-1].upper(), g.split('0x')[-1].upper(), b.split('0x')[-1].upper()
    if len(r) == 1:
        r = '0' + r
    if len(g) == 1:
        g = '0' + g
    if len(b) == 1:
        b = '0' + b
    return r+g+b


def findColor(color):
    """Finds a color in colorList by name, rgb, or hex string.
    If a name string is passed, it must match exactly.
    If rgb (int, int, int) tuple is passed, if no exact match, returns closest color
        by tupleDistance between values.
    If hex string passed, if no exact match, converts to rgb and runs with that tuple.

    :param color: hex string, color name string, or rgb (int, int, int)
    :return: ( [possible color name strings], hex string, (r,g,b) )
    """
    if isinstance(color, str) and (color.startswith('#') or color.startswith('0x')):
        for c in colorList:
            if c[1] == color:
                return c
        return findColor(hex_to_rgb(color))
    if isinstance(color, str):
        for c in colorList:
            for n in c[0]:
                if n.upper() == color.upper():
                    return c[0], c[1].upper(), c[2]
        return None
    if isinstance(color, tuple) and len(color) == 3 and all([isinstance(c, int) for c in color]):
        _min = 1.1e16
        _min_c = ''
        for c in colorList:
            if c[2] == color:
                return c[0], c[1].upper(), c[2]
        for c in colorList:
            d = tupleDistance(color, c[2])
            if d < _min:
                _min = d
                _min_c = c
        return (_min_c[0], _min_c[1].upper(), _min_c[2]) if _min_c else None
    raise TypeError("color: {} is not the correct format for query".format(color))


try:
    from PyQt5.QtGui import QPalette
except ImportError:
    pass
else:
    def getCurrentColor(widget, color='Window'):
        """Returns the 'color' portion of 'widget's QPalette.

        :param widget: widget to get color from
        :param color: str or QPalette.ColorRole, portion of widget to get color from
            e.g. 'Window' or 'WindowText' or QtGui.QPalette.Background or QtGui.QPalette.Foreground
        :return: ( [possible color name strings], hex string, (r,g,b) )
        """
        if isinstance(color, str):
            return findColor(widget.palette().color(QPalette.__getattribute__(QPalette, color)).name())
        elif isinstance(color, QPalette.ColorRole):
            return findColor(widget.palette().color(color).name())
        else:
            raise TypeError


__all__ = ['isFunc', 'getAllFuncs', 'getAllClasses', 'tupleDistance', 'exprIsSafe', 'applyDefaultArgs',
           'loggableQtName', 'hex_to_rgb', 'rgb_to_hex', 'findColor', 'getCurrentColor', 'colorList']
