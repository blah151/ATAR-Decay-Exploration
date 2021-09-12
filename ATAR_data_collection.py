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

    return event


#Use cuts to select the events we want from the tree. Returns an integer list of the indices of the events that we want from the tree.
#is_event_DAR: Value of 0 = decays in flight, 1 = decays at rest, 2 = all data used.
def select_events(tree, is_event_DAR):
    #Apply logical cut to select whether we want DARs and to exclude empty data. n stores the number of entries that satisfy this cut.
    if is_event_DAR == 0:
        cut = "!pion_dar && Sum$(pixel_edep) > 0"
    elif is_event_DAR == 1:
        cut = "pion_dar && Sum$(pixel_edep) > 0"
    else:
        cut = "Sum$(pixel_edep) > 0"
    n = tree.Draw("Entry$", cut, "goff")
    
    #Get all indices that satisfy the cut.
    selected_events = []
    for i in range(n):
        selected_events.append(tree.GetV1()[i])

    # print("Indices of selected events: " + str(selected_events))

    return [int(i) for i in selected_events]

















def process_file(infile, is_event_DAR):
    assert os.path.exists(infile)

    f = r.TFile(infile)
    # f.ls()
    t = f.Get("atar")
    # print(t)
    n = t.GetEntries()
    # print(f"There are {n} events in this file!")

    #Get indices for events that satisfy DAR / DIF criteria.
    event_indices = select_events(t, is_event_DAR) # TODO:  Remove num_events to get all data.

    results = []

    #Use max edep per plane as a heuristic to distinguish between DIFs and DARs.
    max_Es = []

    #Keep track of gap times.
    gap_times = []

    #For each of the event indices specified, process the corresponding event and save useful parameters from it for later analysis.
    for i in range(len(event_indices)):
        e = process_event(t, event_indices[i])
        
        event_e_dep = sum(e.E_data)

        #Add information from event to results for easier conversion to a Pandas dataframe.
        results.append({
            'event':i,
            # 't_data':e.t_data,
            # 'x_data':e.x_data,
            # 'y_data':e.y_data,
            # 'z_data':e.z_data,
            # 'E_data':e.E_data,
            # 'E_per_plane':e.E_per_plane,
            # 'pixel_pdgs':e.pixel_pdgs,
            'Event E_Dep in ATAR':event_e_dep,
            #'gap_times':e.gap_times,
            'file':infile
        })                                      # TODO:  Why are we getting segmentation violations and failures to print output?  Perhaps memory overflow?
        
        # print([x.GetName() for x in t.GetListOfBranches()])

        # for gt in e.gap_times:
        #     gap_times.append(gt)

        # max_Es.append(e.max_E)

    return results


def main():
    is_event_DAR = 0     # Can be 0 (DIF only), 1 (DAR only), or 2 (Both). TODO: Do we want to choose DAR / DIF here or later?

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
        results += process_file(file, is_event_DAR)

    df = pandas.DataFrame(results)
    print(df.head())
    print("\n" + str(df.shape))
    df.to_csv("output.csv")

if __name__ == '__main__':
    main()