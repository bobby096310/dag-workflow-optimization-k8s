from pprint import pprint
from datetime import datetime
import requests
from multiprocessing import Process, Manager

url = "http://10.102.102.237"

def execute(func, data):
    headers = {"Content-Type": "application/json; charset=utf-8", "Host": func + ".default.svc.cluster.local"}
    start_time = datetime.now()
    resp = requests.post(url, headers=headers, json=data)
    end_time = datetime.now()
    print(func + " latency: {:d}".format(int((end_time-start_time).total_seconds())))
    return(resp.json())
    
def execute_map(func, data, out_list):
    out_list.append(execute(func, data)['Result'])
    
def map(func, in_list):
    manager = Manager()
    out_list = manager.list()
    ths=[]
    for input in in_list:
        ths.append(Process(target=execute_map,  args=(func, input, out_list)))
    for t in ths:
        t.start()
    for t in ths:
        t.join()
    return out_list
        

def main():
    start_time = datetime.now()
    input = {"src_name": "0", "DOP": "30", "detect_prob": 2}
    re1 = execute('vi-split', input)
    input2s = re1['Result']['detail']['indeces']
    '''
    re2s = []
    for input2 in input2s:
        re2 = execute('vi-extract', input2)
        re2s.append(re2['Result'])
    input3s = re2s
    '''
    input3s = list(map('vi-extract', input2s))
    print(input3s)
    re3 = execute('vi-shuffle', input3s)
    input4s = re3['Result']['detail']['indeces']
    re4 = map('vi-classify', input4s)
    pprint(re4)
    end_time = datetime.now()
    print("E2E latency:: {:d}".format(int((end_time-start_time).total_seconds())))

if __name__ == "__main__":
    main()
