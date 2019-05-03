import wx
import numpy as np
from wx import glcanvas
from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *
import OpenGL.GL.shaders


class OpenGLCanvas(glcanvas.GLCanvas):
    def __init__(self, parent):
        glcanvas.GLCanvas.__init__(self, parent, -1, size=(1120, 630))
        self.init = False
        self.context = glcanvas.GLContext(self)
        self.SetCurrent(self.context)
        self.Bind(wx.EVT_PAINT, self.OnPaint)

    def OnPaint(self, event):
        if not self.init:
            self.InitGL()
            self.init = True
        self.OnDraw()

    def InitGL(self):
        # Vertices, Colors
        glClearColor(1,0,0,1)

    def draw_rect(self, x, y, width, height):
        glBegin(GL_QUADS)                                  # start drawing a rectangle
        glVertex2f(x, y)                                   # bottom left point
        glVertex2f(x + width, y)                           # bottom right point
        glVertex2f(x + width, y + height)                  # top right point
        glVertex2f(x, y + height)                          # top left point
        glEnd()

    def refresh2d(self):
        width = 1280
        height = 720
        glViewport(0, 0, width, height)
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        glOrtho(0.0, width, 0.0, height, 0.0, 1.0)
        glMatrixMode (GL_MODELVIEW)
        glLoadIdentity()


    def OnDraw(self):
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT) # clear the screen
        glLoadIdentity()                                   # reset position
        self.refresh2d()                           # set mode to 2d
            
        glColor3f(0.0, 0.0, 1.0)                           # set color to blue
        self.draw_rect(10, 10, 200, 100)                        # rect at (10, 10) with width 200, height 100
        
        self.SwapBuffers() 


class MyFrame(wx.Frame):
    def __init__(self):
        self.size = (1280, 720)
        wx.Frame.__init__(self, None, title="A frame", size=self.size)
        self.canvas = OpenGLCanvas(self)

class MyApp(wx.App):
    def OnInit(self):
        frame = MyFrame()
        frame.Show()
        return True

if __name__ == "__main__":
    app = MyApp()
    app.MainLoop()