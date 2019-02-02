
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
    #folder, groups, scale = 'unzip-nouveau', [30, 30, 30], 100
    folder, groups, scale = 'epoch8000', [40, 40, 40], 1
    importance = []
    importance2 = []
    importance3 = []

    def __init__(self):
        # can add local properties here (to avoid having to fill _novue)
        self.weight_dense = np.genfromtxt(self.folder+'/weight_dense.txt')
        self.activations = np.hstack([
            np.genfromtxt(self.folder+'/mp_shapelet_group_'+str(i)+'.txt') for i in range(len(self.groups))
        ])
        self.update()
        pass

    def update(self):
        a = self.activations   # ts, sh
        w = self.weight_dense  # sh, cl
        wa = a[:,:,None] * w[None, :, :]  # ts, sh, cl

        cc = self.currentClass
        n_c = w.shape[1]
        mean_others = wa[:, :, np.arange(n_c) != cc].mean(axis=2)
        self.importance = np.mean(wa[:,:,cc] - mean_others, axis=0) * self.scale

        max_others = wa[:, :, np.arange(n_c) != cc].max(axis=2)
        self.importance2 = np.mean(wa[:,:,cc] - max_others, axis=0) * self.scale

        n_sh = w.shape[0]
        cla = wa.sum(axis=1)  # ts, cl
        clp = np.exp(cla) / np.sum(np.exp(cla), axis=1, keepdims=True) # ts, cl
        def diffp(sh):
            no_cla = wa[:, np.arange(n_sh) != sh, :].sum(axis=1)
            no_cla = np.exp(no_cla)
            no_clp = no_cla / np.sum(no_cla, axis=1, keepdims=True)
            #d = clp[:, :] - no_clp[:, :]
            d = clp[:, cc] - no_clp[:, cc]
            d[d<0] = 0
            return np.mean(d)
        self.importance3 = [diffp(sh) * 100 for sh in range(n_sh)]
        #awa = np.average(wa, axis=0) # sh, cl
        #self.importance = np.std(awa, axis=1)*100
        print(self.activations.shape)
        print(self.weight_dense.shape)
        print(wa.shape)

        #self.importance = importance.tolist()

    def watch_currentClass(self, cc):
        self.update()

    def watch_currentShapelet(self, cs):
        # up current image
        g = 0
        while cs >= self.groups[g]:
          cs -= self.groups[g]
          g += 1
        self.currentImage = f'{self.folder}/plot/group{g}_shapelet{cs}.png'
        #self.update()

    #async def demo_incr(self, t, v):
    #    while True:
    #        await asyncio.sleep(t)
    #        self.i += v

    async def meth1(self, v):
        print("Com", v)
        if v == 'salut':
            self.i += 1
            #await self._up('i')

    async def clone(self, v):
        self.suggestions += [v]
        #_up(self, 'suggestions')

#state = ObservableDict()
#state = {}
#state['suggestions'] = ['salut', 'TOto']
#state['title'] = 'Test1'

m = Comp()
vuejspython.start(Comp(), port=4242)
