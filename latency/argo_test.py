from argo_utils import *

def main():
    args = sys.argv[1:]
    if(len(args) < 1):
        pprint("Please enter action:")
        return
    elif (args[0] == "getwfs"):
        if (len(args) < 2):
            pprint("Please enter namespace")
            return
        pprint(get_wf_latency_all(args[1]))
    elif (args[0] == "getwfsbyFunc"):
        if (len(args) < 3):
            pprint("Please enter namespace and function name")
            return
        pprint(get_wf_latency_all(args[1], by_func=args[2]))
    elif (args[0] == "getwf"):
        if (len(args) < 3):
            pprint("Please enter namespace and workflow name")
            return
        pprint(get_wf_latency(args[1], args[2]))
    elif (args[0] == "create"):
        if (len(args) < 3):
            pprint("Please enter namespace and workflow structure file name")
            return
        pprint(create_workflow(args[1], args[2]))
    elif (args[0] == "runwfs"):
        if (len(args) < 5):
            pprint("Please enter namespace, workflow structure file name and times")
            return
        pprint(run_workflows(args[1], args[2], args[3], {"timeout": str(args[4])}))
    
if __name__ == "__main__":
    main()
