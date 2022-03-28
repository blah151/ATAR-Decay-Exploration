'''
This class provides automated functionality for extracting the locations of the SiPMs from the calorimeter. This is then used in event_visualizer()
to plot the energy deposited at the locations listed in the calorimeter tree. Note that the current geometry used is drawn from the file
calo_plus_ATAR_PEN.gdml in the method get_crystal_data(). The calorimeter geometry is subject to change, and files such as calo_only_PEN.gdml could
also be used in the future.
'''

from operator import indexOf
import numpy as np
from matplotlib import pyplot as plt
import re
from scipy.spatial.transform import Rotation as Rot


geom_file = '../crystal_test/crystals.gdml'
def get_crystal_data_from_gdml(geom_file, key):
    rotations = {}
    with open(geom_file, 'r') as gf:
        for line in gf:
            if(key in line and 'wrap' not in line):
                #Only try to get a 5-digit index if the line has one in the first place.
                if re.search("_\d{5,7}in", line) != None:
                    id_delimited = re.findall("_\d{5,7}in", line)[0]
                    crystal_id = int( id_delimited.split("_")[-1].split("in")[0] )
                    x = float( line.split()[2].split('"')[1] )
                    y = float( line.split()[3].split('"')[1] )
                    z = float( line.split()[4].split('"')[1] )
                    # print(crystal_id, x, y, z)
                    # if(crystal_id < 304000):
                    rotations[crystal_id] = (-x,-y,-z)
                    # print(crystal_id)
    return rotations


#Converts a 3-Vector to spherical coordinates.
def convert_to_spherical(coords):
    # print(coords)
    return [
        np.linalg.norm(coords)**2,
        np.arctan2(np.sqrt(coords[0]*coords[0] + coords[1]*coords[1]), coords[2]),
        np.arctan2(coords[1], coords[0])
    ]


#Convert the Euler angles in the GDML file into a (theta,phi) pair for plotting.
def euler_to_thetaPhi(euler, degrees=True):
    roti = Rot.from_euler("xyz", euler, degrees=degrees)
    # print(roti)
    matrix = roti.as_matrix()
    out = np.matmul(matrix, [0,0,1])
    print(out)
    # theta = np.arcsin()
    # print(matrix)
    angles = convert_to_spherical(out)[1:]
    # print(angles)
    return angles


def gdml_rotations_to_theta_phi(rotations):
    theta_phis = {}
    for x in rotations:
        print(x)
        theta_phis[x] = euler_to_thetaPhi( rotations[x])
        # print(theta_phis[x])
    return theta_phis


#Get information about where all our crystals are. Using this info, we later know at what locations to get the edep values from the corresponding spots
#on the calorimeter.
def get_crystal_data():
    positions = get_crystal_data_from_gdml('./calo_plus_ATAR_PEN.gdml', key='position name="')
    positions_sph = {x:convert_to_spherical(positions[x]) for x in positions}
    
    return positions_sph