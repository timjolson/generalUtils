
def draw_circle(img, center, radius, color, thickness=None):
    height, width = img.shape
    xc, yc = center

    xc, yc, radius, thickness = int(xc), int(yc), int(radius), int(thickness) if thickness is not None else 0

    def fill_line(x0, x1, y):
        if y>=0 and y < height:
            minx, maxx = max(min(x0,width), 0), min(max(x1,0), width)
            img[y, minx:maxx] = color

    def color_pixel(x, y):
        if x >= 0 and y >= 0 and x < width and y < height:
            img[y][x] = color

    thickness = thickness if (thickness is not None and thickness != 0) else 1

    if thickness>1:
        draw_circle(img, center, radius+thickness, color, -1)
        draw_circle(img, center, radius, 0, -1)
    else:
        dx, dy = radius, 0
        err = 1 - dx

        if thickness == 1:
            while dx >= dy:
                color_pixel(dx + xc, dy + yc)  # 1
                color_pixel(dy + xc, dx + yc)  # 2
                color_pixel(-dy + xc, dx + yc)  # 3
                color_pixel(-dx + xc, dy + yc)  # 4
                color_pixel(-dx + xc, -dy + yc)  # 5
                color_pixel(-dy + xc, -dx + yc)  # 6
                color_pixel(dx + xc, -dy + yc)  # 7
                color_pixel(dy + xc, -dx + yc)  # 8

                dy += 1
                if (err < 0):
                    err += 2 * dy + 1
                else:
                    dx -= 1
                    err += 2 * (dy - dx + 1)
        else:
            while (dx >= dy):
                fill_line(xc - dx, xc + dx, yc + dy)  # bottom big
                fill_line(xc - dx, xc + dx, yc - dy)  # top big
                fill_line(xc - dy, xc + dy, yc + dx)  # bottom small
                fill_line(xc - dy, xc + dy, yc - dx)  # top small

                dy += 1
                if (err < 0):
                    err += 2 * dy + 1
                else:
                    dx -= 1
                    err += 2 * (dy - dx + 1)
    return img

# try:
#     import matplotlib.pyplot as plt
#     import numpy as np
# except ImportError:
#     pass
# else:


def plot3d(x, y, z, fig=None, zlim=(-10, 10)):
    """
    obj = plot3d(...)
    obj.show()
    """
    import matplotlib.pyplot as plt
    import numpy as np

    if fig is None:
        fig = plt.figure()

    ax = plt.axes(projection='3d')
    x, y = np.meshgrid(x, y)
    ax.plot_surface(x, y, z)
    ax.set_zlim(*zlim)
    return fig


def flatten(base, *layers):
    for mask in layers[::-1]:
        startx, starty = int(mask.x+mask.offset), int(mask.y+mask.offset)
        endy = min(base.shape[0] - starty, mask.shape[0])
        endx = min(base.shape[1] - startx, mask.shape[1])
        # print('{},{}'.format(starty, startx))
        # print('{},{}'.format(endy, endx))

        # for r, row in enumerate(mask):
        #     R = r + starty
        #     # print('r {}'.format(R))
        #     if R>=0 and R<base.shape[0]:
        #         # print('row {}'.format(row))
        #         for c, val in enumerate(row):
        #             C = c + startx
        #             # print('c {}'.format(C))
        #             if C>=0 and C<base.shape[1]:
        #                 # print('val {}'.format(val))
        #                 # print('*** {} {} {}'.format(r+starty, c+startx, base[r+starty][c+startx] +val))
        #                 base[R].__setitem__(C, base[R][C] + val)

        [[base[r+starty].__setitem__(c+startx, base[r+starty][c+startx] + val)
           for c,val in enumerate(row) if c+startx>=0 and c+startx<base.shape[1]]
            for r, row in enumerate(mask) if r+starty>=0 and r+starty<base.shape[0]]

        # [print(row) for row in mask]
        # [[base[r+starty].__setitem__(c+startx, base[r+starty][c+startx]+val) for c, val in enumerate(row)] for r, row in enumerate(mask)]
        # [[[print(item) for item in row] for row in col] for col in mask]

        # for y in np.arange(0, min(base.shape[0] - starty, mask.shape[0]), 1):
        #     for x in np.arange(0, min(base.shape[1] - startx, mask.shape[1]), 1):
        #         if y + starty >= 0 and x + startx >= 0:
        #             base[y + starty][x + startx] += mask[y][x]

        # for y in np.arange(0, min(base.shape[0] - starty, mask.shape[0]), 1):
        #     y += starty
        #     if y >=0 :
        #         for x in np.arange(0, min(base.shape[1] - startx, mask.shape[1]), 1):
        #             x += startx
        #             if x >= 0:
        #                 base[y][x] += mask[y][x]

    return base

__all__ = ['draw_circle', 'plot3d', 'flatten']
