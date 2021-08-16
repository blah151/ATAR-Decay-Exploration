'''Class stores the following data for ease of use:
c - list of colors to distinguish different decay products.
t - time data.
x - x-coordinate data.
y - y-coordinate data.
z - z-coordinate data; i.e., the number of planes deep into the ATAR
E - energy deposited at the given read time
E_per_plane - energy deposited per plane. Should be of length 50 since there are 50 planes.
max_E - maximum energy deposited over all planes.
gap_times - any large time gaps in the data, which signal a decay at rest.
'''

import numpy as np

class Event():

    def __init__(self):
        self.c_data = []
        self.t_data = []
        self.x_data = []
        self.y_data = []
        self.z_data = []
        self.E_data = []
        self.E_per_plane = np.zeros(50)
        self.max_E = []
        self.gap_times = []