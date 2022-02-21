from operator import indexOf
import numpy as np
from matplotlib import pyplot as plt
import re

# This is where the preliminary calo analysis code goes. Some representative output files from the simulation, including GDML angle data from photon impacts in the calo
# should be placed in this folder. The calo data is then analyzed via various methods below.
# This class is used in the atar_exploration.py class as an additional tool for visualizing events.


geom_file = '../crystal_test/crystals.gdml'
def get_crystal_data_from_gdml(geom_file, key):
    rotations = {}
    with open(geom_file, 'r') as gf:
        for line in gf:
            if(key in line and 'wrap' not in line):
                # print(line.split())
                #TODO Why are we getting "list index out of range" now that we are using calo_plus_ATAR_PEN.gdml?
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

def convert_to_spherical(coords):
    '''
        Converts a 3-Vector to spherical coordinates
    '''
    # print(coords)
    return [
        np.linalg.norm(coords)**2,
        np.arctan2(np.sqrt(coords[0]*coords[0] + coords[1]*coords[1]), coords[2]),
        np.arctan2(coords[1], coords[0])
    ]

def euler_to_thetaPhi(euler, degrees=True):
    '''
        Convert the Euler angles in the GDML file into a (theta,phi) pair for ploting
    '''
    from scipy.spatial.transform import Rotation as Rot
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
    
    # TODO: Note - if we use calo_plus_ATAR_PEN.gdml, then we get weird lines where crystals (shouldn't?) be and an overflow error. Why is this?
    rotations = get_crystal_data_from_gdml('./calo_plus_ATAR_PEN.gdml', key='rotation name="')
    # print(rotations)
    positions = get_crystal_data_from_gdml('./calo_plus_ATAR_PEN.gdml', key='position name="')
    positions_sph = {x:convert_to_spherical(positions[x]) for x in positions}

    return positions_sph


#For debugging purposes.
#get_crystal_data()