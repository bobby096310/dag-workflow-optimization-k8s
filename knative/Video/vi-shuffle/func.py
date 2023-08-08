from utils import *
from parliament import Context


def mainFunc(event):
    # TODO implement
    # Remove below line for ORG DAG
    # event = event["detail"]["indeces"]
    trips = []
    counter_out = 0
    src_id_out = ""
    detect_prob = -1
    for eve in range(len(event)):
        counter_out = event[eve]["counter"]
        src_id_out = event[eve]["source_id"]
        detect_prob = event[eve]["detect_prob"]
        for c in range(event[eve]["counter"]):
            val = event[eve]["values"][c]
            m1 = event[eve]["millis1"][c]
            m2 = event[eve]["millis2"][c]
            trips.append((val, m1, m2))

    print(trips)
    # random.shuffle(trips)
    # print(trips)

    returnedDic = {}
    # returnedDic["source_id"] = src_id_out
    returnedDic["detail"] = {}
    returnedDic["detail"]["indeces"] = []

    v = []
    m1 = []
    m2 = []
    count = 0
    step_size = len(event)
    for eve in range(len(event)):
        count = eve
        for t in range(counter_out):
            v.append(trips[count][0])
            m1.append(trips[count][1])
            m2.append(trips[count][2])
            count = count + step_size

        # print(v)
        # print(m1)
        # print(m2)

        obj = {
            'statusCode': 200,
            'counter': counter_out,
            'millis1': m1,
            'millis2': m2,
            'source_id': src_id_out,
            'detect_prob': detect_prob,
            'values': v,
            'body': json.dumps('Download/Split/Upload Successful!'),
        }
        returnedDic["detail"]["indeces"].append(obj)
        v = []
        m1 = []
        m2 = []

    return returnedDic


def main(context: Context):
    """
    Function template
    The context parameter contains the Flask request object and any
    CloudEvent received with the request.
    """

    # Add your business logic here
    print("Received request")

    if 'request' in context.keys():
        ret = pretty_print(context.request)
        print(ret, flush=True)
        exeRet = mainFunc(context.request.get_json())
        everything = {"Result": exeRet, "Received": ret, "Sent": payload_print(context.request)}
        return everything, 200
    else:
        print("Empty request", flush=True)
        return "{}", 200
