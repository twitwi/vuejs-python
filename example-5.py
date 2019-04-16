
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
    svg = ""
    png = ""
    use_svg = True
    use_png = True
    show_points = True
    show_nn = True

    def __init__(self):
        self.draw_dataset()
        

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

    def watch_show_points(self, _): self.watch_gamma(self.gamma)
    def watch_show_nn(self, _):     self.watch_gamma(self.gamma)
    
    def watch_gamma(self, ga):
        x = self.x
        y = self.y
        im = self.im
        xp, yp = self.xp, self.yp
        xm, ym = self.xm, self.ym
        plt.figure()
        if self.show_nn:
            CS = plt.contour(im, extent=[x.min(), x.max(), y.min(), y.max()], levels=[1], colors=['k'], linewidths=[3])
        CS = plt.contour(im, extent=[x.min(), x.max(), y.min(), y.max()], levels=[ga])
        ###plt.clabel(CS)
        plt.xlim([x.min(), x.max()])
        plt.ylim([y.min(), y.max()])
        if self.show_points:
            plt.scatter(xp, yp, marker='+')
            plt.scatter(xm, ym, marker='.')
        plt.xticks([]) ; plt.yticks([])
        if self.use_png:
            b = io.BytesIO()
            plt.savefig(b, format="png")
            self.png = base64.b64encode(b.getvalue()).decode()
            b.close()
        if self.use_svg:
            s = io.StringIO()
            plt.savefig(s, format="svg")
            self.svg = s.getvalue()
            s.close()
        plt.close()
            

start(Comp())
