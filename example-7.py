
import asyncio

from vuejspython import model, start


@model
class Comp:
    # define properties to forward to vue (or not)
    i = 42
    i_name = 'l'
    o_name = 's'
    slice_expr = ':'
    is_error = False
    input_expr = str(list(range(40,60)))

    def __init__(self):
        pass

    def computed_input(self):
        try:
            res = eval(self.input_expr)
            if type(res) is list: return res
            return []
        except:
            return []

    def computed_output(self):
        try:
            locals()[self.i_name] = self.input
            res = eval('%s[%s]'%(self.i_name, self.slice_expr))
            self.is_error = False
            return res
        except Exception as e:
            self.is_error = True
            self.error_message = str(e)
            return []

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
