from operator import indexOf
import numpy as np
from matplotlib import pyplot as plt

# This is where the preliminary calo analysis code goes. Some representative output files from the simulation, including GDML angle data from photon impacts in the calo
# should be placed in this folder. The calo data is then analyzed via various methods below.
# This class is used in the atar_exploration.py class as an additional tool for visualizing events.

# Methods for converting GDML angles to (theta, phi) to be more easily interpreted and displayed.
# def convert_to_spherical(coords):
#     '''
#         Converts a 3-Vector to spherical coordinates
#     '''
#     # print(coords)
#     return [
#         np.linalg.norm(coords)**2,
#         np.arctan2(np.sqrt(coords[0]*coords[0] + coords[1]*coords[1]), coords[2]),
#         np.arctan2(coords[1], coords[0])
#     ]

# def euler_to_thetaPhi(euler, degrees=True):
#     '''
#         Convert the Euler angles in the GDML file into a (theta,phi) pair for plotting
#     '''
#     from scipy.spatial.transform import Rotation as Rot
#     roti = Rot.from_euler("xyz", euler, degrees=degrees)
#     # print(roti)
#     matrix = roti.as_matrix()
#     out = np.matmul(matrix, [0,0,1])
#     # print(out)
#     # theta = np.arcsin()
#     # print(matrix)
#     angles = convert_to_spherical(out)[1:]
#     # print(angles)
#     return angles

# #TODO: Use RegEx to get IDs of sipms, can use ID to find edep branch from root file
# def get_angles_from_gdml(infile, key='<rotation name="HEX'):
#     angles = {}
#     with open(infile, 'r') as f:
#         for line in f: 
#             if key in line:
#                 # print(line)
#                 sipm = int(line.split("0_")[1].split("_")[0])
#                 x = float(line.split('x="')[1].split('"')[0])
#                 y = float(line.split('y="')[1].split('"')[0])
#                 z = float(line.split('z="')[1].split('"')[0])
#                 # print(x,y,z)
#                 angles[sipm] = (-x,-y,-z)
#     return angles




geom_file = '../crystal_test/crystals.gdml'
def get_rotations_from_gdml(geom_file, key='rotation name="'):
    rotations = {}
    with open(geom_file, 'r') as gf:
        for line in gf:
            if(key in line and 'wrap' not in line):
                # print(line.split())
                crystal_id = int( line.split()[1].split("_")[-1].split("in")[0] )
                x = float( line.split()[2].split('"')[1] )
                y = float( line.split()[3].split('"')[1] )
                z = float( line.split()[4].split('"')[1] )
                # print(crystal_id, x, y, z)
                # if(crystal_id < 304000):
                rotations[crystal_id] = (-x,-y,-z)
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




# plot a 2d histogram of energy deposited in each SIPM "pixel" in the calorimeter.
def calo_edep_plot():
    #Get information about where all our crystals are. Using this info, we later know at what locations to get the edep values from the corresponding spots
    #on the calorimeter.
    rotations = get_rotations_from_gdml('./calo_only_PEN.gdml', key='rotation name="')
    # print(rotations)
    positions = get_rotations_from_gdml('./calo_only_PEN.gdml', key='position name="')
    positions_sph = {x:convert_to_spherical(positions[x]) for x in positions}
    # print(positions_sph)
    crys_rs, crys_thetas, crys_phis = zip(*[positions_sph[x] for x in positions_sph])
    print("Length of thetas:", len(crys_thetas))
    # plt.scatter(crys_thetas, crys_phis)
    # plt.xlabel("Theta (rad)")
    # plt.ylabel("Phi (rad)")
    # plt.title("Energy Deposited in Calorimeter SiPMs by Theta vs. Phi")
    # plt.colorbar(orientation="vertical")
    # plt.show()

    return

calo_edep_plot()