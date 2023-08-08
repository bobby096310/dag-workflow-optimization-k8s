import json
from parliament import Context
from utils import *


def mainFunc(event):
    if ("dummy" in event):
        return {'dummy': 'dummy combine, doing nothing'}
    print(event)
    configs_list = []
    accuracy_list = []
    for i in range(len(event)):
        for j in range(len(event[i]["trees_max_depthes"])):
            configs_list.append(event[i]["trees_max_depthes"][j])
            accuracy_list.append(event[i]["accuracies"][j])

    Z = [x for _, x in sorted(zip(accuracy_list, configs_list))]
    returned_configs = Z[-10:len(accuracy_list)]
    returned_latecy = sorted(accuracy_list)[-10:len(accuracy_list)]
    print(returned_configs)
    print(returned_latecy)
    # TODO implement
    return {
        'statusCode': 200,
        'accuracy': returned_configs,
        'returned_latecy': returned_latecy,
        'all_data': json.dumps(str(event)),
        'body': json.dumps('Hello from Lambda!')
    }


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

