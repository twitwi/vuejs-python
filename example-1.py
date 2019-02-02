
import asyncio
from reactive.ObservableDict import ObservableDict

import vuejspython


@vuejspython.model
class Comp:
    # define properties to forward to vue (or not)
    suggestions = ['salut', 'ToTo']
    title = 'Test1'
    i = 42
    i2 = i*i
    subtitle = 'very local'
    _v_novue = ['subtitle']

    def __init__(self):
        self.i = 55
        asyncio.ensure_future(self.demo_incr(2, 3))
        pass

    def watch_i(self, i):
        self.i2 = i*i

    def computed_i_squared(self):
        print("COMPUTING i_squared")
        return self.i**2

    async def demo_incr(self, t, v):
        while True:
            await asyncio.sleep(t)
            self.i += v

    async def meth1(self, v):
        print("Com", v)
        self.subtitle = "Changed: "+v # will not trigger change as _novue
        if v == 'salut':
            self.i += 1
            #await self._up('i')

    async def clone(self, v):
        self.suggestions += [v]
        #_up(self, 'suggestions')

vuejspython.start(Comp())
