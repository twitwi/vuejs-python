
import asyncio
from reactive.ObservableDict import ObservableDict

import vuejspython


# TODO: watchers on the python side to be able to act when js changes a value (maybe with a convention on method name, e.g., on_title(old, new), or an annotation that decorates the _up cb)
# TODO: prevent /init from sending _novue (and __init__ content)

@vuejspython.model # this annotation could start the things automatically (if there is a single model anyway)
class Comp:
    # define properties to forward to vue (or not)
    suggestions = ['salut', 'ToTo']
    title = 'Test1'
    i = 42
    subtitle = 'very local'
    _novue = ['subtitle']

    def __init__(self):
        self.i = 55
        asyncio.ensure_future(self.demo_incr(2, 3))
        pass

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

#state = ObservableDict()
#state = {}
#state['suggestions'] = ['salut', 'TOto']
#state['title'] = 'Test1'

m = Comp()
# todo, might want to implement derived properties as methods (by annotating them as @computed so they are setup properly on the html side)
vuejspython.start(m)
