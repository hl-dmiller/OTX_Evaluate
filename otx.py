import argparse, json, urllib.request, os
from datetime import datetime


def pull_new_otx_iocs():
    url="https://otx.alienvault.com:443/api/v1/pulses/subscribed"
    headers={'X-OTX-API-KEY': "f3805c37fb6aeb0e8e2811ca3ccd3f9b117c0a8e83d2b22c326111b7bcb0e320"}
    req = urllib.request.Request(url, headers=headers)

    with urllib.request.urlopen(req) as data:
        otx_pull = json.loads(data.read().decode())
        file_name = "otx-" + datetime.now().strftime("%d-%m-%Y-%H-%M-%S") + ".json"
        with open(file_name, 'w') as outfile:
            json.dump(otx_pull, outfile)


def format_data(parameters):
    template = """Pulse Name: {0}
    Created on: {1}
    Modified on: {2}
    IOC Types: {3}
    {4} IOCs\n"""
    return template.format(*parameters)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-p", "--pull", help="Pull new OTX IOCs", action="store_true")
    args = parser.parse_args()

    if args.pull:
        pull_new_otx_iocs()

    otx_files = set()

    for file in os.listdir("./"):
        f = file.split("-")
        if f[0] == "otx":
            otx_files.add(file)

    for otx_file in otx_files:
        with open(otx_file) as otx_data:
            otx_json = json.load(otx_data)
        for result in otx_json['results']:
            ioc_count = 0
            ioc_types=set()
            for indicator in result['indicators']:
                ioc_count += 1
                ioc_types.add(indicator['type'])
            parameters = (
                result['name'],
                result['created'],
                result['modified'],
                ioc_types,
                ioc_count
            )
            print(format_data(parameters))