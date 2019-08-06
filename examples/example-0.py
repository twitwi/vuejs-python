
import vuejspython
from numpy import pi

@vuejspython.model
class App:
    radius = 2
    def computed_area(self):
        if self.radius == "": return 0
        return pi * self.radius ** 2

vuejspython.start(App())
