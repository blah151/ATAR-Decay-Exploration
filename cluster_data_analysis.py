import ROOT as r
import numpy as np
from matplotlib import pyplot as plt
from Event import Event
import pandas as pd


#Calculates and displays the suppression factor for the two given data sets. User must specify whether the cut is above or below the given threshold.
#Params:
#  data_a - the first data set (as pandas sequence)
#  data_b - the second data set (as pandas sequence)
#  cut_threshold - the number that determines which values will be kept or cut
#  is_cut_gt - True means cut is greater than threshold, False means cut is less than threshold
def calc_supp_factor(data_a, data_b, cut_threshold, is_cut_gt):
    if (is_cut_gt):
        cut_a = data_a[data_a.gt(cut_threshold)]
        cut_b = data_b[data_b.gt(cut_threshold)]
    else:
        cut_a = data_a[data_a.lt(cut_threshold)]
        cut_b = data_b[data_b.lt(cut_threshold)]

    original_data_ratio = len(data_b) / len(data_a)
    cut_data_ratio = len(cut_b) / len(cut_a)
    print("Original PiMuE / PiENu ratio: ", original_data_ratio)
    print("Cut PiMuE / PiENu ratio: ", cut_data_ratio)
    print("Suppression factor:", original_data_ratio / cut_data_ratio, "\n")




#Read data files scp'd from cluster.
pienu_data = pd.read_csv("output_pienu.csv")
pimue_data = pd.read_csv("output_pimue.csv")
# print(pienu_data.head())
# print(pimue_data.head())


#>>>>>>>>>>>>>>>  Cut 3  <<<<<<<<<<<<<<<
plt.figure()
#Separate DAR and DIF events.
pi_mu_energy_PiENu_DAR = pienu_data[pienu_data["is_DAR"] == 1].get("pi_mu_energy")
pi_mu_energy_PiENu_DIF = pienu_data[pienu_data["is_DAR"] == 0].get("pi_mu_energy")
pi_mu_energy_PiMuE_DAR = pimue_data[pimue_data["is_DAR"] == 1].get("pi_mu_energy")
pi_mu_energy_PiMuE_DIF = pimue_data[pimue_data["is_DAR"] == 0].get("pi_mu_energy")
#use numpy's histogram and hstack functions to ensure both data sets have the same bounds and number of bins.
# pi_mu_energy_PiENu_DAR, pi_mu_energy_PiENu_DIF, pi_mu_energy_PiMuE_DAR, pi_mu_energy_PiMuE_DIF = PiENu_DAR.get("pi_mu_energy"), PiENu_DIF.get("pi_mu_energy"), PiMuE_DAR.get("pi_mu_energy"), PiMuE_DAR.get("pi_mu_energy")
bins = np.histogram(np.hstack((pi_mu_energy_PiENu_DAR, pi_mu_energy_PiENu_DIF, pi_mu_energy_PiMuE_DAR, pi_mu_energy_PiMuE_DIF)), bins = 40)[1]
plt.hist(pi_mu_energy_PiENu_DAR, bins = bins, color = "orange", alpha = 0.5, label = "PiENu DAR")
plt.hist(pi_mu_energy_PiENu_DIF, bins = bins, color = "red", alpha = 0.5, label = "PiENu DIF")
plt.hist(pi_mu_energy_PiMuE_DAR, bins = bins, color = "blue", alpha = 0.5, label = "PiMuE DAR")
plt.hist(pi_mu_energy_PiMuE_DIF, bins = bins, color = "cyan", alpha = 0.5, label = "PiMuE DIF")

plt.title("Total Energy Deposited in ATAR by Pions and Muons")
plt.xlabel("E_Dep in ATAR (MeV)")
plt.ylabel("Counts")
plt.yscale("log")
#Show where Tristan's cut would be.
#TODO: Tristan gives a range:  18.67 < E < 19.2.  Is the line below incorrect?
plt.axvline(18.67, color = "black", label = "Cut")  #Units = MeV
plt.legend()

# print("\nPiENu pi_mu_energy: " + str(pienu_data["pi_mu_energy"].mean()))
# print("PiMuE pi_mu_energy: " + str(pimue_data["pi_mu_energy"].mean()))

calc_supp_factor(pienu_data.get("pi_mu_energy"), pimue_data.get("pi_mu_energy"), 18.67, True)


#>>>>>>>>>>>>>>>  Cut 5  <<<<<<<<<<<<<<<
plt.figure()
three_plane_E_sum_PiENu, three_plane_E_sum_PiMuE = pienu_data.get("three_plane_E_sum"), pimue_data.get("three_plane_E_sum")
bins = np.histogram(np.hstack((three_plane_E_sum_PiENu, three_plane_E_sum_PiMuE)), bins = 40)[1]
plt.hist(three_plane_E_sum_PiENu, bins = bins, color = "green", alpha = 0.5, label = "pienu_data")
plt.hist(three_plane_E_sum_PiMuE, bins = bins, color = "brown", alpha = 0.5, label = "pimue_data")
plt.title("Energy Deposited 3 Planes Before Stopping Plane in ATAR")
plt.xlabel("E (MeV)")
plt.ylabel("Counts")
plt.yscale("log")
plt.axvline(1.88, color = "black", label = "Cut")   #Units = MeV
plt.legend()

# print("\nPiENu three_plane_E_sum: " + str(pienu_data["three_plane_E_sum"].mean()))
# print("PiMuE three_plane_E_sum: " + str(pimue_data["three_plane_E_sum"].mean()))

calc_supp_factor(three_plane_E_sum_PiENu, three_plane_E_sum_PiMuE, 1.88, False)

plt.show()