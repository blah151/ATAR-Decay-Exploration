# This file collates data from a number of root files, then saves it to a data frame to be analyzed later.

import ROOT as r
import os
import sys
import pandas
import numpy as np
from Event import Event


'''
Methods needed:

*process_event
display_event
plot_with_color_legend
plot_event
*select_events
*event_visualization
compare_max_edep
compare_gap_times
'''


'''
Returns the time vs. x and time vs. y data from the pixel_hits. The ATAR is made up of sheets that contain alternating horizontal or vertical strips with npixels_per_plane.
If npixels_per_plane were 100, for instance, 100036 would represent plate 1, 36 / 100 in x, 100161 would represent plate 2, 61 / 100 in y, etc. The output for each of 
x and y is an n x 2 matrix, where the first column contains the times corresponding to the coordinate values in the second column.
Also extract the z (plane #) vs. time data. The third element of the tuples contained in this list and the x and y lists will contain corresponding colors to represent
when particles have decayed.
'''
def process_event(tree, event_index):
    #Get the specified entry so we can extract data from it.
    tree.GetEntry(event_index)

    #Store pixel hits for the entry printed above in which a pion didn't decay at rest.
    pixel_times = tree.pixel_time
    pixel_hits = tree.pixel_hits
    pixel_edep = tree.pixel_edep
    
    #Initialize lists for storing color (for labeling data points according to decay product), t, x, y, z, energy, and energy per plane using the Event class.
    npixels_per_plane = 100
    event = Event()

    #Init time value so 1st loop below works.
    cur_time = 0
    
    #Extract x vs. t, y vs. t, and z vs. t data. Also add indexed color coding to represent different particles.
    for i in range(pixel_hits.size()):
        plane = int(np.floor((pixel_hits[i] - 1 - 100_000) / npixels_per_plane))

        cur_val = (pixel_hits[i] - 1) % npixels_per_plane
        last_time = cur_time    #Allows us to note any large time gaps for later analysis.
        cur_time = pixel_times[i]

        event.t_data.append(cur_time)

        if(plane % 2 == 0):
            event.x_data.append(cur_val)
            event.y_data.append(np.nan)
        else:
            event.y_data.append(cur_val)
            event.x_data.append(np.nan)

        event.z_data.append(plane)
        event.E_data.append(pixel_edep[i])

        #Keep track of any gaps in time between decays.
        if cur_time - last_time > 1.0:      #TODO: Adjust this time gap (in ns) as needed.
            event.gap_times.append(cur_time - last_time)

        #print("plane # " + str(plane))

        #Keep track of sum of energies deposited in each plane.
        event.E_per_plane[plane] += pixel_edep[i]

    #Keep track of particle IDs.
    event.pixel_pdgs = tree.pixel_pdg

    #Keep track of maximum energy deposited per plane in this event.
    event.max_E = max(event.E_per_plane)

    #Keep track of whether event is a DAR (Decay at Rest) or DIF (Decay in Flight). Event is DAR if value is 1, DIF if value is 0.
    event.is_DAR = tree.pion_dar

    return event


#Use cuts to select the events we want from the tree. Returns an integer list of the indices of the events that we want from the tree.
#is_PiENu: Controls whether we look at PiENu or PiMuE data.
def select_events(tree, is_PiENu):
    #Apply logical cut to select whether we want to look at PiENu or PiMuE data.
    if is_PiENu:
        cut = "!has_muon && Sum$(pixel_edep) > 0"
    else:
        cut = "has_muon && Sum$(pixel_edep) > 0"
    n = tree.Draw("Entry$", cut, "goff")
    
    #Get all indices that satisfy the cut.
    selected_events = []
    for i in range(n):
        selected_events.append(tree.GetV1()[i])

    # print("Indices of selected events: " + str(selected_events))

    return [int(i) for i in selected_events]
















def process_file(infile, is_PiENu):
    assert os.path.exists(infile)

    f = r.TFile(infile)
    # f.ls()
    t = f.Get("atar")
    # print(t)
    n = t.GetEntries()
    # print(f"There are {n} events in this file!")
    # print([x.GetName() for x in t.GetListOfBranches()])

    #Get indices for events that satisfy DAR / DIF criteria.
    event_indices = select_events(t, is_PiENu) # TODO:  Remove num_events to get all data.

    results = []

    #TODO: Cuts out of order makes the most sense (e.g., to get dz/dt for Cut 2)?
    #For each of the event indices specified, process the corresponding event and save useful parameters from it for later analysis.
    for i in range(len(event_indices)):
        e = process_event(t, event_indices[i])

        #>>>>>>>>>>  Cut 3: Pion and Muon Energies  <<<<<<<<<<
        pi_mu_energy = sum(e.E_data)
        #If a positron was present, we must subtract all energy deposited by it per Tristan's cut.
        if t.has_positron:
            for i in range(0, len(e.E_data)):
                if e.pixel_pdgs[i] == -11:
                    pi_mu_energy -= e.E_data[i]

        #>>>>>>>>>>  Cut 5: Energy 3 Planes Before Stopping Plane  <<<<<<<<<<
        last_x, last_y = 0, 0
        stop_x, stop_y, stopping_plane = 0, 0, 0
        three_plane_E_sum = 0
        for i in range(0, len(e.pixel_pdgs) - 2):
            dzdt = (e.z_data[i + 2] - e.z_data[i]) / (e.t_data[i + 2] - e.t_data[i])

            #Store last x and y each loop so we don't get stuck with any nan values in Cut 2.
            if e.x_data[i] is not np.nan:
                last_x = e.x_data[i]
            if e.y_data[i] is not np.nan:
                last_y = e.y_data[i]
            
            '''and e.is_DAR'''   '''and not e.is_DAR'''
            #We know we have found the stopping plane if the particle is a pion or antimuon and has stopped moving in z. Also only record a value for the three plane
            #sum if we are more than a few time intervals in (a pion just sitting there for a few frames in the target deposits no energy anyway).
            if ((e.pixel_pdgs[i] == 211) or (e.pixel_pdgs[i] == -13)) and abs(dzdt) < 1 and i >= 4:
                #>>>>>>>>>>  Cut 2: Restricted Stopping Distribution  <<<<<<<<<<
                #We already have the stopping plane info from Cut 5 to use here.
                stop_x, stop_y, stopping_plane = last_x, last_y, e.z_data[i]
                three_plane_E_sum = e.E_data[i - 2] + e.E_data[i - 3] + e.E_data[i - 4]

        #Add information from event to results for easier conversion to a Pandas dataframe.
        results.append({
            'event':i,
            'is_DAR':e.is_DAR,
            'stop_x': stop_x,
            'stop_y': stop_y,
            'stop_z': stopping_plane,
            'pi_mu_energy':pi_mu_energy,
            'three_plane_E_sum':three_plane_E_sum,
            'file':infile
        })

    return results


def main():
    # Selects whether we want to store data for PiENu or PiMuE events, which we will compare later.
    is_PiENu = True

    # python test.py arg arg2 arg3
                    #^^^^^^^^^^^^^
    file_list = sys.argv[1] # get command line args
    files = []
    with open(file_list, 'r') as f:
        for line in f:
            files.append(line.strip()) # removes trailing \n: "  test \n" -> "test"
    print("\n")
    # print(files)
    print("\n")
    results = []
    for file in files:
        results += process_file(file, is_PiENu)
    

    df = pandas.DataFrame(results)
    print(df.head())
    print("\n" + str(df.shape))
    df.to_csv("output.csv")

if __name__ == '__main__':
    main()