
import asyncio
from reactive.ObservableDict import ObservableDict

from vuejspython import model, computed, start


@model
class Comp:
    # define properties to forward to vue (or not)
    suggestions = ['+1']
    i = 42
    j = 111

    def __init__(self):
        self.i = 1

    @computed
    def i_squared(self): return self.i**2
    @computed
    def i_mod2(self): return self.i%2
    @computed
    def odd(self): return self.i_mod2 == 1
    @computed
    def even(self): return not self.odd
    @computed
    def iorisquared(self): return self.i if self.odd else self.i_squared
    @computed
    def iorj(self): return self.i if self.even else self.j
    @computed
    def loopy(self): return self.iorisquared # + self.loopy2 # causes recursion error
    @computed
    def loopy2(self): return self.iorj + self.loopy


    async def demo_incr(self, t, v):
        while True:
            await asyncio.sleep(t)
            self.i += v

    async def meth1(self, v):
        print("Com", v)
        self.subtitle = "Changed: "+v # will not trigger change as _novue
        if v == '+1':
            self.i += 1
            #await self._up('i')

start(Comp())
