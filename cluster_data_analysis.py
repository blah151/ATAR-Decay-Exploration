import ROOT as r
import numpy as np
from matplotlib import pyplot as plt
from Event import Event
import pandas as pd


pienu_data = pd.read_csv("output_pienu.csv")
pimue_data = pd.read_csv("output_pimue.csv")
# print(pienu_data.head())
# print(pimue_data.head())

plt.figure()
_, bins, _ = plt.hist(pienu_data.get("pi_mu_energy"), bins = 20, color = "orange", alpha = 0.5, label = "pienu_data")
plt.hist(pimue_data.get("pi_mu_energy"), bins = 20, color = "blue", alpha = 0.5, label = "pimue_data")
plt.title("Total Energy Deposited in ATAR by Pions and Muons")
plt.xlabel("E_Dep in ATAR (MeV)")
plt.ylabel("Counts")
plt.yscale("log")
plt.legend()

print("\nPiENu pi_mu_energy: " + str(pienu_data["pi_mu_energy"].mean()))
print("PiMuE pi_mu_energy: " + str(pimue_data["pi_mu_energy"].mean()))


plt.figure()
_, bins, _ = plt.hist(pienu_data.get("three_plane_E_sum"), bins = 20, color = "green", alpha = 0.5, label = "pienu_data")
plt.hist(pimue_data.get("three_plane_E_sum"), bins = 20, color = "brown", alpha = 0.5, label = "pimue_data")
plt.title("Energy Deposited 3 Planes Before Stopping Plane in ATAR")
plt.xlabel("E (MeV)")
plt.ylabel("Counts")
plt.yscale("log")
plt.legend()

print("\nPiENu three_plane_E_sum: " + str(pienu_data["three_plane_E_sum"].mean()))
print("PiMuE three_plane_E_sum: " + str(pimue_data["three_plane_E_sum"].mean()))


plt.show()