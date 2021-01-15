import click
import sys
import configparser
from osc import OSCDeployer
from api import APIManager

config = configparser.ConfigParser()
c = config.read('../config.cfg')
if not c:
    print('Could not find Config file')
    sys.exit()

osc_deployer = OSCDeployer(
    config.get('basic', 'node_base_url'),
    config.get('basic', 'odbl_image'),
    config.get('basic', 'mongo_image'),
    config.get('basic', 'oc_project'),
    config.get('basic', 'authority_node'),
)
api_manager = APIManager(
    config.get('basic', 'dataset_folder'),
    config.get('basic', 'authority_node'),
    config.get('basic', 'node_base_url')
)


@click.group()
def cli():
    """Welcome to the ODBl CLI Tool"""
    pass


@cli.group()
def deploy():
    """Deployment Commands"""
    pass


@cli.group()
def setup():
    """Setup Commands"""
    pass


@cli.group()
def validate():
    """Validate and Evaluation Commands"""
    pass


@deploy.command(help='Deploy ODBL nodes', name='init')
@click.option('-c', '--count', 'count', type=int, default=3, help='Number of nodes')
def init_nodes(count):
    osc_deployer.deploy(count)


@deploy.command(help='Remove ODBL nodes', name='remove')
@click.option('-c', '--count', 'count', type=int, default=3, help='Number of nodes')
def remove_nodes(count):
    osc_deployer.remove(count)


@deploy.command(help='Manage an extra ODBL node', name='extra')
@click.option('-o', '--operation', 'operation',
              type=click.Choice(['init', 'remove'], case_sensitive=False), required=True)
def manage_extra(operation):
    if operation == 'init':
        osc_deployer.extra_node()
    if operation == 'remove':
        osc_deployer.remove_extra_node()


@deploy.command(help='Manage an Authority Node', name='authority')
@click.option('-o', '--operation', 'operation',
              type=click.Choice(['init', 'remove'], case_sensitive=False), required=True)
def manage_authority(operation):
    if operation == 'init':
        osc_deployer.deploy_authority()
    if operation == 'remove':
        osc_deployer.remove_authority()


@deploy.command(help='Manage Node01', name='node01')
@click.option('-o', '--operation', 'operation',
              type=click.Choice(['init', 'remove'], case_sensitive=False), required=True)
def manage_node01(operation):
    if operation == 'init':
        osc_deployer.deploy_node01()
    if operation == 'remove':
        osc_deployer.remove_node01()


@deploy.command(help='Manage Nodes', name='manage')
@click.option('-o', '--operation', 'operation',
              type=click.Choice(['deactivate', 'activate'], case_sensitive=False), required=True)
@click.option('-n', '--node', 'nodes', multiple=True, required=True)
def manage_nodes(operation, nodes):
    nodes = list(nodes)
    if operation == 'deactivate':
        osc_deployer.deactivate_nodes(nodes)
    if operation == 'activate':
        osc_deployer.reactivate_nodes(nodes)


@setup.command(help='Setup all nodes', name='all')
@click.option('-c', '--count', 'count', type=int, default=3, help='Number of nodes')
@click.option('-p', '--publisher', 'publisher', type=str, help='Publisher URI', multiple=True)
def setup_nodes(count, publisher):
    if publisher:
        api_manager.setup(list(publisher))
    else:
        api_manager.setup(api_manager.get_base_urls(count))


@setup.command(help='Reset all nodes', name='reset')
@click.option('-c', '--count', 'count', type=int, default=3, help='Number of nodes')
@click.option('-p', '--publisher', 'publisher', type=str, help='Publisher URI', multiple=True)
def reset_nodes(count, publisher):
    if publisher:
        api_manager.reset(list(publisher))
    else:
        api_manager.reset(api_manager.get_base_urls(count))


@setup.command(help='Reset all nodes', name='single')
@click.option('-u', '--url', 'url', type=str, required=True, help='URL of the node')
def setup_single_node(url):
    api_manager.setup_single(url)


@validate.command(help='Check the online state of all nodes', name='online')
@click.option('-c', '--count', 'count', type=int, default=3, help='Number of nodes')
@click.option('-p', '--publisher', 'publisher', type=str, help='Publisher URI', multiple=True)
def setup_nodes(count, publisher):
    if publisher:
        api_manager.online(list(publisher))
    else:
        api_manager.online(api_manager.get_base_urls(count))


@validate.command(help='Check the blockchain state of all nodes', name='chain')
@click.option('-c', '--count', 'count', type=int, default=3, help='Number of nodes')
@click.option('-p', '--publisher', 'publisher', type=str, help='Publisher URI', multiple=True)
def setup_nodes(count, publisher):
    if publisher:
        api_manager.chain(list(publisher))
    else:
        api_manager.chain(api_manager.get_base_urls(count))


@validate.command(help='Issue transactions', name='transaction')
@click.option('-f', '--folder', 'folder', type=str, help='Name of the folder', multiple=True, required=True)
@click.option('-s', '--start', 'start', type=int, help='Starting point of datasets', default=0)
@click.option('-m', '--max', 'max_datasets', type=int, help='Maximum datasets', default=100000000)
def setup_nodes(folder, start, max_datasets):
    folder = list(folder)
    api_manager.load_datasets(folder, start, max_datasets)


if __name__ == '__main__':
    cli()
    deploy()
    setup()
    validate()


