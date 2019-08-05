
import asyncio
import numpy as np
import matplotlib.pyplot as plt
import os

from vuejspython import model, start


@model
class Comp:
    # define properties to forward to vue (or not)
    i = 42
    fname = ""

    def __init__(self):
        self.i = 1

    def watch_i(self, i):
        d = ",,ex4"
        if not os.path.exists(d):
            os.makedirs(d)
        fname = d+"/fname-"+str(self.i)+".svg"
        x = np.linspace(0, 100, 1000)
        y = x-i
        y[y<0] = 0
        plt.figure()
        plt.grid()
        plt.plot(x, y)
        plt.savefig(fname)
        plt.close()
        self.fname = fname


start(Comp())
