import sys
import os
from catchup import transferlog

def copyandpaste(groupname):
    # clear the data in the info file
    with open(os.path.join("logs/group/", groupname + ".txt"), 'w') as groupfile:
        pass
    with open(os.path.join("logs/group/", groupname + ".txt"), 'a') as groupfile:
        for filename in os.listdir("logs/"):
            if groupname == filename[:-10]:
                print(filename)
                with open(os.path.join("logs/", filename), 'r') as runfile:
                    lines = runfile.readlines()
                    groupfile.writelines(lines)

def fetch_groups():
    groupnames = []
    for filename in os.listdir("logs/"):
        if os.path.isfile(os.path.join("logs/", filename)) and (filename[:-10] not in groupnames):
            groupnames.append(filename[:-10])
    return groupnames

def main():
    groupnames = fetch_groups()
    for groupname in groupnames:
        copyandpaste(groupname)
        agg = transferlog(os.path.join("logs/group/", groupname + ".txt"))
        print(agg)
        with open(os.path.join("logs/group/", "group_logs.txt"), 'a') as groupfile:
            groupfile.write(groupname + " " + agg + "\n")

if __name__ == "__main__":
    main()
