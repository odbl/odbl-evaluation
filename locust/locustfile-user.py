import random
import configparser

from locust import HttpUser, task, between

config = configparser.ConfigParser()
c = config.read('../config.cfg')


class QuickstartUser(HttpUser):
    wait_time = between(1, 1200)
    host = "https://node01-odbl" + config.get('basic', 'node_base_url')

    @task
    def status_page(self):

        self.client.get("node/datasets?page=" + str(random.randint(1,50000)))
