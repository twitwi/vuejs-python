
import asyncio
from vuejspython import model, start

import numpy as np
import matplotlib.pyplot as plt
import io
import base64

@model
class Comp:
    # define properties to forward to vue (or not)
    gamma = 1.0
    show_points = True
    show_nn = True
    im = np.zeros((1,))
    xp = np.zeros((1,))
    yp = np.zeros((1,))
    xm = np.zeros((1,))
    ym = np.zeros((1,))

    def __init__(self):
        self.draw_dataset()

    def computed_xmin(self): return self.x.min()
    def computed_xmax(self): return self.x.max()
    def computed_dx(self): return (self.x.max() - self.x.min()) / (np.sum(self.x.shape)-1)
    def computed_ymin(self): return self.y.min()
    def computed_ymax(self): return self.y.max()
    def computed_dy(self): return (self.y.max() - self.y.min()) / (np.sum(self.y.shape)-1)

    def draw_dataset(self):
        self.y = np.linspace(-0.87, 0.87, 103)[None, :, None]
        self.x = np.linspace(-1.3, 1.3, 91)[:, None, None]
        self.xp = np.array([0, 0.75])[None,None,:]
        self.yp = np.array([0, 0])[None,None,:]
        rangle = np.random.uniform(0, np.pi*4/3, (1, 1, 300))
        rradius = np.random.uniform(1, 1.7, rangle.shape)
        self.xm = rradius * np.cos(rangle)
        self.ym = rradius*4/6 * np.sin(rangle)
        d1m = np.min( ((self.x-self.xm)**2 + (self.y-self.ym)**2)**0.5, axis=2)
        d1p = np.min( ((self.x-self.xp)**2 + (self.y-self.yp)**2)**0.5, axis=2)
        s = d1m/(d1p+.0001)
        self.im = np.transpose(s)



start(Comp())
