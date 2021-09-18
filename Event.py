'''Class stores the following data for ease of use:
t - time data.
x - x-coordinate data.
y - y-coordinate data.
z - z-coordinate data; i.e., the number of planes deep into the ATAR
E - energy deposited at the given read time
E_per_plane - energy deposited per plane. Should be of length 50 since there are 50 planes.
pixel_pdgs - particle IDs (as ints) to distinguish different decay products.
max_E - maximum energy deposited over all planes.
gap_times - any large time gaps in the data, which signal a decay at rest.
is_DAR - True means event is a Decay at Rest, False means it is a Decay in Flight.
'''

import numpy as np

class Event():

    def __init__(self):
        self.t_data = []
        self.x_data = []
        self.y_data = []
        self.z_data = []
        self.E_data = []
        self.E_per_plane = np.zeros(100)
        self.pixel_pdgs = []
        self.max_E = []
        self.gap_times = []
        self.is_DAR = None