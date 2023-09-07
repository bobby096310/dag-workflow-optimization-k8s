import sys
import os
from pdf_cdf import *

def transferlog(filename):
    with open(filename, 'r') as file:
        #lines = file.readlines()
        lines = [line for line in file]
        return analyze_result(lines, 10) #2 for E2E

def copyandpaste(groupname):
    # clear the data in the info file
    with open(os.path.join("logs/group/", groupname + ".txt"), 'w') as groupfile:
        pass
    with open(os.path.join("logs/group/", groupname + ".txt"), 'a') as groupfile:
        for filename in os.listdir("logs/"):
            if groupname == filename[:-10]:
                #print(filename)
                with open(os.path.join("logs/", filename), 'r') as runfile:
                    lines = runfile.readlines()
                    groupfile.writelines(lines)

def fetch_groups():
    groupnames = []
    for filename in os.listdir("logs/"):
        if os.path.isfile(os.path.join("logs/", filename)) and (filename[:-10] not in groupnames):
            groupnames.append(filename[:-10])
    return groupnames

def sort_by_mean(agg_list):
    dic = {}
    for agg in agg_list:
        mean = float(agg.split(" ")[2])
        dic[mean] = agg
    return list(dict(sorted(dic.items())).values())

def sort_by_p95(agg_list):
    dic = {}
    for agg in agg_list:
        n = float(agg.split(" ")[4])
        dic[n] = agg
    return list(dict(sorted(dic.items())).values())


def main():
    groupnames = fetch_groups()
    agg_list = []
    with open(os.path.join("logs/group/", "group_logs.txt"), 'w') as groupfile:
        pass
    for groupname in groupnames:
        copyandpaste(groupname)
        agg = groupname + " " + transferlog(os.path.join("logs/group/", groupname + ".txt"))
        #print(agg)
        agg_list.append(agg)
    agg_mean = sort_by_mean(agg_list)
    agg_p95 = sort_by_p95(agg_list)
    with open(os.path.join("logs/group/", "group_logs.txt"), 'a') as groupfile:
        groupfile.write("Sort by Mean:\n")
        for line in agg_mean:
            print(line)
            groupfile.writelines(line + "\n")
        groupfile.write("Sort by P95:\n")
        for line in agg_p95:
            print(line)
            groupfile.writelines(line + "\n")

if __name__ == "__main__":
    main()
