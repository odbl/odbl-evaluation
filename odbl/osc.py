import os
import sys
import json
import time


class OSCDeployer:

    def __init__(self, node_base_url, odbl_image, mongo_image, oc_project, authority_node):
        self.node_base_url = node_base_url
        self.odbl_image = odbl_image
        self.mongo_image = mongo_image
        self.oc_project = oc_project
        self.authority_node = authority_node
        self.network_delay = {
            "\"enabled\"": True,
            "\"min\"": 0,
            "\"max\"": 1000
        }

    def extra_node(self):
        self.s("oc project %s" % self.oc_project)
        mongo_name = "node32-mongo"
        odbl_name = "node32-odbl"
        odbl_title = "node32 name"
        url = "http://" + odbl_name + ":8080"
        self.s(self.cmd_new_app(mongo_name, "", "mongo"))
        self.s(self.cmd_set_volume(mongo_name, mongo_name + "-volume", 40, "/data/db"))
        self.s(self.cmd_import_image(odbl_name, self.odbl_image))
        env = {
            "PORT": 8080,
            "NODE_ID": odbl_name,
            "MONGO_HOST": mongo_name,
            "NAME": odbl_title,
            "URL": url,
            "MONGO_PORT": 27017,
            "PIVEAU_LOG_LEVEL": "DEBUG",
            "INITIAL_PRIMARY": "node01-odbl",
            "AUTO_SYNC": True,
            "TACT": 500,
            "AUTHORITY_NODE": self.authority_node
        }
        values = ""
        for key, value in env.items():
            values = values + " -e " + key + "=\"" + str(value) + "\""
        print(values)
        self.s(self.cmd_new_app(odbl_name, values, odbl_name))
        self.s(self.cmd_create_route(odbl_name, 8080))

    def remove_extra_node(self):
        mongo_name = "node32-mongo"
        odbl_name = "node32-odbl"
        self.s("oc project %s" % self.oc_project)
        self.s(self.cmd_delete_dc(mongo_name))
        self.s(self.cmd_delete_service(mongo_name))
        self.s(self.cmd_delete_pvc(mongo_name + "-volume"))
        self.s(self.cmd_delete_dc(odbl_name))
        self.s(self.cmd_delete_service(odbl_name))
        self.s(self.cmd_delete_route(odbl_name))


    def deploy_odbl(self, id, node_env):
        mongo_name = id + "-mongo"
        odbl_name = id + "-odbl"
        odnl_title = id + " name"
        url = "http://" + odbl_name + ":8080"
        self.s(self.cmd_import_image("mongo:4.4.0", self.mongo_image))
        self.s(self.cmd_new_app(mongo_name, "", "mongo:4.4.0"))
        self.s(self.cmd_set_volume(mongo_name, mongo_name + "-volume", 5, "/data/db"))
        self.s(self.cmd_import_image(odbl_name, self.odbl_image))
        env = {
            "PORT": 8080,
            "NODE_ID": odbl_name,
            "MONGO_HOST": mongo_name,
            "NAME": odnl_title,
            "URL": url,
            "MONGO_PORT": 27017,
            "PIVEAU_LOG_LEVEL": "INFO",
            "INITIAL_PRIMARY": "node02-odbl",
            "TACT": 500,
            "AUTHORITY_NODE": self.authority_node,
            "NETWORK_DELAY": json.dumps(self.network_delay),
        }
        values = ""
        for key, value in env.items():
            values = values + " -e " + key + "=\"" + str(value) + "\""
        self.s(self.cmd_new_app(odbl_name, values, odbl_name))
        self.s(self.cmd_create_route(odbl_name, 8080))

    def deploy(self, node_no):
        print("Deploying")
        node_count = node_no
        self.s("oc project %s" % self.oc_project)
        node_ids = []
        node_env = []

        for i in range(2, node_count+2):
            node_id = "node" + str(i).zfill(2)
            node_ids.append(node_id)

        start_time = time.time()

        eva = {}
        for n in node_ids:
            print("Deploy " + n)
            self.deploy_odbl(n, node_env)
            eva[n] = time.time() - start_time

        elapsed_time = time.time() - start_time
        print("Took " + str(elapsed_time) + " seconds")
        print(eva)

    def remove_odbl(self, id):
        mongo_name = id + "-mongo"
        odbl_name = id + "-odbl"
        self.s("oc project %s" % self.oc_project)
        self.s(self.cmd_delete_dc(mongo_name))
        self.s(self.cmd_delete_service(mongo_name))
        self.s(self.cmd_delete_pvc(mongo_name + "-volume"))
        self.s(self.cmd_delete_dc(odbl_name))
        self.s(self.cmd_delete_service(odbl_name))
        self.s(self.cmd_delete_route(odbl_name))

    def remove(self, node_no):
        print("Removing")
        node_count = node_no
        self.s("oc project %s" % self.oc_project)
        node_ids = []
        for i in range(2, node_count+2):
            node_id = "node" + str(i).zfill(2)
            node_ids.append(node_id)

        for n in node_ids:
            self.remove_odbl(n)

    def deploy_authority(self):
        self.s("oc project %s" % self.oc_project)
        self.s(self.cmd_new_app("authority-mongo", "", "mongo:4.4.0"))
        self.s(self.cmd_set_volume("authority-mongo", "authority-mongo-volume", 5, "/data/db"))
        self.s(self.cmd_import_image("authority-odbl", self.odbl_image))
        env = {
            "MODE": "authority",
            "PORT": 8080,
            "NODE_ID": "auth:edp",
            "MONGO_HOST": "authority-mongo",
            "MONGO_PORT": 27017,
            "MONGO_DB": "auth-edp"
        }
        values = ""
        for key, value in env.items():
            values = values + " -e " + key + "=\"" + str(value) + "\""

        self.s(self.cmd_new_app("authority-odbl", values, "authority-odbl"))
        self.s(self.cmd_create_route("authority-odbl", 8080))

    def remove_authority(self):
        self.s("oc project %s" % self.oc_project)
        self.s(self.cmd_delete_dc("authority-mongo"))
        self.s(self.cmd_delete_service("authority-mongo"))
        self.s(self.cmd_delete_pvc("authority-mongo-volume"))
        self.s(self.cmd_delete_dc("authority-odbl"))
        self.s(self.cmd_delete_service("authority-odbl"))
        self.s(self.cmd_delete_route("authority-odbl"))

    def deploy_node01(self):
        self.s("oc project %s" % self.oc_project)
        mongo_name = "node01-mongo"
        odbl_name = "node01-odbl"
        odbl_title = "node01 name"
        url = "http://" + odbl_name + ":8080"
        self.s(self.cmd_new_app(mongo_name, "", self.mongo_image))
        self.s(self.cmd_set_volume(mongo_name, mongo_name + "-volume", 40, "/data/db"))
        self.s(self.cmd_import_image(odbl_name, self.odbl_image))
        env = {
            "PORT": 8080,
            "NODE_ID": odbl_name,
            "MONGO_HOST": mongo_name,
            "NAME": odbl_title,
            "URL": url,
            "MONGO_PORT": 27017,
            "PIVEAU_LOG_LEVEL": "DEBUG",
            "INITIAL_PRIMARY": "node01-odbl",
            "TACT": 500,
            "AUTHORITY_NODE": self.authority_node
        }
        values = ""
        for key, value in env.items():
            values = values + " -e " + key + "=\"" + str(value) + "\""
        print(values)
        self.s(self.cmd_new_app(odbl_name, values, odbl_name))
        self.s(self.cmd_create_route(odbl_name, 8080))

    def remove_node01(self):
        mongo_name = "node01-mongo"
        odbl_name = "node01-odbl"
        self.s("oc project %s" % self.oc_project)
        self.s(self.cmd_delete_dc(mongo_name))
        self.s(self.cmd_delete_service(mongo_name))
        self.s(self.cmd_delete_pvc(mongo_name + "-volume"))
        self.s(self.cmd_delete_dc(odbl_name))
        self.s(self.cmd_delete_service(odbl_name))
        self.s(self.cmd_delete_route(odbl_name))

    def deactivate_nodes(self, nodes):
        for n in nodes:
            odbl_name = n + "-odbl"
            self.s(self.cmd_delete_dc(odbl_name))
            self.s(self.cmd_delete_service(odbl_name))

    def reactivate_nodes(self, nodes):
        for n in nodes:
            odbl_name = n + "-odbl"
            odnl_title = n + " name"
            mongo_name = n + "-mongo"
            url = "http://" + odbl_name + ":8080"
            env = {
                "PORT": 8080,
                "NODE_ID": odbl_name,
                "MONGO_HOST": mongo_name,
                "NAME": odnl_title,
                "URL": url,
                "MONGO_PORT": 27017,
                "PIVEAU_LOG_LEVEL": "INFO",
                "INITIAL_PRIMARY": "node02-odbl",
                "TACT": 500,
                "AUTHORITY_NODE": self.authority_node,
                "NETWORK_DELAY": json.dumps(self.network_delay)
            }
            values = ""
            for key, value in env.items():
                values = values + " -e " + key + "=\"" + str(value) + "\""
            self.s(self.cmd_new_app(odbl_name, values, odbl_name))

    def cmd_import_image(self, name, image):
        return "oc import-image %s --from=%s --confirm" % (name, image)

    def cmd_new_app(self, name, env, image_stream="odbl"):
        return "oc new-app --name=%s --image-stream=%s %s" % (name, image_stream, env)

    def cmd_set_volume(self, dc, name, size, mount):
        return "oc set volume dc/%s --add -t pvc --claim-name=%s --claim-size=%dGi  --overwrite --claim-mode=\"ReadWriteOnce\" -m %s" % (dc, name, size, mount)

    def cmd_create_route(self, name, port):
        return "oc create route edge --service=%s --hostname=%s%s --insecure-policy=Redirect --port=%d" % (name, name, self.node_base_url, port)

    def cmd_set_env(self, dc, env_dict):
        values = ""
        for key, value in env_dict.items():
            values = values + " " + key + "=" + str(value)
        return "oc set env dc/%s %s" % (dc, values)

    def cmd_delete_service(self, name):
        return "oc delete service %s" % name

    def cmd_delete_dc(self, name):
        return "oc delete dc %s" % name

    def cmd_delete_pvc(self, name):
        return "oc delete pvc %s" % name

    def cmd_delete_route(self, name):
        return "oc delete route %s" % name

    def cmd_delete_configmap(self, name):
        return "oc delete configmap %s" % name

    def s(self, cmd):
        os.system(cmd)