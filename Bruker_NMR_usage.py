import os
from datetime import datetime

# this is the datetime format used in Bruker audita.txt
FMT = '%Y-%m-%d %H:%M:%S'

def nmrusage(dataroot):
    '''Takes a directory path and writes to "w", an already open file object'''
    for root, dirs, files in os.walk(dataroot):
        if 'audita.txt' in files:
            acqusfile = root+"\\acqus"
            audita = root+"\\audita.txt"
            shimfile = root+"\\shimvalues"

            # timing data are checked in "audita.txt", as "acqus" gets changed on processing
            with open(audita, 'r') as a:auditlinelist = a.readlines()
            
            # we regularly WRPA and then CONVDTA the fid which can lead to double-counting
            if any((True for line in auditlinelist if "<convdta" in line)):continue
            
            # all Topspin 3 and 4 experiments have the timing information on fixed line numbers
            startline = auditlinelist[8].split()
            endline = auditlinelist[6].split()

            # grab the date the experiment finished and output so you can track progress while the script runs
            when = endline[1][3:]
            print(when, root.split('\\')[-1])
            
            # find the real duration of the experiment
            try:
                start = startline[2] + " " + startline[3][:-4]  # [:-4] part takes off the ".012" milliseconds
                end = endline[1][3:] + " " + endline[2][:-4]
                tdelta = datetime.strptime(end, FMT) - datetime.strptime(start, FMT)
            except: # acquisition still in progress, convdta, or something else
                print(when, root.split('\\')[-1],"<--- CAUSED AN ERROR")
                continue
            
            # convert into seconds (as a string)
            expt = str(tdelta.days*86400 + tdelta.seconds)

            # optionally get parameters of interest
            with open(acqusfile, 'r') as e:acquslinelist = e.readlines()
            for line in acquslinelist:
                if '##$PROBHD=' in line:
                    probe = line.replace('##$PROBHD= ','').strip()
                elif '##$MASR=' in line:
                    masr = line.split()[1]
                elif "##$NUC1=" in line:
                    nuc = line.split()[1]
                    nuc = nuc[1:-1]
                elif "##$PULPROG=" in line:
                    pulprog = line.split()[1]
                    pulprog = pulprog[1:-1]
                elif "##$MASR=" in line:
                    masr = line.split()[1]
                elif "##$NS=" in line:
                    ns = line.split()[1]

            # you can also find out the probe from the shimfile, if the shim settings were loaded
            try:
                with open(shimfile, 'r') as f:shimfilelinelist = f.readlines()
                for line in shimfilelinelist:
                    if "#$$PROBENAME=" in line:
                        shimprobe = line.split('=')[1].strip()
            except:
                pass

            # for graphing purposes later it's useful to have the nucleus as a number rather than a string
            if nuc == "1H":
                hadrons = "1"
                element = "H"
            elif nuc == "2H":
                hadrons = "2"
                element = "H"
            elif nuc == "6Li":
                hadrons = "6"
                element = "Li"
            elif nuc == "7Li":
                hadrons = "7"
                element = "Li"
            elif len(nuc) == 5:
                hadrons = nuc[:3]
                element = nuc[3:]
            else:
                hadrons = nuc[:2]
                element = nuc[2:]

            # actually write out all the information we gathered to the file
            w.write(start[:10]+','+hadrons+','+element+','+shimprobe+','+masr+','+pulprog+','+probe+','+ns+','+expt+','+'\n')

            # to generate some aggregated stats we need to map out the total duration and number of experiments, per nucleus
            if not nuc in nuclist: # new nucleus!
                nuclist.append(nuc) # add to list so it's not new anymore
                nuctimedict[nuc] = 0 # create dictionary element, starting at zero
                nucspectradict[nuc] = 0

            nuctimedict[nuc] = nuctimedict[nuc] + expt
            nucspectradict[nuc] = nucspectradict[nuc] + 1


# this is where you can change the output filename
with open('NMR Usage.csv', 'w') as w:
    nuclist = [] # a list of nuclei the script has come across
    nuctimedict = {} # a dictionary of duration, per nucleus
    nucspectradict = {} # a dictionary of number of experiments, per nucleus
    w.write("when,hadrons,element,shimprobe,masr,pulprog,probe,ns,secs,\n") # header for the csv file

    # add your paths to the directories to scan here!
    nmrusage("C:\\Bruker\\TopSpin4.0.5\\data\\tesla\\2018\\")
    nmrusage("C:\\Bruker\\TopSpin4.0.5\\data\\tesla\\2019\\")

    # output the aggregated stats
    w.write("\n,nuc,secs\n")
    for items in nuctimedict.items():w.write(",%s,%f\n" % items) # list out a line per nucleus of total experimental time
    w.write(",,=%f/3600/24\n" % sum(nuctimedict.values())) # and the total
    w.write("\n,,,,nuc,expts\n")
    for items in nucspectradict.items():w.write(",,,,%s,%d\n" % items) # list out a line per nucleus of experimental counts
    w.write(",,,,,%f\n" % sum(nucspectradict.values())) # and the total