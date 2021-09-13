import ROOT as r
import numpy as np
from matplotlib import pyplot as plt
from Event import Event
import pandas as pd


pienu_data = pd.read_csv("output_pienu.csv")
pimue_data = pd.read_csv("output_pimue.csv")
print(pienu_data.head())
print(pimue_data.head())

plt.figure()
_, bins, _ = plt.hist(pienu_data.get("pi_mu_energy"), bins = 20, color = "orange", alpha = 0.5, label = "pienu_data")
plt.hist(pimue_data.get("pi_mu_energy"), bins = bins, color = "blue", alpha = 0.5, label = "pimue_data")
plt.title("Total Energy Deposited in ATAR by Pions and Muons")
plt.xlabel("E_Dep in ATAR (MeV)")
plt.ylabel("Counts")
plt.yscale("log")
plt.legend()
plt.show()