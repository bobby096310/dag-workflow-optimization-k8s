from k_function import *

def main():
    args = sys.argv[1:]
    if(len(args) < 1):
        pprint("Please enter action:")
        return
    elif (args[0] == "get"):
        if (len(args) < 3):
            pprint("Please enter namespace and function name:")
            return
        pprint(get_function(args[1], args[2]))
    elif (args[0] == "patch"):
        if (len(args) < 4):
            pprint("Please enter namespace, function name, and concurrency:")
            return
        body = concurrency_body(args[3])
        pprint(patch_function(args[1], args[2], body))
    
if __name__ == "__main__":
    main()
