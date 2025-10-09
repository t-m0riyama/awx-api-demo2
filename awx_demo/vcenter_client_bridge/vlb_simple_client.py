import os

from awx_demo.utils.logging import Logging
import vcenter_lookup_bridge_client
from vcenter_lookup_bridge_client import ApiClient
from vcenter_lookup_bridge_client.rest import ApiException


class VlbSimpleClient:

    @staticmethod
    @Logging.func_logger
    def generate_configuration():
        return vcenter_lookup_bridge_client.Configuration(
            host=os.environ["RMX_VLB_API_SERVER"],
            username=os.environ["RMX_VLB_API_USERNAME"],
            password=os.environ["RMX_VLB_API_PASSWORD"],
        )

    @staticmethod
    @Logging.func_logger
    def get_api_client(configuration):
        return vcenter_lookup_bridge_client.ApiClient(configuration)

    @staticmethod
    @Logging.func_logger
    def get_vcenters(api_client: ApiClient):
        with api_client:
            # APIインスタンスを生成
            api_instance = vcenter_lookup_bridge_client.VcentersApi(api_client)
            try:
                api_response = api_instance.list_vcenters()
                return api_response.results
            except ApiException as e:
                Logging.warning(f"Exception when calling VcentersApi->list_vcenters: {e}")

    @staticmethod
    @Logging.func_logger
    def get_vm_folders(api_client: vcenter_lookup_bridge_client.ApiClient):
        with api_client:
            # APIインスタンスを生成
            api_instance = vcenter_lookup_bridge_client.VmFoldersApi(api_client)
            try:
                api_response = api_instance.list_vm_folders()
                return api_response.results
            except ApiException as e:
                Logging.warning(f"Exception when calling VMsApi->list_vm_folders: {e}")

    @staticmethod
    @Logging.func_logger
    def get_vms_by_vm_folders(
        api_client: ApiClient,
        vcenter: str,
        system_ids: list[str],
    ):
        with api_client:
            # APIインスタンスを生成
            api_instance = vcenter_lookup_bridge_client.VmsApi(api_client)
            try:
                api_response = api_instance.list_vms(vcenter=vcenter, vm_folders=system_ids)
                api_response.results.sort(key=lambda x: x.name)
                return api_response.results
            except ApiException as e:
                Logging.warning(f"Exception when calling VMsApi->list_vm_folders: {e}")

    @staticmethod
    @Logging.func_logger
    def get_vm(
        api_client: ApiClient,
        vcenter: str,
        vm_instance_uuid: str,
    ):
        with api_client:
            # APIインスタンスを生成
            api_instance = vcenter_lookup_bridge_client.VmsApi(api_client)
            try:
                api_response = api_instance.get_vm(vcenter=vcenter, vm_instance_uuid=vm_instance_uuid)
                return api_response.results
            except ApiException as e:
                Logging.warning(f"Exception when calling VMsApi->get_vm: {e}")
