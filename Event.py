'''Class stores the following data for ease of use:
c - list of colors to distinguish different decay products.
t - time data.
x - x-coordinate data.
y - y-coordinate data.
z - z-coordinate data; i.e., the number of planes deep into the ATAR
E - energy deposited at the given read time
E_per_plane - energy deposited per plane. Should be of length 50 since there are 50 planes.
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
    
    # def __init__(self, c_data, t_data, x_data, y_data, z_data, E_data, E_per_plane):
    #     self.c_data = c_data
    #     self.t_data = t_data
    #     self.x_data = x_data
    #     self.y_data = y_data
    #     self.z_data = z_data
    #     self.E_data = E_data
    #     self.E_per_plane = E_per_plane