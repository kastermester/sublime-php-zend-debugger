import bisect
import sublime


def subtract_region(r1, r2):
    if not r1.contains(r2):
        r2 = r1.intersection(r2)

    r1s, r1e = r1.begin(), r1.end()
    r2s, r2e = r2.begin(), r2.end()

    if r1s == r2s and r1e == r2e:
        return []
    elif r1s == r2s:
        return [sublime.Region(r2e, r1e)]
    elif r1e == r2e:
        return [sublime.Region(r1s, r2s)]
    else:
        return [sublime.Region(r1s, r2s), sublime.Region(r2e, r1e)]


class PyRegionSet(list):

    def __init__(self, l=[], merge=False):
        if merge:
            list.__init__(self)
            for r in l:
                self.add(l)
        else:
            list.__init__(self, l)

    def bisect(self, r):
        ix = min(bisect.bisect(self, r), len(self) - 1)
        reg = self[ix]
        if r < reg and not (reg.contains(r) or reg.intersects(r)):
            ix -= 1
        return max(0, ix)

    def clear(self):
        del self[:]

    def contains(self, r):
        return self and self.closest_selection(r).contains(r)

    def closest_selection(self, r):
        return self[self.bisect(r)]

    def add(self, r):
        if not self:
            return self.append(r)

        for ix in range(self.bisect(r), -1, -1):
            closest = self[ix]

            if closest.contains(r) or closest.intersects(r):
                self[ix] = closest.cover(r)
                return

            elif r.contains(closest) or r.intersects(closest):
                r = r.cover(closest)
                if ix:
                    del self[ix]
                else:
                    self[ix] = r
            else:
                self.insert(ix+1, r)
                return

    def subtract(self, r):
        ix = self.bisect(r)

        while self:
            closest = self[ix]

            if closest.contains(r) or closest.intersects(r):
                del self[ix]
                for reg in subtract_region(closest, r):
                    bisect.insort(self, reg)

                if ix == len(self):
                    break
                continue
            break
