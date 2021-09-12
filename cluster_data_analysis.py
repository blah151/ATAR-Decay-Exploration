import ROOT as r
import numpy as np
from matplotlib import pyplot as plt
from Event import Event
import pandas as pd


cluster_data = pd.read_csv("output.csv")
print(cluster_data.head())

plt.hist(cluster_data.get("Event E_Dep in ATAR"), bins = 50, color = "orange", label = "DIF")
plt.title("Total Energy Deposited for Decay in Flight Events")
plt.xlabel("E_Dep in ATAR (MeV)")
plt.ylabel("Count")
plt.show()