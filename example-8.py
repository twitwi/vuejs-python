
import asyncio

from vuejspython import model, start


@model
class Comp:
    # define properties to forward to vue (or not)
    i = 42

    def __init__(self):
        self.i = 1

    def incr(self, d):
        self.i += d

@model
class Dummy:
    i = 12
    def incr(self, d):
        self.i += d

@model
class Square:
    def computed_square(self):
        return self.val ** 2

start(Comp())
