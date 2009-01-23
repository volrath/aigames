from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *

class Floor:
    def __init__(self, floor):
        #surface = pygame.image.load("stage_surface.png")
        self.floor_size = floor

    def render(self):
        glPushMatrix()
        glTranslatef(0., -self.floor_size, 0.)
	glBegin(GL_QUADS)
	glColor3f(60./255, 60./255, 60./255)		# Set The Color To Dark Grey
	glVertex3f( self.floor_size, self.floor_size,-self.floor_size)		# Top Right Of The Quad (Top)
	glVertex3f(-self.floor_size, self.floor_size,-self.floor_size)		# Top Left Of The Quad (Top)
	glVertex3f(-self.floor_size, self.floor_size, self.floor_size)		# Bottom Left Of The Quad (Top)
	glVertex3f( self.floor_size, self.floor_size, self.floor_size)		# Bottom Right Of The Quad (Top)

	glColor3f(90./255, 90./255, 90./255)			# Set The Color To Red
	glVertex3f( self.floor_size, self.floor_size, self.floor_size)		# Top Right Of The Quad (Front)
	glVertex3f(-self.floor_size, self.floor_size, self.floor_size)		# Top Left Of The Quad (Front)
	glVertex3f(-self.floor_size,-self.floor_size, self.floor_size)		# Bottom Left Of The Quad (Front)
	glVertex3f( self.floor_size,-self.floor_size, self.floor_size)		# Bottom Right Of The Quad (Front)

	glColor3f(0.0,0.0,1.0)			# Set The Color To Blue
	glVertex3f(-self.floor_size, self.floor_size, self.floor_size)		# Top Right Of The Quad (Left)
	glVertex3f(-self.floor_size, self.floor_size,-self.floor_size)		# Top Left Of The Quad (Left)
	glVertex3f(-self.floor_size,-self.floor_size,-self.floor_size)		# Bottom Left Of The Quad (Left)
	glVertex3f(-self.floor_size,-self.floor_size, self.floor_size)		# Bottom Right Of The Quad (Left)

	glEnd()				# Done Drawing The Quad
        glPopMatrix()

class Amplificator:
    def __init__(self, size=1, position=(0,0), color=(1.,1.,1.), rotation=0):
        self.size = size
        self.xpos, self.zpos = position
        self.color = color
        self.rotation = rotation

    def render(self):
        glPushMatrix()
        glTranslatef(self.xpos, self.size/2., self.zpos)
        glRotatef(self.rotation, 0., 1., 0.)
        glColor3f(*self.color)
        glutSolidCube(self.size)
        glPopMatrix()

class Stage:
    def __init__(self, floor_size):
        self.floor = Floor(floor_size)

    def default_amplificators(self):
        """
        Set 2 amplificator in the default position
        """
        self.amps = [
            Amplificator(size=5., position=(15.5, 7.), color=(1.,0.,0.), rotation=35),
            Amplificator(size=5., position=(-15.5, 7.), color=(1.,0.,0.), rotation=-35),
            ]
        return self

    def render(self):
        self.floor.render()
        for amp in self.amps:
            amp.render()
