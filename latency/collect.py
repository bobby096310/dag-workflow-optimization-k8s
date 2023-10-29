import sys
import os
from pdf_cdf import *

root_dir = "logs/"
group_dir = root_dir + "group/"
data_index = 10

def transferlog(filename, limit):
    with open(filename, 'r') as file:
        #lines = file.readlines()
        lines = [line for line in file]
        if limit > 0 and limit < len(lines):
            lines = lines[:limit]
        return analyze_result(lines, data_index) #2 for E2E

def copyandpaste(groupname):
    # clear the data in the info file
    with open(os.path.join(group_dir, groupname + ".txt"), 'w') as groupfile:
        pass
    with open(os.path.join(group_dir, groupname + ".txt"), 'a') as groupfile:
        for filename in os.listdir(root_dir):
            if groupname == filename[:-10]:
                #print(filename)
                with open(os.path.join(root_dir, filename), 'r') as runfile:
                    lines = runfile.readlines()
                    groupfile.writelines(lines)

def fetch_groups():
    groupnames = []
    for filename in os.listdir(root_dir):
        if os.path.isfile(os.path.join(root_dir, filename)) and (filename[:-10] not in groupnames):
            groupnames.append(filename[:-10])
    return groupnames

def get_agg_list(groupnames, limit=0):
    agg_list = []
    with open(os.path.join(group_dir, "group_logs.txt"), 'w') as groupfile:
        pass
    for groupname in groupnames:
        copyandpaste(groupname)
        agg = groupname + " " + transferlog(os.path.join(group_dir, groupname + ".txt"), limit)
        agg_list.append(agg)
    return agg_list

def sort_by_mean(agg_list):
    dic = {}
    for agg in agg_list:
        mean = float(agg.split(" ")[2])
        dic[agg] = mean
    return list(dict(sorted(dic.items(), key=lambda x:x[1])).keys())

def sort_by_p50(agg_list):
    dic = {}
    for agg in agg_list:
        n = float(agg.split(" ")[4])
        dic[agg] = n
        # sorted(footballers_goals.items(), key=lambda x:x[1])
    return list(dict(sorted(dic.items(), key=lambda x:x[1])).keys())

def sort_by_p95(agg_list):
    dic = {}
    for agg in agg_list:
        n = float(agg.split(" ")[6])
        dic[agg] = n
    return list(dict(sorted(dic.items(), key=lambda x:x[1])).keys())

def store_statistics(agg_list):
    agg_mean = sort_by_mean(agg_list)
    agg_p50 = sort_by_p50(agg_list)
    agg_p95 = sort_by_p95(agg_list)
    with open(os.path.join(group_dir, "group_logs.txt"), 'a') as groupfile:
        print("Sort by Mean:")
        groupfile.write("Sort by Mean:\n")
        for line in agg_mean:
            print(line)
            groupfile.writelines(line + "\n")
        print("Sort by P50:")
        groupfile.write("Sort by P50:\n")
        for line in agg_p50:
            print(line)
            groupfile.writelines(str(line) + "\n")
        print("Sort by P95:")
        groupfile.write("Sort by P95:\n")
        for line in agg_p95:
            print(line)
            groupfile.writelines(line + "\n")

def get_results(groupnames):
    agg_list = get_agg_list(groupnames)
    store_statistics(agg_list)
            
def get_results_with_limit(groupnames, limit):
    agg_list = get_agg_list(groupnames, limit)
    store_statistics(agg_list)
    

def main():
    args = sys.argv[1:]
    if len(args) > 0:
        global root_dir
        root_dir = args[0]
        global group_dir
        group_dir = root_dir + "group/"
    if len(args) > 1:
        global data_index
        data_index = int(args[1])
    groupnames = fetch_groups()
    if len(args) > 2:
        get_results_with_limit(groupnames, int(args[2]))
    else:
        get_results(groupnames)
    

if __name__ == "__main__":
    main()
