#This is a script version of atar_exploration.ipynb to be run via the command line.

import ROOT as r
import numpy as np
from matplotlib import pyplot as plt
from Event import Event


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

        # #Keep track of any gaps in time between decays.
        if cur_time - last_time > 1.0:      #TODO: Adjust this time gap (in ns) as needed.
            event.gap_times.append(cur_time - last_time)

        #Keep track of sum of energies deposited in each plane.
        event.E_per_plane[plane] += pixel_edep[i]

    #Keep track of particle IDs.
    event.pixel_pdgs = tree.pixel_pdg

    #Keep track of maximum energy deposited per plane in this event.
    event.max_E = max(event.E_per_plane)

    return event


#Show some useful parameters describing our event.
def display_event(event):
    print("Length of pixel_pdgs: " + str(len(event.pixel_pdgs)))
    print("Length of t_data: " + str(len(event.t_data)))
    print("Length of x_data: " + str(len(event.x_data)))
    print("Length of y_data: " + str(len(event.y_data)))
    print("Length of z_data: " + str(len(event.z_data)))
    print("Length of E_data: " + str(len(event.E_data)))
    print("Length of E_per_plane: " + str(len(event.E_per_plane)))
    print("pixel_pdgs: " + str(event.pixel_pdgs))
    print("x_data: " + str(event.x_data))
    print("t_data: " + str(event.t_data))


#For each color in a list of color labels for different particles, plot the corresponding data.
def plot_with_color_legend(x_coords, y_coords, pixel_pdgs):
    #Store colors and corresponding particle type labels in one place for ease of editing.
    colors = ["r", "b", "g", "y", "m"]
    labels = ["Pion", "Positron", "Electron", "Antimuon", "Muon"]
    particle_IDs = [211, -11, 11, -13, 13]
    
    #Store list of tuples of our data to be processed below.
    coords = zip(x_coords, y_coords, pixel_pdgs)

    #Keep track of known particles and other particles to plot.
    cur_data_to_plot = []
    other_to_plot = []
    other_IDs = []
    other_colors = ["k", "gray", "cyan", "indigo", "teal", "lime"]

    #For each color, extract all pdgs of that color and display them on a scatter plot.
    for i in range(0, len(particle_IDs)):
        for coord in coords:
            if coord[2] == particle_IDs[i]:                
                cur_data_to_plot.append(coord)
            elif coord[2] not in particle_IDs:  # Keep track of number of unidentified particles so we can plot them separately after exiting this loop.
                other_to_plot.append(coord)

                #Keep list of other IDs so we know how many labels are needed.
                if coord[2] not in other_IDs:
                    other_IDs.append(coord[2])
                #str(pixel_pdg[i])
        
        #Plot data for corresponding color each loop, but only if the data for the corresponding color is not empty.
        if len(cur_data_to_plot) != 0:
            plt.scatter([coord[0] for coord in cur_data_to_plot], [coord[1] for coord in cur_data_to_plot], 10, colors[i], label = labels[i])

        #Reset data to plot every loop.
        cur_data_to_plot = []

    #Plot the unidentified particles in distinct colors with their pdgs for labels.
    for i in range(0, len(other_IDs)):
        ID = other_IDs[i]
        
        #Extract x and y coordinates to plot only if they are all of the particle ID that we are currently plotting.
        # [coord[0] for coord in other_to_plot if coord[2] == ID]
        x = []
        y = []
        for coord in other_to_plot:
            if coord[2] == ID:
                x.append(coord[0])
                y.append(coord[1])

        plt.scatter(x, y, 10, other_colors[i], label = str(ID))


#Plot x vs. t, y vs. t, z vs. t, and E vs. z data from our event. The graphs will show the color-coding system used to represent different particles.
#Display 0 to num_planes on plots including the z variable.
def plot_event(event, num_planes):

    plt.figure(figsize = (25, 6))

    plt.subplot(1,4,1)

    plot_with_color_legend(event.z_data, event.x_data, event.pixel_pdgs)
    plt.title("x vs. z")
    plt.xlabel("z (plane number)")
    plt.ylabel("x (pix)")
    plt.legend()
    plt.xlim(0, num_planes)
    plt.ylim(0, 100)

    plt.subplot(1,4,2)
    plot_with_color_legend(event.z_data, event.y_data, event.pixel_pdgs)
    plt.title("y vs. z")
    plt.xlabel("z (plane number)")
    plt.ylabel("y (pix)")
    plt.xlim(0, num_planes)
    plt.ylim(0, 100)

    plt.subplot(1,4,3)
    plot_with_color_legend(event.t_data, event.z_data, event.pixel_pdgs)
    plt.title("z vs. t")
    plt.xlabel("t (ns)")
    plt.ylabel("z (plane number)")
    # plt.xlim(0, 60)
    plt.ylim(0, num_planes)

    plt.subplot(1,4,4)

    plt.scatter(event.z_data, event.E_data, 10, label = "e_dep")
    plt.scatter(range(50), event.E_per_plane, 10, "black", label = "e_dep per plane")
    plt.title("ATAR Energy Deposition Per Plane vs. z")
    plt.xlabel("z (plane number)")
    plt.ylabel("Energy (MeV / plane)")
    plt.legend()
    #plt.xlim(0, num_planes)

    plt.subplots_adjust(left = 0.1,
                        bottom = 0.1, 
                        right = 0.9, 
                        top = 0.9, 
                        wspace = 0.5, 
                        hspace = 0.4)

    plt.show()


#Use cuts to select the events we want from the tree. Returns an integer list of the indices of the events that we want from the tree.
#is_event_DAR: Value of 0 = decays in flight, 1 = decays at rest, 2 = all data used.
#num_events:  Controls how many events we want to select.
def select_events(tree, is_event_DAR, num_events):
    #Apply logical cut to select whether we want DARs and to exclude empty data. n stores the number of entries that satisfy this cut.
    if is_event_DAR == 0:
        cut = "!pion_dar && Sum$(pixel_edep) > 0"
    elif is_event_DAR == 1:
        cut = "pion_dar && Sum$(pixel_edep) > 0"
    else:
        cut = "Sum$(pixel_edep) > 0"
    n = tree.Draw("Entry$", cut, "goff")
    
    #Get all indices that satisfy the cut.
    events = []
    for i in range(n):
        events.append(tree.GetV1()[i])

    selected_events = events[0:num_events]
    print("Indices of selected events: " + str(selected_events))

    return [int(i) for i in selected_events]


#Combines the functions we created above to give a visualization of events with the specified condition(s).
#is_event_DAR: Value of 0 = decays in flight, 1 = decays at rest, 2 = all data used.
#display_text_output = True / False controls whether we should have text info / not have text info displayed.
#display_plots = True / False controls whether event data is plotted or not.
#num_events allows us to plot multiple events with the specified conditions from the tree.\
#gap_times = True / False means we should show / not show gap times between decays if any are present.
def event_visualization(tree, is_event_DAR, display_text_output, display_outliers, num_events):
    
    #Get num_events indices for events that satisfy DAR / DIF criteria.
    event_indices = select_events(tree, is_event_DAR, num_events)

    #Use max edep per plane as a heuristic to distinguish between DIFs and DARs.
    max_Es = []

    #Keep track of gap times.
    gap_times = []

    #For each of the event indices specified, process the corresponding event and display useful output if we want, then plot it.
    for i in range(len(event_indices)):
        e = process_event(tree, event_indices[i])

        if display_text_output:
            display_event(e)
        
        #Show events with abnormally large energies if we want.
        if display_outliers and e.max_E > 7.5:
            plot_event(e, 50)

        for gt in e.gap_times:
            gap_times.append(gt)

        max_Es.append(e.max_E)
        
    return (max_Es, gap_times)


#Compare the maximum energy deposition of decays in flight and decays at rest. Show mean, median, and standard deviation for both sets of maximum energies, then plot them in
#histogram form. One should notice that the DARs have a higher median energy deposited, though the means may be closer due to large outliers present in some DIF data.
#max_Es_DIF:  Data for maximum energies from decays in flight.
#max_Es_DAR:  Data for maximum energies from decays at rest.
#num_bins:  Controls the number of bins used when plotting data on histograms.
def compare_max_edep(max_Es_DIF, max_Es_DAR, num_bins):
    max_Es_DIF_mean = np.mean(max_Es_DIF)
    max_Es_DIF_median = np.median(max_Es_DIF)
    max_Es_DIF_std = np.std(max_Es_DIF)

    max_Es_DAR_mean = np.mean(max_Es_DAR)
    max_Es_DAR_median = np.median(max_Es_DAR)
    max_Es_DAR_std = np.std(max_Es_DAR)

    print("\nmax_Es_DIF_mean: " + str(max_Es_DIF_mean))
    print("max_Es_DIF_median: " + str(max_Es_DIF_median))
    print("max_Es_DIF_std: " + str(max_Es_DIF_std))

    print("\nmax_Es_DAR_mean: " + str(max_Es_DAR_mean))
    print("max_Es_DAR_median: " + str(max_Es_DAR_median))
    print("max_Es_DAR_std: " + str(max_Es_DAR_std))


    plt.figure(figsize = (20, 6))

    #Plot histograms. Saving bins parameter from first plot ensures that both histograms have the same number of bins.
    _, bins, _ = plt.hist(max_Es_DIF, bins = num_bins, color = "blue", alpha = 0.5, label = "DIF")
    plt.hist(max_Es_DAR, bins = bins, color = "orange", alpha = 0.5, label = "DAR")
    plt.title("Max Energy by Group for Decays in Flight and Decays at Rest")
    plt.xlabel("Max Energy by Group (MeV)")
    plt.ylabel("Count")
    plt.legend()
    plt.show()


#Plots gap times given and visualizes how these correlate with DIFs / DARs.
#gap_times: A list of times in ns.
#gap_times_DIF:  Data for times between decays for DIFs in ns.
#gap_times_DAR:  Data for times between decays for DARs in ns.
#num_bins:  Controls the number of bins used when plotting data on histograms.
def compare_gap_times(gap_times_DIF, gap_times_DAR, num_bins):
    gap_times_DIF_mean = np.mean(gap_times_DIF)
    gap_times_DIF_median = np.median(gap_times_DIF)
    gap_times_DIF_std = np.std(gap_times_DIF)

    gap_times_DAR_mean = np.mean(gap_times_DAR)
    gap_times_DAR_median = np.median(gap_times_DAR)
    gap_times_DAR_std = np.std(gap_times_DAR)

    print("\ngap_times_DIF_mean: " + str(gap_times_DIF_mean))
    print("gap_times_DIF_median: " + str(gap_times_DIF_median))
    print("gap_times_DIF_std: " + str(gap_times_DIF_std))

    print("\ngap_times_DAR_mean: " + str(gap_times_DAR_mean))
    print("gap_times_DAR_median: " + str(gap_times_DAR_median))
    print("gap_times_DAR_std: " + str(gap_times_DAR_std))


    plt.figure(figsize = (20, 6))

    #Plot histograms. Saving bins parameter from first plot ensures that both histograms have the same number of bins.
    _, bins, _ = plt.hist(gap_times_DIF, bins = num_bins, color = "green", alpha = 0.5, label = "DIF")
    plt.hist(gap_times_DAR, bins = bins, color = "brown", alpha = 0.5, label = "DAR")
    plt.title("Gap Times for Decays in Flight and Decays at Rest")
    plt.xlabel("Time (ns)")
    plt.ylabel("Count")
    plt.legend()
    plt.show()


#Compare energy deposition and gap times of DARs and DIFs for pion --> e data.
PiEfile = r.TFile("pienux_out_stripped.root")
PiEtree = PiEfile.Get("atar")
# print([x.GetName() for x in tree.GetListOfBranches()])
# print("\n")
print("\n\nPion --> e Data\n\n")
(max_Es_DIF, gap_times_DIF) = event_visualization(PiEtree, 0, False, False, 100)
(max_Es_DAR, gap_times_DAR) = event_visualization(PiEtree, 1, False, False, 100)
compare_max_edep(max_Es_DIF, max_Es_DAR, 20)
compare_gap_times(gap_times_DIF, gap_times_DAR, 20)


#Just look at outlier plots for the pion --> e data.
out_data = event_visualization(PiEtree, 0, False, True, 100)


#Compare energy deposition and gap times of DARs and DIFs for pion --> muon --> e data.
PiMuEfile = r.TFile("pienux_out_stripped_muons.root")
PiMuEtree = PiMuEfile.Get("atar")
# print([x.GetName() for x in tree.GetListOfBranches()])
# print("\n")
print("\n\nPion --> Muon --> e Data\n\n")
(max_Es_DIF, gap_times_DIF) = event_visualization(PiMuEtree, 0, False, False, 50)
(max_Es_DAR, gap_times_DAR) = event_visualization(PiMuEtree, 1, False, False, 50)
compare_max_edep(max_Es_DIF, max_Es_DAR, 20)
compare_gap_times(gap_times_DIF, gap_times_DAR, 20)


#Just look at outlier plots for the pion --> muon --> e data.
out_data = event_visualization(PiMuEtree, 0, False, True, 50)