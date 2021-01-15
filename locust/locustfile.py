import json
import logging
import os
import random
import configparser

from locust import HttpUser, task, between

config = configparser.ConfigParser()
c = config.read('../config.cfg')


class QuickstartUser(HttpUser):
    wait_time = between(1, 6)
    host = "http://localhost:8084"
    data_folder = config.get('locust', 'demo_datasets')
    max_dataset = 10000

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.count = 0
        self.dataset = []
        with os.scandir(self.data_folder) as entries:
            i = 1
            for entry in entries:
                self.dataset.append(entry)
                if i == self.max_dataset:
                    break
                i = i + 1
        logging.info("Loaded %d Datasets", len(self.dataset))

        self.nodes = self.get_base_urls()

    def get_base_urls(self):
        nodes = []
        node_base_url = config.get('basic', 'node_base_url')
        for i in range(2, 30+2):
            node_id = "node" + str(i).zfill(2)
            nodes.append("https://" + node_id + "-odbl" + node_base_url)
        return nodes

    @task
    def status_page(self):
        if self.count >= len(self.dataset):
            self.count = 0

        with open(self.dataset[self.count], encoding="utf8") as file:
            payload = json.load(file)
            url = random.choice(self.nodes) + "/node/transactions"
            logging.info("Send to %s ", url)
            self.client.post(url, json=payload)
            self.count = self.count + 1
            logging.info(self.count)

