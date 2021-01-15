import requests
import json
import time
import os

from urllib3.util.retry import Retry
from requests.adapters import HTTPAdapter


class APIManager:

    def __init__(self, dataset_folder, authority_node, node_base_url):
        self.authority_node = authority_node
        self.base_folder = dataset_folder
        self.node_base_url = node_base_url

    def get_base_urls(self, node_count):
        nodes = []
        for i in range(2, node_count+2):
            node_id = "node" + str(i).zfill(2) + "-odbl"
            nodes.append("https://" + node_id + self.node_base_url)
        return nodes

    def setup(self, publisher_nodes):
        start_time = time.time()
        elapsed = []
        for p in publisher_nodes:

            print('Setup ' + self.ano_url(p))
            payload = {'action': 'identityCard'}
            r = requests.post(p + '/admin/node', json=payload)
            identity_card = r.json()['identityCard']
            print(identity_card)
            headers = {
                'Content-Type': 'text/plain'
            }
            r2 = requests.post(self.authority_node + '/admin/addpeer', data=identity_card, headers=headers)
            elapsed_time = time.time() - start_time
            elapsed.append(elapsed_time)
            print("Took " + str(elapsed_time) + " seconds")
            print(elapsed)

    def setup_single(self, url):
        print('Setup ' + self.ano_url(url))
        payload = {'action': 'identityCard'}
        r = requests.post(url + '/admin/node', json=payload)
        identity_card = r.json()['identityCard']
        print(identity_card)
        headers = {
            'Content-Type': 'text/plain'
        }
        r2 = requests.post(self.authority_node + '/admin/addpeer', data=identity_card, headers=headers)

    def reset(self, publisher_nodes):
        for p in publisher_nodes:
            print('Reset ' + self.ano_url(p))
            payload = {'action': 'reset'}
            r = requests.post(p + '/admin/database', json=payload)

    def online(self, nodes):
        start_time = time.time()
        for n in nodes:
            url = n + "/node/blockchain"
            result = requests.get(url=url)
            if result.status_code == 200:
                print(self.ano_url(n) + " is online")
            else:
                print(self.ano_url(n) + " is offline")
        elapsed_time = time.time() - start_time
        print("Took " + str(elapsed_time) + " seconds")

    def chain(self, nodes):
        for n in nodes:
            print(">>> " + self.ano_url(n))
            url = n + "/node/datasets"
            #print(">>> " + self.ano_url(n))
            result = requests.get(url=url)
            if result.status_code == 200:
                payload = result.json()
                print("Datasets " + str(payload['count']))
            else:
                print(self.ano_url(n) + " is offline")

    def load_datasets(self, folders, start=0, max_datasets=10000000000):
        for f in folders:
            folder = self.base_folder + f
            print(folder)
            self.transaction_request(folder, start, max_datasets)

    def transaction_request(self, folder, start=0, max_datasets=10000000000):
        datasets = []
        with os.scandir(folder) as entries:
            i = 1
            for entry in entries:
                datasets.append(entry)
                if i == max_datasets:
                    break
                i = i + 1

        datasets = datasets[start:]
        print(len(datasets))

        i = 1
        j = 1
        payload = []
        for d in datasets:
            # if i % 100 == 0:
            #     print(i)
            with open(d, encoding="utf8") as file:
                #print(file.name)
                try:
                    payload.append(json.load(file))
                except:
                    pass
                #time.sleep(0.1)
                #create_transaction(req)

            if j == 500 or i == len(datasets):
                req = {
                    "bulk": True,
                    "payload": payload
                }
                print(folder + " Added: " + str(len(req['payload'])))
                #self.create_transaction(req)
                payload = []
                j = 0
                print(folder + " Count " + str(i))
            if i == max_datasets:
                break
            i = i + 1
            j = j + 1

    def create_transaction(self, dataset):
        try:
            s = requests.Session()
            retries = Retry(total=5,
                            backoff_factor=1)

            s.mount('https://', HTTPAdapter(max_retries=retries))
            url = "https://node01-odbl" + self.node_base_url + "/node/transactions?debug=true"
            s.post(url, json=dataset)
        except:
            pass


    def ano_url(self, url):
        return url[8:19]
