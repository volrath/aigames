from math import sqrt

from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *

from physics.rect import Rect
from physics.vector3 import Vector3
import graphics

class Floor(object):
    def __init__(self, floor):
        self.area = Rect((0, 0), floor*2, floor*2)
        #surface = pygame.image.load("stage_surface.png")
        self.size = floor

    def render(self):
        glPushMatrix()
        glTranslatef(0., -self.size, 0.)
	glBegin(GL_QUADS)
	glColor3f(60./255, 60./255, 60./255)		# Set The Color To Dark Grey
	glVertex3f( self.size, self.size,-self.size)		# Top Right Of The Quad (Top)
	glVertex3f(-self.size, self.size,-self.size)		# Top Left Of The Quad (Top)
	glVertex3f(-self.size, self.size, self.size)		# Bottom Left Of The Quad (Top)
	glVertex3f( self.size, self.size, self.size)		# Bottom Right Of The Quad (Top)

	glColor3f(90./255, 90./255, 90./255)			# Set The Color To Red
	glVertex3f( self.size, self.size, self.size)		# Top Right Of The Quad (Front)
	glVertex3f(-self.size, self.size, self.size)		# Top Left Of The Quad (Front)
	glVertex3f(-self.size,-self.size, self.size)		# Bottom Left Of The Quad (Front)
	glVertex3f( self.size,-self.size, self.size)		# Bottom Right Of The Quad (Front)

	glColor3f(0.0,0.0,1.0)			# Set The Color To Blue
	glVertex3f(-self.size, self.size, self.size)		# Top Right Of The Quad (Left)
	glVertex3f(-self.size, self.size,-self.size)		# Top Left Of The Quad (Left)
	glVertex3f(-self.size,-self.size,-self.size)		# Bottom Left Of The Quad (Left)
	glVertex3f(-self.size,-self.size, self.size)		# Bottom Right Of The Quad (Left)

	glEnd()				# Done Drawing The Quad
        glPopMatrix()

class Obstacle(object):
    def __init__(self, size=1, position=Vector3(), color=(1.,1.,1.),
                 rotation=0.):
        self.area = Rect((position.x, position.z), size, size)
        self.size = size
        self.mass = size**4
        self.height = size*2
        self.position = position
        self.velocity = Vector3()
        self.color = color
        self.rotation = rotation
        self.radius = size - (sqrt(2 * size**2)) / 4

    def render(self):
        glPushMatrix()
        glTranslatef(self.position.x, self.size/2., self.position.z)
        glRotatef(self.rotation, 0., 1., 0.)
        glColor3f(*self.color)
        glutSolidCube(self.size)
        glPopMatrix()
        graphics.draw_circle(self.position, self.radius, (195./255, 1./255, 243./255))
        self.velocity.set_length(0)


class SideAmplificator(Obstacle):
    """
    An amplificator on the side of the stage.
    """
    def __init__(self, position, *args, **kwargs):
        super(SideAmplificator, self).__init__(position=position, size=5,
                                               color=(34/255., 38/255., 41/255.),
                                               *args, **kwargs)


class MainAmplificator(Obstacle):
    """
    Amplificator in front of the stage.
    """
    def __init__(self, position, rotation, *args, **kwargs):
        super(MainAmplificator, self).__init__(position=position, size=6,
                                               rotation=rotation,
                                               color=(22/255., 26/255., 30/255.),
                                               *args, **kwargs)
        

class Stage(object):
    def __init__(self, floor_size):
        self.floor = Floor(floor_size)
        self.obstacles = []
        self.display_list = None

    def set_level(self, obstacles):
        """
        Set the game level's obstacles
        """
        self.obstacles = obstacles

    def render(self):
        if self.display_list is None:
            # Create a display list
            self.display_list = glGenLists(1)
            glNewList(self.display_list, GL_COMPILE)

            # Draw the stage
            self.floor.render()

            for obstacle in self.obstacles:
                obstacle.render()

            glEndList()
        else:
            glCallList(self.display_list)
