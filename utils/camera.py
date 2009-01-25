from utils.locals import MAIN_VIEW

class Camera:
    """
    Models an opengl camera
    """
    def __init__(self, position=(0.,0.,0.), view=(0.,0.,0.), up=(0.,1.,0.)):
        self.position = {'x': position[0], 'y': position[1], 'z': position[2]}
        self.view     = {'x': view[0], 'y': view[1], 'z': view[2]}
        self.up       = {'x': up[0], 'y': up[1], 'z': up[2]}
        # initialize with the main view.
        self.set(MAIN_VIEW)

    def __unicode__(self):
        args = self.to_args()
        return 'POSITION: %s  VIEW: %s' % (args[:3], args[3:6])
    __str__ = __unicode__

    def to_args(self):
        """
        return a tuple of its values to be passed as arguments to a function
        """
        return (self.position['x'], self.position['y'], self.position['z']) + \
               (self.view['x'], self.view['y'], self.view['z']) + \
               (self.up['x'], self.up['y'], self.up['z'])
# WTF?!
#        return tuple(self.position.values()) + \
#               tuple(self.view.values()) + \
#               tuple(self.up.values())

    def set(self, view_dict):
        """
        set the camera view, given a representive dict
        """
        if view_dict.has_key('position'):
            self.position = view_dict['position'].copy()
        if view_dict.has_key('view'):
            self.view = view_dict['view'].copy()
        if view_dict.has_key('up'):
            self.up = view_dict['up'].copy()
        return self
