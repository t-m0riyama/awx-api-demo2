import os

from urllib3.exceptions import HTTPError
from urllib3.exceptions import RequestError

from awx_demo.utils.logging import Logging
import vcenter_lookup_bridge_client
from vcenter_lookup_bridge_client import ApiClient
from vcenter_lookup_bridge_client.exceptions import NotFoundException


class VlbSimpleClientError(Exception):
    """Raised when VLB Simple Client fails."""


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
            except Exception as e:
                VlbSimpleClient._handle_exception(e, "VcentersApi->list_vcenters")

    @staticmethod
    @Logging.func_logger
    def get_vm_folders(api_client: vcenter_lookup_bridge_client.ApiClient):
        with api_client:
            # APIインスタンスを生成
            api_instance = vcenter_lookup_bridge_client.VmFoldersApi(api_client)
            try:
                api_response = api_instance.list_vm_folders()
                return api_response.results
            except Exception as e:
                VlbSimpleClient._handle_exception(e, "VmFoldersApi->list_vm_folders")

    @staticmethod
    @Logging.func_logger
    def get_vms_by_vm_folders(
        api_client: ApiClient,
        system_ids: list[str],
        vcenter: str = None,
    ):
        with api_client:
            # APIインスタンスを生成
            api_instance = vcenter_lookup_bridge_client.VmsApi(api_client)
            try:
                if vcenter is not None:
                    api_response = api_instance.list_vms(vcenter=vcenter, vm_folders=system_ids)
                else:
                    api_response = api_instance.list_vms(vm_folders=system_ids)
                api_response.results.sort(key=lambda x: x.name)
                return api_response.results
            except Exception as e:
                VlbSimpleClient._handle_exception(e, "VmsApi->list_vms")

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
            except Exception as e:
                VlbSimpleClient._handle_exception(e, "VmsApi->get_vm")

    @staticmethod
    @Logging.func_logger
    def get_vm_instance_uuid_by_vm_name(
        api_client: ApiClient,
        vcenter: str,
        system_ids: list[str],
        vm_name: str,
    ):
        with api_client:
            results = VlbSimpleClient.get_vms_by_vm_folders(
                api_client=api_client, vcenter=vcenter, system_ids=system_ids
            )
            for result in results:
                if result.name == vm_name:
                    return result.instance_uuid
            return None

    @staticmethod
    @Logging.func_logger
    def get_vm_snapshots(
        api_client: ApiClient,
        vcenter: str,
        vm_instance_uuid: str,
    ):
        with api_client:
            # APIインスタンスを生成
            api_instance = vcenter_lookup_bridge_client.VmSnapshotsApi(api_client)
            try:
                api_response = api_instance.get_vm_snapshots(vcenter=vcenter, vm_instance_uuid=vm_instance_uuid)
                return api_response.results
            except Exception as e:
                VlbSimpleClient._handle_exception(e, "VmSnapshotsApi->get_vm_snapshots")

    @staticmethod
    @Logging.func_logger
    def list_vm_snapshots(
        api_client: ApiClient,
        vcenter: str,
    ):
        with api_client:
            # APIインスタンスを生成
            api_instance = vcenter_lookup_bridge_client.VmSnapshotsApi(api_client)
            try:
                api_response = api_instance.list_vm_snapshots(vcenter=vcenter)
                return api_response.results
            except Exception as e:
                VlbSimpleClient._handle_exception(e, "VmSnapshotsApi->list_vm_snapshots")

    @staticmethod
    @Logging.func_logger
    def _handle_exception(
        e: Exception,
        api_name: str,
    ):
        if isinstance(e, RequestError):
            Logging.error(f"RequestErrorが発生しました: {e}")
            raise VlbSimpleClientError(f"RequestError when calling {api_name}: {e}")
        elif isinstance(e, HTTPError):
            Logging.error(f"HTTPErrorが発生しました: {e}")
            raise VlbSimpleClientError(f"HTTPError when calling {api_name}: {e}")
        elif isinstance(e, NotFoundException):
            Logging.warning(f"該当するvCenterオブジェクトが見つかりませんでした: {e}")
            pass
        else:
            Logging.error(f"不明な例外が発生しました: {e}")
            raise VlbSimpleClientError(f"Exception when calling {api_name}: {e}")
