import argparse, json, urllib.request, os, yaml
from datetime import datetime
from collections import OrderedDict 


def pull_new_otx_iocs():
    with open("api.yml") as api_file:
        api_keys = yaml.load(api_file, Loader=yaml.FullLoader)
    url="https://otx.alienvault.com:443/api/v1/pulses/subscribed"
    headers={'X-OTX-API-KEY': api_keys['otx']}
    req = urllib.request.Request(url, headers=headers)

    with urllib.request.urlopen(req) as data:
        otx_pull = json.loads(data.read().decode())
        otx_pull_file_name = "otx_files/otx-" + datetime.now().strftime("%d-%m-%Y-%H-%M-%S") + ".json"
        with open(otx_pull_file_name, 'w') as otx_pull_file:
            json.dump(otx_pull, otx_pull_file)


def format_data(otx_entry):
    ioc_count = 0
    ioc_types=set()
    indicators=set()
    for indicator in otx_entry['indicators']:
        ioc_count += 1
        ioc_types.add(indicator['type'])
        if indicator['type'] == "domain":
            indicators.add(indicator['indicator'])
    top_10k_count = evaluate_top_10k(indicators)
    parameters = [
        otx_entry['name'],
        otx_entry['created'],
        otx_entry['modified'],
        ioc_types,
        ioc_count,
        top_10k_count
    ]
    template = """Pulse Name: {0}
    Created on: {1}
    Modified on: {2}
    IOC Types: {3}
    IOCs: {4}
    Domains in top10k: {5}\n"""
    return template.format(*parameters)


def evaluate_top_10k(indicators):
    with open("opendns-top-domains.txt") as top10k_file:
        top_10k_list = top10k_file.readlines()
    top_10k_list = [x.strip('\n') for x in top_10k_list]
    top_10k_iocs = 0
    for indicator in indicators:
        for ioc in top_10k_list:
            if indicator == ioc:
                top_10k_iocs += 1
    return top_10k_iocs


def parse_files(otx_files):
    for otx_file in otx_files:
        file_name = "otx_files/" + otx_file
        with open(file_name) as otx_data:
            otx_json = json.load(otx_data)
        for result in otx_json['results']:
            key = result['id']
            otx_dict[key] = result


def return_evaluated_files(evaluated_values):
    sorted_values=OrderedDict()
    for i in sorted(evaluated_values.keys()):
        sorted_values[i] = evaluated_values[i]
    for otx_entry in sorted_values.values():
        if args.out:
            with open(args.out, 'a') as evaled_file:
                evaled_file.write(format_data(otx_entry))
        else:
            print(format_data(otx_entry))


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

    parse_files(otx_files)

    return_evaluated_files(otx_dict)