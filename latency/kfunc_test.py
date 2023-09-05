from k_function import *

def main():
    args = sys.argv[1:]
    if(len(args) < 1):
        pprint("Please enter action:")
        return
    elif (args[0] == "get"):
        if (len(args) < 2):
            pprint("Please enter function name:")
            return
        pprint(get_function(args[1]))
    elif (args[0] == "patch_conc"):
        if (len(args) < 3):
            pprint("Please enter function name, and concurrency:")
            return
        body = concurrency_body(args[2])
        pprint(patch_function(args[1], body))
    elif (args[0] == "patch_cpu"):
        if (len(args) < 4):
            pprint("Please enter function name, and cpu requests and limits:")
            return
        body = resources_body(args[2], args[3])
        pprint(patch_function(args[1], body))
    
if __name__ == "__main__":
    main()
