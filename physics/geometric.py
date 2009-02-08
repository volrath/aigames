from math import sqrt

class Point:
    """
    Singleton class for points-related functions
    """
    @classmethod
    def distance(self, p1, p2):
        """
        Get the Euclidean distance between two points.
        Points are represented by tuples (x-coord, y-coord)
        """
        return sqrt( sum([(a-b)**2 for a,b in zip(p1,p2)]) )

    @classmethod
    def is_between(self, p, seg):
        """
        Returns true if the point p is between the segment
        """
        return (self.collinear(seg[0], seg[1], p)
                and (self.within(seg[0][0], p[0], seg[1][0]) if seg[0][0] != seg[1][0] else
                     self.within(seg[0][1], p[1], seg[1][1])))

    @classmethod
    def collinear(self, a, b, c):
        "Return true iff a, b, and c all lie on the same line."
        return (b[0] - a[0]) * (c[1] - a[1]) == (c[0] - a[0]) * (b[1] - a[1])
    
    @classmethod
    def within(self, p, q, r):
        "Return true iff q is between p and r (inclusive)."
        return p <= q <= r or r <= q <= p
