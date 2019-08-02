
import asyncio

from vuejspython import model, start


@model
class Comp:
    # define properties to forward to vue (or not)
    i = 42

    def __init__(self):
        self.i = 1

    def computed_sqrd(self):
        return self.i ** 2

    def incr(self, d):
        self.i += d

@model
class Dummy:
    i = 3
    def incr(self, d):
        self.i += d

@model
class Square:
    props = ['val'] # python defined props
    val = 0 # need a value for typing reasons, maybe this will change
    # TODO? consider a more vuejs syntax like: props = {'val': {'default': 0}}

    def computed_square(self):
        return self.val ** 2

start(Comp())
