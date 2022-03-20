# nmr-usage
Edit the script at the bottom (https://github.com/barrown/nmr-usage/blame/main/Bruker_NMR_usage.py#L109) to point to your directory containing Bruker NMR files and run it.

In the same directory as the script a "NMR Usage.csv" file will be written, with each line giving some information about that NMR experiment:
* when - the start date
* hadrons - the number part of the spin, e.g. 11B is 11
* element - the elemental symbol
* shimprobe - the name of the probe as given in the shim file
* masr - spinning speed for solid-state experiments
* pulprog - name of the pulse program
* probe - probe as given in the acqus file
* ns - number of scans actually acquired
* secs - duration the experimental actually ran in seconds

At the end of the .csv file aggregated stats are given for the total duration and experiment count, per nucleus

You can add/remove parameters of interest if they are in the acqus file, however some lists like D1 and P1 require you to enumerate the lines first then skip one head to find the actual value.

At the point of finding out when an experiment was run (https://github.com/barrown/nmr-usage/blame/main/Bruker_NMR_usage.py#L16) you can choose to "continue" according to a condition, e.g. before a certain time.
