
import asyncio
from reactive.ObservableDict import ObservableDict

import vuejspython
import numpy as np

@vuejspython.model # this annotation could start the things automatically (if there is a single model anyway)
class Comp:
    # define properties to forward to vue (or not)
    currentClass = 0
    currentShapelet = 0
    currentImage = ''
    folder, groups, scale = 'unzip-nouveau', [30, 30, 30], 100
    #folder, groups, scale = 'epoch8000', [40, 40, 40], 1
    _v_nobroadcast = ['wa']

    def __init__(self):
        # can add local properties here (to avoid having to fill _novue)
        self.weight_dense = np.genfromtxt(self.folder+'/weight_dense.txt')
        self.activations = np.hstack([
            np.genfromtxt(self.folder+'/mp_shapelet_group_'+str(i)+'.txt') for i in range(len(self.groups))
        ])

    def computed_wa(self):
        a = self.activations   # ts, sh
        w = self.weight_dense  # sh, cl
        wa = a[:,:,None] * w[None, :, :]  # ts, sh, cl
        return wa

    def computed_importance(self):
        cc = self.currentClass
        n_c = self.weight_dense.shape[1]
        wa = self.wa
        mean_others = wa[:, :, np.arange(n_c) != cc].mean(axis=2)
        return np.mean(wa[:,:,cc] - mean_others, axis=0) * self.scale

    def computed_importance2(self):
        cc = self.currentClass
        n_c = self.weight_dense.shape[1]
        wa = self.wa
        max_others = wa[:, :, np.arange(n_c) != cc].max(axis=2)
        return np.mean(wa[:,:,cc] - max_others, axis=0) * self.scale

    def computed_importance3(self):
        cc = self.currentClass
        n_c = self.weight_dense.shape[1]
        n_sh = self.weight_dense.shape[0]
        wa = self.wa
        cla = wa.sum(axis=1)  # ts, cl
        clp = np.exp(cla) / np.sum(np.exp(cla), axis=1, keepdims=True) # ts, cl
        def diffp(sh):
            no_cla = wa[:, np.arange(n_sh) != sh, :].sum(axis=1)
            no_cla = np.exp(no_cla)
            no_clp = no_cla / np.sum(no_cla, axis=1, keepdims=True)
            #d = clp[:, :] - no_clp[:, :]
            d = clp[:, cc] - no_clp[:, cc]
            #d[d<0.2] = 0
            d[d<0.01] = 0
            return np.mean(d)
        #self.importance3 = [diffp(sh) * 100000 for sh in range(n_sh)]
        imp3 = np.array([diffp(sh) for sh in range(n_sh)])
        imp3 *= 200/np.max(imp3)
        return imp3

    def watch_currentShapelet(self, cs):
        # up current image
        g = 0
        while cs >= self.groups[g]:
          cs -= self.groups[g]
          g += 1
        self.currentImage = f'{self.folder}/plot/group{g}_shapelet{cs}.png'


m = Comp()
vuejspython.start(Comp(), port=4242)
