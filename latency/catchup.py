from pdf_cdf import *

def analyze_result(raw_data):
    E2Es = []
    for run in raw_data:
        E2Es.append(float(run.split(' ')[2]))
    E2E_mean = sum(E2Es) / len(E2Es)
    return "Mean " + str(E2E_mean) + " N95 " +  str(get_n_latency(E2Es, 95)) + " Count " + str(len(E2Es))

def transferlog(filename):
    with open(filename, 'r') as file:
        #lines = file.readlines()
        lines = [line for line in file]
        return analyze_result(lines)    

def main():
    args = sys.argv[1:]
    if (len(args) < 1):
        print("Please enter filename")
        return
    print(args[0][5:-4] + " " +  transferlog(args[0]))
    
if __name__ == "__main__":
    main()
