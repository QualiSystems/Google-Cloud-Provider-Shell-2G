from __future__ import annotations

from typing import TYPE_CHECKING

from cloudshell.cp.core.cancellation_manager import CancellationContextManager

from cloudshell.cp.core.reservation_info import ReservationInfo
from cloudshell.shell.core.resource_driver_interface import ResourceDriverInterface
from cloudshell.shell.core.session.cloudshell_session import CloudShellSessionContext
from cloudshell.shell.core.session.logging_session import LoggingSessionContext

from cloudshell.cp.proxmox.flows import (
    ProxmoxDeleteFlow as DeleteFlow,
    ProxmoxSnapshotFlow as SnapshotFlow,
    ProxmoxAutoloadFlow,
    ProxmoxPowerFlow,
    ProxmoxGetVMDetailsFlow,
)
from cloudshell.cp.gcp.flows.deploy_flow import get_deploy_params
from cloudshell.cp.proxmox.flows.refresh_ip import refresh_ip

from cloudshell.cp.proxmox.handlers.proxmox_handler import ProxmoxHandler

from cloudshell.cp.proxmox.models.deploy_app import (
    ProxmoxDeployVMRequestActions,
    InstanceFromTemplateDeployApp,
    InstanceFromVMDeployApp,
)
from cloudshell.cp.proxmox.models.deployed_app import (
    ProxmoxDeployedVMActions,
    ProxmoxGetVMDetailsRequestActions,
    InstanceFromTemplateDeployedApp,
    InstanceFromVMDeployedApp,
)
from cloudshell.cp.proxmox.resource_config import ProxmoxResourceConfig

from cloudshell.cp.gcp.helpers import constants

if TYPE_CHECKING:
    from cloudshell.shell.core.driver_context import (
        AutoLoadCommandContext,
        AutoLoadDetails,
        CancellationContext,
        InitCommandContext,
        ResourceCommandContext,
        ResourceRemoteCommandContext,
    )

"""
        # self.instance_handler = InstanceHandler(
        #     credentials=self.credentials,
        #     zone=self.zone,
        #     region=self.region
        # )

"""


class GoogleCloudProviderShell2GDriver(ResourceDriverInterface):
    SHELL_NAME = constants.SHELL_NAME

    def __init__(self):
        """Init function."""
        pass

    def initialize(self, context):
        pass

    def Deploy(self, context, request=None, cancellation_context=None):
        """Called when reserving a sandbox during setup.

        Method creates the compute resource in the cloud provider - VM instance or
        container. If App deployment fails, return a "success false" action result.
        """
        with LoggingSessionContext(context) as logger:
            logger.info("Starting Deploy command")
            logger.debug(f"Request: {request}")
            cs_api = CloudShellSessionContext(context).get_api()
            resource_config = ProxmoxResourceConfig.from_context(context, api=cs_api)

            cancellation_manager = CancellationContextManager(cancellation_context)
            reservation_info = ReservationInfo.from_resource_context(context)

            request_actions = ProxmoxDeployVMRequestActions.from_request(
                request,
                cs_api
            )
            deploy_flow_class, deploy_instance_type = get_deploy_params(request_actions)
            api = ProxmoxHandler.from_config(resource_config)

            # with ProxmoxHandler.from_config(resource_config) as api:
            deploy_flow = deploy_flow_class(
                api=api,
                resource_config=resource_config,
                reservation_info=reservation_info,
                cs_api=cs_api,
                cancellation_manager=cancellation_manager,
            )
            return deploy_flow.deploy(request_actions=request_actions)

    def PowerOn(self, context, ports):
        pass

    def PowerOff(self, context, ports):
        pass

    def orchestration_power_on(self, context, ports):
        pass

    def orchestration_power_off(self, context, ports):
        pass

    def PowerCycle(self, context, ports, delay):
        pass

    def remote_refresh_ip(self, context, ports, cancellation_context):
        pass

    def DeleteInstance(self, context, ports):
        pass

    def PrepareSandboxInfra(self, context, request, cancellation_context):
        pass

    def CleanupSandboxInfra(self, context, request):
        pass

    def get_inventory(self, context):
        pass

    def GetAccessKey(self, context, ports):
        pass

    def SetAppSecurityGroups(self, context, request):
        pass

    def GetVmDetails(self, context, cancellation_context, requests):
        pass

    def AddCustomTags(self, context, request, ports):
        pass

    def cleanup(self):
        pass
