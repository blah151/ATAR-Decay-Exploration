import ROOT as r
import numpy as np
from matplotlib import pyplot as plt
from Event import Event
import pandas as pd


#Calculates and displays the suppression factor for the two given data sets. User must specify whether the cut is above or below the given threshold.
#Params:
#  data_a - (Pandas Sequence) The first data set (as pandas sequence)
#  data_b - (Pandas Sequence) The second data set (as pandas sequence)
#  cut_threshold - (Float) The number that determines which values will be kept or cut
#  is_cut_gt - (Boolean) True means cut is greater than threshold, False means cut is less than threshold
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


#Plots PiENu and PiMuE events on a histogram and compares their suppression factors. Can also compare DARs / DIFs if desired.
#Params:
#  cut_var - (Str) Variable whose values we extract from the dataframes. We expect PiENu events and PiMuE events to have distinguishable distributions of this variable.
#  cut_units - (Str) Shorthand name and units of variable for x-axis label of histogram.
#  cut_val - (Float) The value of the cut that Tristan used in his study
#  title - (Str) The title of the histogram.
#  is_comparing_DAR_DIF - (Boolean) True means we divide data 4 ways:  PiENu_DAR / PiENu_DIF / PiMuE_DAR / PiMuE_DIF. False means we stick with the usual splitting along 
#                         PiENu / PiMuE.
#  is_cut_gt - (Boolean) True means cut is greater than threshold, False means cut is less than threshold
def plot_cut(cut_var, cut_units, cut_val, title, is_comparing_DAR_DIF, is_cut_gt):
    plt.figure()
    cut_var_PiENu = pienu_data.get(cut_var)
    cut_var_PiMuE = pimue_data.get(cut_var)

    #Do 2 plots if simply comparing PiENu to PiMuE, do 4 plots if also splitting data on DAR / DIF.
    if not is_comparing_DAR_DIF:
        #use numpy's histogram and hstack functions to ensure both data sets have the same bounds and number of bins.
        bins = np.histogram(np.hstack((cut_var_PiENu, cut_var_PiMuE)), bins = 40)[1]
        plt.hist(cut_var_PiENu, bins = bins, color = "orange", alpha = 0.5, label = "pienu_data")
        plt.hist(cut_var_PiMuE, bins = bins, color = "blue", alpha = 0.5, label = "pimue_data")
    else:
        #Separate DAR and DIF events.
        cut_var_PiENu_DAR = pienu_data[pienu_data["is_DAR"] == 1].get(cut_var)
        cut_var_PiENu_DIF = pienu_data[pienu_data["is_DAR"] == 0].get(cut_var)
        cut_var_PiMuE_DAR = pimue_data[pimue_data["is_DAR"] == 1].get(cut_var)
        cut_var_PiMuE_DIF = pimue_data[pimue_data["is_DAR"] == 0].get(cut_var)
        bins = np.histogram(np.hstack((cut_var_PiENu_DAR, cut_var_PiENu_DIF, cut_var_PiMuE_DAR, cut_var_PiMuE_DIF)), bins = 40)[1]
        plt.hist(cut_var_PiENu_DAR, bins = bins, color = "orange", alpha = 0.5, label = "PiENu DAR")
        plt.hist(cut_var_PiENu_DIF, bins = bins, color = "red", alpha = 0.5, label = "PiENu DIF")
        plt.hist(cut_var_PiMuE_DAR, bins = bins, color = "blue", alpha = 0.5, label = "PiMuE DAR")
        plt.hist(cut_var_PiMuE_DIF, bins = bins, color = "cyan", alpha = 0.5, label = "PiMuE DIF")
    
    plt.title(title)
    plt.xlabel(cut_units)
    plt.ylabel("Counts")
    plt.yscale("log")
    plt.axvline(cut_val, color = "black", label = "Cut")
    plt.legend()

    calc_supp_factor(cut_var_PiENu, cut_var_PiMuE, cut_val, is_cut_gt)




#Read data files scp'd from cluster.
pienu_data = pd.read_csv("output_pienu.csv")
pimue_data = pd.read_csv("output_pimue.csv")
# print(pienu_data.head())
# print(pimue_data.head())


#TODO: Implement cuts 1, 2, and 4.
#>>>>>>>>>>>>>>>  Cut 1 - Stop in Target (Pion for DAR, Muon for DIF)  <<<<<<<<<<<<<<<
plot_cut("three_plane_E_sum", "E (MeV)", 1, "Energy Deposited 3 Planes Before Stopping Plane in ATAR", False, False)

#>>>>>>>>>>>>>>>  Cut 2 - Restricted Stopping Distribution  <<<<<<<<<<<<<<<
plot_cut("three_plane_E_sum", "E (MeV)", 1, "Energy Deposited 3 Planes Before Stopping Plane in ATAR", False, False)

#>>>>>>>>>>>>>>>  Cut 3 - Pion and Muon Energies  <<<<<<<<<<<<<<<
plot_cut("pi_mu_energy", "E_Dep in ATAR (MeV)", 18.67, "Total Energy Deposited in ATAR by Pions and Muons", True, True)

#>>>>>>>>>>>>>>>  Cut 4 - Tracking Cut  <<<<<<<<<<<<<<<
plot_cut("three_plane_E_sum", "E (MeV)", 1, "Energy Deposited 3 Planes Before Stopping Plane in ATAR", False, False)

#>>>>>>>>>>>>>>>  Cut 5 - EPreStop Cut  <<<<<<<<<<<<<<<
plot_cut("three_plane_E_sum", "E (MeV)", 1, "Energy Deposited 3 Planes Before Stopping Plane in ATAR", False, False)

plt.show()