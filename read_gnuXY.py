def x_and_y(filename):
    xs = []; ys = []
    for l in open(filename).readlines():
        x, y = [int(s) for s in l.split()]
        xs.append(x)
        ys.append(y)
    return xs, ys

