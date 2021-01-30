import argparse, json, urllib.request, os
from datetime import datetime


def pull_new_otx_iocs():
    api_key = 0 #pull from api.yml
    url="https://otx.alienvault.com:443/api/v1/pulses/subscribed"
    headers={'X-OTX-API-KEY': api_key}
    req = urllib.request.Request(url, headers=headers)

    with urllib.request.urlopen(req) as data:
        otx_pull = json.loads(data.read().decode())
        file_name = "otx-" + datetime.now().strftime("%d-%m-%Y-%H-%M-%S") + ".json"
        with open(file_name, 'w') as outfile:
            json.dump(otx_pull, outfile)


def format_data(otx_entry):
    ioc_count = 0
    ioc_types=set()
    for indicator in otx_entry['indicators']:
        ioc_count += 1
        ioc_types.add(indicator['type'])
    parameters = [
        otx_entry['name'],
        otx_entry['created'],
        otx_entry['modified'],
        ioc_types,
        ioc_count
    ]
    template = """Pulse Name: {0}
    Created on: {1}
    Modified on: {2}
    IOC Types: {3}
    {4} IOCs\n"""
    return template.format(*parameters)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-p", "--pull", help="Pull new OTX IOCs", action="store_true")
    parser.add_argument("-o", "--out", help="Print to file (provide file name)")
    args = parser.parse_args()

    if args.pull:
        pull_new_otx_iocs()

    otx_files = set()

    for file in os.listdir("otx_files/"):
        otx_files.add(file)

    otx_dict = dict()

    for otx_file in otx_files:
        file_name = "otx_files/" + otx_file
        with open(file_name) as otx_data:
            otx_json = json.load(otx_data)
        for result in otx_json['results']:
            key = result['id']
            otx_dict[key] = result

    for otx_entry in otx_dict.values():
        if args.out:
            with open(args.out, 'a') as write_file:
                write_file.write(format_data(otx_entry))
        else:
            print(format_data(otx_entry))