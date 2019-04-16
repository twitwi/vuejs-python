
import asyncio
import numpy as np
import matplotlib.pyplot as plt

from vuejspython import model, start


@model
class Comp:
    # define properties to forward to vue (or not)
    gamma = 1.0
    fname = ""

    def __init__(self):
        self.draw_dataset()

    def draw_dataset(self):
        self.y = np.linspace(-0.87, 0.87, 1003)[None, :, None]
        self.x = np.linspace(-1.3, 1.3, 901)[:, None, None]
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
        
    def watch_gamma(self, ga):
        fname = ",,fname-"+str(ga)+".svg"
        x = self.x
        y = self.y
        im = self.im
        xp, yp = self.xp, self.yp
        xm, ym = self.xm, self.ym
        plt.figure()
        #CS = plt.contour(im, extent=[x.min(), x.max(), y.min(), y.max()], levels=[1], colors=['k'], linewidths=[3])
        CS = plt.contour(im, extent=[x.min(), x.max(), y.min(), y.max()], levels=[ga])
        #plt.clabel(CS)
        plt.xlim([x.min(), x.max()])
        plt.ylim([y.min(), y.max()])
        #plt.scatter(xp, yp, marker='+')
        #plt.scatter(xm, ym, marker='.')
        plt.xticks([]) ; plt.yticks([])
        plt.savefig(fname)
        self.fname = fname
        

start(Comp())
