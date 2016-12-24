# ## An interesting example
#
# This is an interesting example.

import numpy as np
x = np.linspace(0, 2 * np.pi, 1000)
x[:10]

# Even more interesting than that:
#
# If running in the IPython console, consider running `%matplotlib` to enable
# interactive plots.  If running in the Jupyter Notebook, use `%matplotlib
# inline`.

import matplotlib.pyplot as plt

plt.plot(x, np.sin(x))
