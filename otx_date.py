import argparse, json, logging, urllib.request, yaml
from datetime import datetime,timedelta


def pull_new_otx_iocs():
    with open('api.yml') as api_file:
        api_keys = yaml.load(api_file, Loader=yaml.FullLoader)
    url='https://otx.alienvault.com:443/api/v1/pulses/subscribed'
    headers={'X-OTX-API-KEY': api_keys['otx']}
    req = urllib.request.Request(url, headers=headers)

    with urllib.request.urlopen(req) as data:
        otx_pull = json.loads(data.read().decode())
        otx_pull_file_name = 'otx_files/otx-' + datetime.now().strftime('%d-%m-%Y-%H-%M-%S') + '.json'
        write_file(otx_pull_file_name, otx_pull)
    
    return otx_pull


def get_file(test_file_name):
    with open(test_file_name) as otx_data:
        otx_json = json.load(otx_data)
    return otx_json


def write_file(out_file_name, out_file_json):
    with open(out_file_name, 'w') as write_file_name:
        json.dump(out_file_json, write_file_name)


def parse_data(otx_entry):
    results = otx_entry['results']
    for result in results[:]:
        indicators = result['indicators']
        iocs_removed = 0
        iocs_added = 0
        for indicator in indicators[:]:
            if compare_date(indicator['created']) > timedelta(days=7):
                result['indicators'].remove(indicator)
                iocs_removed += 1
            else:
                iocs_added +=1
        if iocs_removed > 0:
            logging.info('OTX Pulse {} - "{}" - Removed {} IOCs'.format(result['id'],result['name'],iocs_removed))
        else:
            logging.info('OTX Pulse {} - "{}" - Added {} IOCs'.format(result['id'],result['name'],iocs_added))
        if not result['indicators']:
            otx_entry['results'].remove(result)
            logging.info('OTX Pulse {} - "{}" - Removed full Pulse'.format(result['id'],result['name']))
    return otx_entry


def compare_date(ioc_date):
    current_date = datetime.now()
    ioc_date_compare = datetime.strptime(ioc_date, '%Y-%m-%dT%H:%M:%S')
    return current_date - ioc_date_compare


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('out_file', help='Print to file (provide file name)')
    parser.add_argument('-t', '--test_file', help='Run against test file - this will prevent pull of new IOCs')
    args = parser.parse_args()

    logging.basicConfig(filename='otx.log', filemode='a', level=logging.INFO, format='%(asctime)s - %(message)s')

    if args.test_file:
        otx_test_file = get_file(args.test_file)
        new_otx_json = parse_data(otx_test_file)
    else:
        new_otx_json = parse_data(pull_new_otx_iocs())

    write_file(args.out_file, new_otx_json)