
import asyncio
from reactive.ObservableDict import ObservableDict

import vuejspython


@vuejspython.model
class Comp:
    # define properties to forward to vue (or not)
    suggestions = ['salut', 'ToTo']
    title = 'Test1'
    i = 42
    subtitle = 'very local'
    _novue = ['subtitle']

    def __init__(self):
        asyncio.ensure_future(self.demo_incr(2, 3))
        pass

    async def demo_incr(self, t, v):
        while True:
            await asyncio.sleep(t)
            self.i += v

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
vuejspython.start(m)
