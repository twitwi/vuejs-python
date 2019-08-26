
import vuejspython
import numpy as np


@vuejspython.model
class App:

    # input = np.random.uniform(-1000, 1000, 10)
    input = 4 + 5*np.sin(np.linspace(-6, 5, 15))
    scale = 1
    bias = 0

    def computed_size(self): return len(self.input)

    def computed_scaled(self):
        return np.array(self.input) * self.scale

    def computed_biased(self):
        return np.array(self.scaled) - self.bias

    def computed_relu(self):
        res = np.copy(self.biased)
        #res[res < self.bias] = self.bias
        res[res < 0] = 0
        return res

    def computed_logsoftmax(self):
        smax = np.exp(self.relu)
        smax /= np.sum(smax)
        return np.log(smax + 0.000001)


vuejspython.start(App())
