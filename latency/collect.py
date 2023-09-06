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

def main():
    groupnames = ["video_1_1_0", "video_2_1_0", "video_3_1_0"]
    for groupname in groupnames:
        copyandpaste(groupname)
        print(transferlog(os.path.join("logs/group/", groupname + ".txt")))

if __name__ == "__main__":
    main()
