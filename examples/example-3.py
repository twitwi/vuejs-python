
import asyncio

from vuejspython import model, start


@model
class Comp:
    # define properties to forward to vue (or not)
    i = 42
    j = 111

    def __init__(self):
        self.i = 1

    def computed_i_squared(self): return self.i**2
    def computed_i_mod2(self): return self.i%2
    def computed_odd(self): return self.i_mod2 == 1
    def computed_even(self): return not self.odd
    def computed_iorisquared(self): return self.i if self.odd else self.i_squared
    def computed_iorj(self): return self.i if self.even else self.j
    def computed_loopy(self): return self.iorisquared # + self.loopy2 # causes recursion error
    def computed_loopy2(self): return self.iorj + self.loopy


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
