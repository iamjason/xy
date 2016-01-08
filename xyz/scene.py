from matrix import Matrix
import itertools
import util

class Scene(object):

    def __init__(self, shapes=None):
        self.shapes = shapes or []

    def add(self, shape):
        self.shapes.append(shape)

    def paths(self):
        result = []
        for shape in self.shapes:
            result.extend(shape.paths())
        return result

    def intersect(self, o, d):
        ts = [x.intersect(o, d) for x in self.shapes]
        ts = [x for x in ts if x is not None]
        return min(ts) if ts else None

    def clip_paths(self, eye, step):
        paths = self.paths()
        result = []
        for path in paths:
            result.extend(self.clip(path, eye, step))
        return result

    def clip(self, path, eye, step):
        result = []
        points = util.chop(path, step)
        visible = [self.visible(eye, point) for point in points]
        items = zip(visible, points)
        for visible, group in itertools.groupby(items, lambda x: x[0]):
            points = [x[1] for x in group]
            if visible and len(points) > 1:
                result.append(points)
        return result

    def visible(self, eye, point):
        v = util.sub(eye, point)
        o = point
        d = util.normalize(v)
        t = self.intersect(o, d)
        if t is not None and t < util.length(v):
            return False
        return True

    def render(self, eye, center, up, fovy, aspect, znear, zfar, step=None):
        def inside(p):
            x, y, z = p
            return -1 <= x <= 1 and -1 <= y <= 1 and -1 <= z <= 1
        if step is None:
            paths = self.paths()
        else:
            paths = self.clip_paths(eye, step)
        m = Matrix().look_at(eye, center, up)
        m = m.perspective(fovy, aspect, znear, zfar)
        paths = [[(m * (x, y, z, 1)) for x, y, z in path] for path in paths]
        paths = [[util.div_scalar(p, p[3])[:3] for p in path] for path in paths]
        paths = [[p[:2] for p in path if inside(p)] for path in paths]
        paths = filter(None, paths)
        return paths
