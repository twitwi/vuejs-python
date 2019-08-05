
import vuejspython
from numpy import pi

@vuejspython.model
class App:
  radius = 5
  def computed_area(self):
    return pi * self.radius ** 2

vuejspython.start(App())
