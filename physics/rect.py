class Rect(object):
    def __init__(self, left, top, width, height):
        self.left   = float(left)
        self.top    = float(top)
        self.width  = float(width)
        self.height = float(height)
        # Rect instances will have virtual attributes such as right and bottom
        # and attributes to modify the rectangle by its vertices (top_left,
        # top_right, bottom_left and bottom_right, center)

    def _get_left(self):
        return self.left

    def _get_top(self):
        return self.top

    def _get_width(self):
        return self.width

    def _get_height(self):
        return self.height

    def _set_left(self, value):
        self.left = value

    def _set_top(self, value):
        self.top = value

    def _set_width(self, value):
        self.width = value

    def _set_height(self, value):
        self.height = value

    _getters = (_get_left, _get_top, _get_width, _get_height)
    _setters = (_set_left, _set_top, _set_width, _set_height)

    def _get_right(self):
        return self.left + self.width

    def _set_right(self, value):
        assert self.left < value, "Right side must be greater than left side"
        self.width = self.left + value
    
    right = property(_get_right, _set_right, None, "rectangle's right side.")

    def _get_bottom(self):
        return self.top + self.height

    def _set_bottom(self, value):
        assert self.top < value, "Bottom side must be greater than top side"
        self.height = self.top + value
    
    bottom = property(_get_bottom, _set_bottom, None, "rectangle's bottom side.")

    def _get_center(self):
        return (self.left+self.right/2), (self.top+self.bottom/2)

    def _set_center(self, value):
        assert isinstance( value, tuple ), "Center must be a tuple of the form\
        (x_coord, y_coord)"
        self.left = self.width/2 - value[0]
        self.top  = self.height/2 - value[1]
    
    center = property(_get_center, _set_center, None, "rectangle's center point.")

    def _get_top_left(self):
        return self.left, self.top

    def _set_top_left(self, value):
        assert isinstance( value, tuple ), "Coordinates must be a tuple of the\
        form (x_coord, y_coord)"
        self.left = value[0]
        self.top  = value[1]
    
    top_left = property(_get_top_left, _set_top_left, None, "rectangle's\
    (top, left) coordinate.")

    def _get_size(self):
        return self.width, self.height

    def _set_size(self, value):
        assert isinstance( value, tuple ), "Center must be a tuple of the form\
        (x_coord, y_coord)"
        self.width  = value[0]
        self.height = value[1]
    
    size = property(_get_size, _set_size, None, "rectangle's size.")

    ## TO DO: implement the rest of virtual attributes

    def _as_tuple(self):
        return self.left, self.top, self.width, self.height

    def __str__(self):
        return "(left: %s, top: %s, width: %s, height: %s)" % self._as_tuple()

    def __repr__(self):
        return "Rect%s" % self.__str__()

    def copy(self):
        """
        Returns a copy of this rectangle.
        """
        nr = self.__class__(*self._as_tuple())
        return nr
    __copy__ = copy

    def move(self, x, y):
        """
        Moves the rectangle in place
        """
        self.left   += x
        self.top    += y
        self.width  += x
        self.height += y

    def move_dup(self, x, y):
        """
        Returns a copy of this rectangle moved
        """
        nr = self.copy()
        nr.move(x, y)
        return nr

    def inflate(self, x, y):
        """
        Grow or shrink the rectangle size in place
        """
        self.width  += x
        self.height += y

    def inflate_dup(self, x, y):
        """
        Returns a copy of this rectangle and applies inflate to it
        """
        nr = self.copy()
        nr.inflate(x, y)
        return nr

    def clamp(self, r):
        """
        Moves the rectangle to be completely inside the argument Rect.
        If the rectangle is too large to fit inside, it is centered inside
        the argument, but its size is not changed.
        """
        if self.width > r.width or self.height > r.height:
            self.center = r.center
        else:
            self.top_left = r.top_left

    def clamp_dup(self, r):
        """
        Same as clamp but returns a duplicate
        """
        nr = self.copy()
        nr.clamp(r)
        return nr

    def clip(self, r):
        """
        Returns a new rectangle that is cropped to be completely inside the
        argument Rect. If the two rectangles do not overlap to begin with,
        a Rect with 0 size is returned.
        """
        # Check if the left side is intersected
        if self.left >= r.left and self.left < r.right:
            left = self.left
        elif self.left < r.left and r.left < self.right:
            left = r.left
        else:
            return self.__class__(self.left, self.top, 0, 0)

        # Check if the right side is intersected to get the width
        if self.right > r.left and self.right <= r.right:
            width = self.right - left
        elif r.right > self.left and r.right <= self.right:
            width = r.right - left;
        else:
            return self.__class__(self.left, self.top, 0, 0)

        # Check if the top side is intersected
        if self.top >= r.top and self.top < r.bottom:
            top = self.top
        elif self.top < r.top and r.top < self.bottom:
            top = r.top
        else:
            return self.__class__(self.left, self.top, 0, 0)

        # Check if the bottom side is intersected to get the height
        if self.bottom > r.top and self.bottom <= r.bottom:
            height = self.bottom - top
        elif r.bottom > self.top and r.bottom <= self.bottom:
            height = r.bottom - top;
        else:
            return self.__class__(self.left, self.top, 0, 0)

        return self.__class__(left, top, width, height)

    def union(self, r):
        """
        Returns a new rectangle that completely covers the area of the two
        provided rectangles. There may be area inside the new Rect that is not
        covered by the originals.
        """
        left = min(self.left, r.left)
        top = min(self.top, r.top)
        right = max(self.right, r.right)
        bottom = max(self.bottom, r.bottom)
        return self.__class__(left, top, right-left, bottom-top)

    def union_all(self, r_seq):
        """
        Returns the union of one rectangle with a sequence of many rectangles.
        """
        pass

    def contains(self, r):
        """
        Returns true when the argument is completely inside the rectangle.
        """
        return self.left < r.left and self.top < r.top and \
               self.right > r.right and self.bottom > r.bottom

    def collide_point(self, x, y):
        """
        Returns true if the given point is inside the rectangle. A point along
        the right or bottom edge is not considered to be inside the rectangle.
        """
        return self.left < x and self.top < y and \
               self.right > x and self.bottom > y

    def collide_rect(self, r):
        """
        Returns true if any portion of either rectangle overlap (except the
        top+bottom or left+right edges).
        """
        return self.collide_point(r.top_left) or \
               self.collide_point(r.top_right) or \
               self.collide_point(r.bottom_left) or \
               self.collide_point(r.bottom_right)
