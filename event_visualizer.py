# This class provides functionality for viewing characteristics of selected events in the active target. The user can pass the event that they want
# along with various parameters to control how that data displays. 5 different plots are shown for each event: particle x vs. z, particle y vs. z, 
# particle z vs. t, energy deposition per plane vs. z, and energy deposited in SiPMs by (theta, phi) coordinates on the ATAR.

from logging.config import IDENTIFIER
import ROOT as r
import numpy as np
from matplotlib import pyplot as plt
from matplotlib.ticker import StrMethodFormatter
from Event import Event
import calo_analysis


class Event_Visualizer:
    #TODO: Deal with is_event_DAR along with select_events()
    '''
    The primary method that this class is used for. Uses helper functions below to give a visualization of events satisfying the specified condition(s).
    is_event_DAR: Value of 0 = decays in flight, 1 = decays at rest, 2 = all data used.
    display_text_output = True / False controls whether we should have text info / not have text info displayed.
    display_plots = True / False controls whether event data is plotted or not.
    num_events allows us to plot multiple events with the specified conditions from the tree.
    gap_times = True / False means we should show / not show gap times between decays if any are present.
    '''
    def visualize_event(self, tree_atar, tree_calo, is_event_DAR, display_text_output, event_index):

        #Use max edep per plane as a heuristic to distinguish between DIFs and DARs.
        max_Es = []

        #Keep track of gap times.
        gap_times = []

        #Process the event whose index we are given.
        e = self.process_event(tree_atar, tree_calo, event_index)

        # TODO Uncomment and fix option choice on user interface.
        if display_text_output:
            self.display_event(e)
        
        # TODO Need to incorporate 1) selection of events and 2) discrimination by max_E
    
        self.plot_event(e, 50)

        for gt in e.gap_times:
            gap_times.append(gt)

        max_Es.append(e.max_E)
            
        return (max_Es, gap_times)

    
    #Uses the TFile retreived from the .root file to get the active target and calorimeter trees, which are used by other methods to get the
    #data we need.
    def get_trees(self, r_TFile):
        self.tree_atar = r_TFile.Get("atar")
        self.tree_calo = r_TFile.Get("calorimeter")

        return self.tree_atar, self.tree_calo


    '''
    Returns the time vs. x and time vs. y data from the pixel_hits. The ATAR is made up of sheets that contain alternating horizontal or vertical strips with npixels_per_plane.
    If npixels_per_plane were 100, for instance, 100036 would represent plate 1, 36 / 100 in x, 100161 would represent plate 2, 61 / 100 in y, etc. The output for each of 
    x and y is an n x 2 matrix, where the first column contains the times corresponding to the coordinate values in the second column.
    Also extract the z (plane #) vs. time data. The third element of the tuples contained in this list and the x and y lists will contain corresponding colors to represent
    when particles have decayed.
    '''
    def process_event(self, tree_atar, tree_calo, event_index):
        #Get the specified entries from our trees so we can extract data from them.
        tree_atar.GetEntry(event_index)
        tree_calo.GetEntry(event_index)

        #Store pixel hits for the entry printed above in which a pion didn't decay at rest.
        pixel_times = tree_atar.pixel_time
        pixel_hits = tree_atar.pixel_hits
        pixel_edep = tree_atar.pixel_edep
        
        #Initialize lists for storing color (for labeling data points according to decay product), t, x, y, z, energy, and energy per plane using the Event class.
        npixels_per_plane = 100
        event = Event()

        #Init time value so 1st loop below works.
        cur_time = 0
        
        #Extract x vs. t, y vs. t, and z vs. t data. Also add indexed color coding to represent different particles.
        for i in range(pixel_hits.size()):
            #We can get the plane number using some modular arithmetic on the pixel_hits values. The convention is that these numbers start at 100,000,
            #so we must subtract 100,000. We also have to subtract 1 to deal with 100 wrapping around to 0 when it shouldn't (i.e., an "off by one"
            #error)
            plane = int(np.floor((pixel_hits[i] - 1 - 100_000) / npixels_per_plane))

            cur_val = (pixel_hits[i] - 1) % npixels_per_plane
            last_time = cur_time    #Allows us to note any large time gaps for later analysis.
            cur_time = pixel_times[i]

            event.t_data.append(cur_time)

            #Even planes give us x-values while odd-numbered planes give us y-values. We can use some simple modular arithmetic to distinguish between
            #the two. We must also add NaNs to fill in the gaps in x_data and y_data to make sure the indices of actual data points correspond to the
            #timestamps recorded in t_data.
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

            #Keep track of sum of energies deposited in each plane.
            event.E_per_plane[plane] += pixel_edep[i]

        #Keep track of particle IDs.
        event.pixel_pdgs = tree_atar.pixel_pdg

        #Keep track of maximum energy deposited per plane in this event.
        event.max_E = max(event.E_per_plane)

        #Extract all (theta, phi) pairs from the calorimeter tree.
        global_crys_dict = calo_analysis.get_crystal_data()
        #Get the IDs of the crystals that were hit at those (theta, phi) pairs from the calorimeter tree.
        event.crystal_ids = list(tree_calo.crystal)
        event.calo_edep = list(tree_calo.edep)

        # Use the IDs (tree_calo.crystal) to get the corresponding values from the dictionary of (ID: (r, theta, phi)) values (global_crys_dict).
        event.r_theta_phis = []
        for ID in event.crystal_ids:
            event.r_theta_phis.append(global_crys_dict.get(ID))

        # print("crystal IDs: ", event.crystal_ids)
        # print("edep: ", event.calo_edep)
        # print("r_theta_phis: ", event.r_theta_phis)

        return event


    #Show some useful data describing our event in textual form.
    def display_event(self, event):
        print("Length of pixel_pdgs: ", len(event.pixel_pdgs))
        print("Length of x_data: ", len(event.x_data))
        print("Length of y_data: ", len(event.y_data))
        print("Length of z_data: ", len(event.z_data))
        print("Length of t_data: ", len(event.t_data))
        print("Length of E_data: ", len(event.E_data))
        print("Length of E_per_plane: ", len(event.E_per_plane), "\n\n")

        print("pixel_pdgs: ", str(event.pixel_pdgs), "\n")
        print("x_data:", event.x_data, "\n")
        print("y_data:", event.y_data, "\n")
        print("z_data:", event.z_data, "\n")
        print("t_data:", event.t_data, "\n")
        print("E_data:", event.E_data)


    #Plot the following data from our event: x vs. t, y vs. t, z vs. t, E vs. z, and energy deposited in calorimeter by (theta, phi). The graphs 
    #will show the color-coding system used to represent different particles. Display 0 to num_planes on plots including the z variable.
    def plot_event(self, event, num_planes):

        fig = plt.figure(figsize = (15, 10))

        plt.subplot(2,4,1)
        self.plot_with_color_legend(event.z_data, event.x_data, event.pixel_pdgs)
        #plt.scatter([0, 5, 10, 15, 20, 25, 30], [0, np.nan, 10, np.nan, 20, np.nan, 30], 10, "r", label = "Pion")
        plt.title("x vs. z")
        plt.xlabel("z (plane number)")
        plt.ylabel("x (pixels)")
        plt.legend()
        plt.xlim(0, num_planes)
        plt.ylim(0, 100)

        plt.subplot(2,4,2)
        self.plot_with_color_legend(event.z_data, event.y_data, event.pixel_pdgs)
        plt.title("y vs. z")
        plt.xlabel("z (plane number)")
        plt.ylabel("y (pixels)")
        plt.xlim(0, num_planes)
        plt.ylim(0, 100)

        plt.subplot(2,4,3)
        self.plot_with_color_legend(event.t_data, event.z_data, event.pixel_pdgs)
        plt.title("z vs. t")
        plt.xlabel("t (ns)")
        plt.ylabel("z (plane number)")
        plt.gca().xaxis.set_major_formatter(StrMethodFormatter('{x:,.2f}'))     #Ensures only 2 decimal places are shown on x-axis, decreasing clutter.
        # plt.xlim(0, 60)
        plt.ylim(0, num_planes)

        plt.subplot(2,4,4)
        plt.scatter(event.z_data, event.E_data, 10, label = "e_dep")
        plt.scatter(range(50), event.E_per_plane, 10, "black", label = "e_dep per plane")
        plt.title("ATAR Energy Deposition Per Plane vs. z")
        plt.xlabel("z (plane number)")
        plt.ylabel("Energy (MeV / plane)")
        plt.legend()
        #plt.xlim(0, num_planes)

        #Here, we plot the calo analysis data.
        plt.subplot(2,4,5)

        # Plot scatterplot of energy deposited in each SIPM "pixel" in the calorimeter. Also check to see if only 1 calo entry
        # is present - in this case, the calo ID could be marked as a single volume and we just get 1000, which we don't want to count. The points are
        # color coded by energy deposition and surrounded by a black border to make faint colors easier to distinguish from the white background.
        if len(event.crystal_ids) > 1:
            color_range = event.calo_edep
            thetas = [coords[1] for coords in event.r_theta_phis]
            phis = [coords[2] for coords in event.r_theta_phis]

            plt.scatter(thetas, phis, c=color_range, cmap="YlOrRd", edgecolors="black")
            plt.xlabel("Theta (rad)")
            plt.ylabel("Phi (rad)")
            plt.title("Energy Deposited in Calorimeter SiPMs by Theta vs. Phi")
            plt.xlim(0, 3.2)
            plt.ylim(-3.2, 3.2)
            cbar = plt.colorbar()
            cbar.set_label('Amount of Energy Deposited')

        # plt.subplots_adjust(left = 0.1,
        #                     bottom = 0.1,
        #                     right = 0.9,
        #                     top = 0.9,
        #                     wspace = 0.5,
        #                     hspace = 0.4)
        
        plt.tight_layout()
        plt.show()


    #For each color in a list of color labels for different particles, plot the corresponding data.
    def plot_with_color_legend(self, x_coords, y_coords, pixel_pdgs):
        #Store colors and corresponding particle type labels in one place for ease of editing.
        colors = ["r", "b", "g", "y", "m"]
        labels = ["Pion", "Positron", "Electron", "Antimuon", "Muon"]
        particle_IDs = [211, -11, 11, -13, 13]
        
        #Store list of tuples of our data to be processed below.
        coords = list(zip(x_coords, y_coords, pixel_pdgs))

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
                elif coord[2] not in particle_IDs:
                    #Keep track of unidentified particles and their IDs so we can plot them separately after exiting this loop.
                    other_to_plot.append(coord)
                    if coord[2] not in other_IDs:
                        other_IDs.append(coord[2])
            
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


    # TODO This method needs to be adapted after first round of changes have been made.
    #Use cuts to select the events we want from the tree. Returns an integer list of the indices of the events that we want from the tree.
    #is_event_DAR: Value of 0 = decays in flight, 1 = decays at rest, 2 = all data used.
    #num_events:  Controls how many events we want to select.
    def select_events(self, tree, is_event_DAR, num_events):
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


    '''
    Compare the maximum energy deposition of decays in flight and decays at rest. Show mean, median, and standard deviation for both sets of maximum energies, then plot them in
    histogram form. One should notice that the DARs have a higher median energy deposited, though the means may be closer due to large outliers present in some DIF data.
    max_Es_DIF:  Data for maximum energies from decays in flight.
    max_Es_DAR:  Data for maximum energies from decays at rest.
    num_bins:  Controls the number of bins used when plotting data on histograms.
    '''
    def compare_max_edep(self, max_Es_DIF, max_Es_DAR, num_bins):
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


    '''
    Plots gap times given and visualizes how these correlate with DIFs / DARs.
    gap_times: A list of times in ns.
    gap_times_DIF:  Data for times between decays for DIFs in ns.
    gap_times_DAR:  Data for times between decays for DARs in ns.
    num_bins:  Controls the number of bins used when plotting data on histograms.
    '''
    def compare_gap_times(self, gap_times_DIF, gap_times_DAR, num_bins):
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