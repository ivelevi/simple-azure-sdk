import logging
import os
from azure.identity import DefaultAzureCredential
from azure.mgmt.resource import ResourceManagementClient
from azure.mgmt.compute import ComputeManagementClient
from azure.mgmt.compute.models import VirtualMachine
from azure.mgmt.sql import SqlManagementClient
from azure.mgmt.sql.models import Server, Database
from azure.mgmt.storage import StorageManagementClient
from azure.mgmt.storage.models import StorageAccountCreateParameters

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Set up credentials and clients
subscription_id = ""
resource_group = ""
location = ""
vm_name = ""
sql_server_name = ""
sql_database_name = ""
storage_account_name = ""

credential = DefaultAzureCredential()

resource_client = ResourceManagementClient(credential, subscription_id)
compute_client = ComputeManagementClient(credential, subscription_id)
sql_client = SqlManagementClient(credential, subscription_id)
storage_client = StorageManagementClient(credential, subscription_id)

# Create Resource Group
def create_resource_group():
    try:
        resource_client.resource_groups.create_or_update(
            resource_group,
            {"location": location}
        )
        logger.info(f"Resource group '{resource_group}' created successfully.")
    except Exception as e:
        logger.error(f"Error creating resource group: {e}")

# Deploy Virtual Machine
def create_virtual_machine():
    try:
        vm_parameters = {
            "location": location,
            "hardware_profile": {"vm_size": "Standard_DS1_v2"},
            "storage_profile": {
                "image_reference": {
                    "publisher": "MicrosoftWindowsServer",
                    "offer": "WindowsServer",
                    "sku": "2016-Datacenter",
                    "version": "latest"
                }
            },
            "os_profile": {
                "computer_name": vm_name,
                "admin_username": "azureuser",
                "admin_password": "Password1234!"
            },
            "network_profile": {
                "network_interfaces": [{"id": "/subscriptions/{subscription_id}/resourceGroups/{resource_group}/providers/Microsoft.Network/networkInterfaces/example-nic"}]
            }
        }

        async_vm_creation = compute_client.virtual_machines.begin_create_or_update(
            resource_group,
            vm_name,
            vm_parameters
        )
        async_vm_creation.result()
        logger.info(f"VM '{vm_name}' created successfully.")
    except Exception as e:
        logger.error(f"Error creating VM: {e}")

# Set up Azure SQL Database
def create_sql_database():
    try:
        server_params = Server(
            location=location,
            administrator_login="sqladmin",
            administrator_login_password="Password1234!"
        )

        sql_client.servers.begin_create_or_update(
            resource_group,
            sql_server_name,
            server_params
        ).result()

        database_params = Database(location=location)

        sql_client.databases.begin_create_or_update(
            resource_group,
            sql_server_name,
            sql_database_name,
            database_params
        ).result()

        logger.info(f"SQL Database '{sql_database_name}' created successfully.")
    except Exception as e:
        logger.error(f"Error creating SQL Database: {e}")

# Configure Storage Account
def create_storage_account():
    try:
        storage_params = StorageAccountCreateParameters(
            sku={"name": "Standard_LRS"},
            kind="StorageV2",
            location=location
        )

        storage_client.storage_accounts.begin_create(
            resource_group,
            storage_account_name,
            storage_params
        ).result()

        logger.info(f"Storage account '{storage_account_name}' created successfully.")
    except Exception as e:
        logger.error(f"Error creating Storage Account: {e}")

# Functions to start, stop, and delete VM
def start_vm():
    try:
        async_vm_start = compute_client.virtual_machines.begin_start(resource_group, vm_name)
        async_vm_start.result()
        logger.info(f"VM '{vm_name}' started successfully.")
    except Exception as e:
        logger.error(f"Error starting VM: {e}")

def stop_vm():
    try:
        async_vm_stop = compute_client.virtual_machines.begin_power_off(resource_group, vm_name)
        async_vm_stop.result()
        logger.info(f"VM '{vm_name}' stopped successfully.")
    except Exception as e:
        logger.error(f"Error stopping VM: {e}")

def delete_vm():
    try:
        async_vm_delete = compute_client.virtual_machines.begin_delete(resource_group, vm_name)
        async_vm_delete.result()
        logger.info(f"VM '{vm_name}' deleted successfully.")
    except Exception as e:
        logger.error(f"Error deleting VM: {e}")

# Main script execution
# Call only the functions referent to the resources you want to create
if __name__ == "__main__":
    create_resource_group()
    create_virtual_machine()
    create_sql_database()
    create_storage_account()

    # Example usage of VM control functions
    start_vm()
    stop_vm()
    delete_vm()
    print('end')
