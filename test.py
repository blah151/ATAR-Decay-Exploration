import ROOT as r
import os
import sys
import pandas

def process_file(infile):
    assert os.path.exists(infile)

    f = r.TFile(infile)
    # f.ls()
    t = f.Get("calorimeter")
    print(t)
    n = t.GetEntries()
    print(f"There are {n} events in this file!")

    results = []
    # ni = t.Draw("theta:phi","","goff") # goff = graphics off
    # for i in range(ni):
    #     theta = t.GetV1()[i]
    #     phi = t.GetV2()[i]
    #     results.append({
    #         'file':infile,
    #         'event':i,
    #         'theta':theta,
    #         'phi':phi
    #     })
    for i, e in enumerate(t):
        results.append({
            'file':infile,
            'event':i,
            'theta':e.theta,
            'phi':e.phi,
            'test':'wow!'
        })
    
    f.Close()

    return results
    # {
    #     'file':infile,
    #     'n':n
    # }

def main():
    # python test.py arg arg2 arg3
                    #^^^^^^^^^^^^^
    file_list = sys.argv[1] # get command line args
    files = []
    with open(file_list, 'r') as f:
        for line in f:
            files.append(line.strip()) # removes trailing \n: "  test \n" -> "test"
    print(files)
    results = []
    for file in files:
        results += process_file(file)
        break

    # print(results)
    df = pandas.DataFrame(results)
    print(df.head())
    df.to_csv("output.csv")

if __name__ == '__main__':
    main()