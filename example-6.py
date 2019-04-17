
import asyncio
from vuejspython import model, start, atomic

import numpy as np
import matplotlib.pyplot as plt
import io
import base64

@model
class Comp:
    # define properties to forward to vue (or not)
    im = np.zeros((1,))
    xp = np.zeros((1,))
    yp = np.zeros((1,))
    xm = np.zeros((1,))
    ym = np.zeros((1,))
    _v_nobroadcast = ['d1m', 'd1p']

    def __init__(self):
        self.draw_set2pluses()
        self.draw_dataset()

    def computed_xmin(self): return self.x.min()
    def computed_xmax(self): return self.x.max()
    def computed_dx(self): return (self.x.max() - self.x.min()) / (np.prod(self.x.shape)-1)
    def computed_ymin(self): return self.y.min()
    def computed_ymax(self): return self.y.max()
    def computed_dy(self): return (self.y.max() - self.y.min()) / (np.prod(self.y.shape)-1)
    def computed_d1m(self): return np.min( ((self.x-self.xm)**2 + (self.y-self.ym)**2)**0.5, axis=2)
    def computed_d1p(self): return np.min( ((self.x-self.xp)**2 + (self.y-self.yp)**2)**0.5, axis=2)
    def computed_im(self): return np.transpose(self.d1m / (self.d1p+.0001))

    @atomic
    def draw_dataset(self):
        self.x = np.linspace(-1.3, 1.3, 191)[:, None, None]
        self.y = np.linspace(-0.87, 0.87, 203)[None, :, None]
        rangle = np.random.uniform(0, np.pi*4/3, (1, 1, 300))
        rradius = np.random.uniform(1, 1.7, rangle.shape)
        self.xm = rradius * np.cos(rangle)
        self.ym = rradius*4/6 * np.sin(rangle)

    @atomic
    def draw_bonedataset(self, t='bone', N=300):
        x = np.linspace(-1.3, 1.3, 1000)[:,None]
        y = np.linspace(-0.6, 0.6, 600)[None,:]
        if t == 'bone':
            candidate = (y/0.5)**2 + (x)**2 > 1
            candidate |= ((y-0.5)/0.4)**2 + (x/0.5)**2 < 1
            candidate |= ((y+0.5)/0.4)**2 + (x/0.5)**2 < 1
        else:
            candidate = (y/0.5)**2 + (x)**2 > 1
        candx,candy = np.where(candidate)
        candind = np.random.choice(range(candx.shape[0]), N, replace=False)
        self.xm = x[None,None,candx[candind],0]
        self.ym = y[None,None,0,candy[candind]]

    @atomic
    def draw_set2pluses(self):
        self.xp = np.array([0, 0.75])[None,None,:]
        self.yp = np.array([0, 0])[None,None,:]

    @atomic
    def draw_somepluses(self, N=20):
        self.xp = np.random.uniform(self.xmin, self.xmax, (1,1,N))
        self.yp = np.random.uniform(self.ymin, self.ymax, (1,1,N))

start(Comp())
