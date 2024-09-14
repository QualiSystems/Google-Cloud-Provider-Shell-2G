from __future__ import annotations

import json
from typing import TYPE_CHECKING

from cloudshell.cp.core.cancellation_manager import CancellationContextManager
from cloudshell.cp.core.request_actions import GetVMDetailsRequestActions, \
    PrepareSandboxInfraRequestActions, CleanupSandboxInfraRequestActions

from cloudshell.shell.core.resource_driver_interface import ResourceDriverInterface
from cloudshell.shell.core.session.cloudshell_session import CloudShellSessionContext
from cloudshell.shell.core.session.logging_session import LoggingSessionContext

from cloudshell.shell.core.driver_context import AutoLoadDetails
from cloudshell.cp.gcp.flows.cleanup_infra_flow import CleanUpGCPInfraFlow
from cloudshell.cp.gcp.flows.deploy_instance import get_deploy_params
from cloudshell.cp.gcp.flows.power_flow import GCPPowerFlow
from cloudshell.cp.gcp.flows.prepare_infra_flow import PrepareGCPInfraFlow
from cloudshell.cp.gcp.flows.refresh_ip_flow import GCPRefreshIPFlow
from cloudshell.cp.gcp.flows.vm_details_flow import GCPGetVMDetailsFlow
from cloudshell.cp.gcp.handlers.instance import InstanceHandler
from cloudshell.cp.gcp.helpers import constants
from cloudshell.cp.gcp.models.deploy_app import GCPDeployVMRequestActions, \
    InstanceFromMachineImageDeployApp, InstanceFromTemplateDeployApp, \
    InstanceFromScratchDeployApp
from cloudshell.cp.gcp.models.deployed_app import (GCPDeployedVMRequestActions,
                                                   InstanceFromScratchDeployedApp,
                                                   InstanceFromTemplateDeployedApp,
                                                   InstanceFromMachineImageDeployedApp,
                                                   GCPGetVMDetailsRequestActions)
from cloudshell.cp.gcp.resource_conf import GCPResourceConfig

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
        for deploy_app_cls in (
                InstanceFromScratchDeployApp,
                InstanceFromTemplateDeployApp,
                InstanceFromMachineImageDeployApp,
        ):
            GCPDeployVMRequestActions.register_deployment_path(deploy_app_cls)

        for deployed_app_cls in (
                InstanceFromScratchDeployedApp,
                InstanceFromTemplateDeployedApp,
                InstanceFromMachineImageDeployedApp,
        ):
            GCPDeployedVMRequestActions.register_deployment_path(deployed_app_cls)

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
            resource_config = GCPResourceConfig.from_context(
                context,
                api=cs_api
            )

            cancellation_manager = CancellationContextManager(cancellation_context)

            request_actions = GCPDeployVMRequestActions.from_request(
                request,
                cs_api
            )
            deploy_flow_class = get_deploy_params(request_actions)

            deploy_flow = deploy_flow_class(
                resource_config=resource_config,
                cancellation_manager=cancellation_manager,
            )
            return deploy_flow.deploy(request_actions=request_actions)

    def PowerOn(self, context, ports):
        """Called during sandbox's teardown.

        Can also be run manually by the sandbox end-user from the deployed
        App's commands pane. Method shuts down (or powers off) the VM instance.
        If the operation fails, method should raise an exception.
        """
        with LoggingSessionContext(context) as logger:
            logger.info("Starting Power Off command")
            api = CloudShellSessionContext(context).get_api()
            resource_config = GCPResourceConfig.from_context(
                context,
                api=api
            )
            resource = context.remote_endpoints[0]
            actions = GCPDeployedVMRequestActions.from_remote_resource(
                resource,
                api
            )
            GCPPowerFlow(
                actions.deployed_app,
                resource_config
            ).power_on()

    def PowerOff(self, context, ports):
        """Called during sandbox's teardown.

        Can also be run manually by the sandbox end-user from the deployed
        App's commands pane. Method shuts down (or powers off) the VM instance.
        If the operation fails, method should raise an exception.
        """
        with LoggingSessionContext(context) as logger:
            logger.info("Starting Power Off command")
            api = CloudShellSessionContext(context).get_api()
            resource_config = GCPResourceConfig.from_context(
                context,
                api=api
            )
            resource = context.remote_endpoints[0]
            actions = GCPDeployedVMRequestActions.from_remote_resource(
                resource,
                api
            )
            GCPPowerFlow(
                actions.deployed_app,
                resource_config
            ).power_off()

    def orchestration_power_on(self, context, ports):
        pass

    def orchestration_power_off(self, context, ports):
        pass

    def PowerCycle(self, context, ports, delay):
        pass

    def remote_refresh_ip(self, context, ports, cancellation_context):
        """Called when reserving a sandbox during setup.

        Call for each app in the sandbox can also be run manually by the sandbox
        end-user from the deployed App's commands pane. Method retrieves the VM's
        updated IP address from the cloud provider and sets it on the deployed App
        resource. Both private and public IPs are retrieved, as appropriate. If the
        operation fails, method should raise an exception.
        """
        with LoggingSessionContext(context) as logger:
            logger.info("Starting Remote Refresh IP command")
            api = CloudShellSessionContext(context).get_api()
            resource_config = GCPResourceConfig.from_context(
                context,
                api=api
            )
            resource = context.remote_endpoints[0]
            cancellation_manager = CancellationContextManager(
                cancellation_context
            )
            actions = GCPDeployedVMRequestActions.from_remote_resource(
                resource,
                api
            )
            GCPRefreshIPFlow(
                actions.deployed_app,
                resource_config,
                cancellation_manager
            ).refresh_ip()

    def DeleteInstance(self, context, ports):
        """Called during sandbox's teardown.

        """
        with LoggingSessionContext(context) as logger:
            logger.info("Starting Remote Refresh IP command")
            api = CloudShellSessionContext(context).get_api()
            resource_config = GCPResourceConfig.from_context(
                context,
                api=api
            )
            resource = context.remote_endpoints[0]
            actions = GCPDeployedVMRequestActions.from_remote_resource(
                resource,
                api
            )
            instance_data = json.loads(actions.deployed_app.vmdetails.uid)
            instance_data["credentials"] = resource_config.credentials
            InstanceHandler.get(**instance_data).delete()

    def PrepareSandboxInfra(self, context, request, cancellation_context):
        """

        :param ResourceCommandContext context:
        :param str request:
        :param CancellationContext cancellation_context:
        :return:
        :rtype: str
        """
        with LoggingSessionContext(context) as logger:
            logger.info("Starting Prepare Sandbox Infra command...")
            logger.debug(f"Request: {request}")
            api = CloudShellSessionContext(context).get_api()
            resource_config = GCPResourceConfig.from_context(
                context=context,
                api=api
            )

            request_actions = PrepareSandboxInfraRequestActions.from_request(
                request
            )
            cancellation_manager = CancellationContextManager(
                cancellation_context
            )

            prepare_sandbox_flow = PrepareGCPInfraFlow(
                logger=logger,
                config=resource_config,
            )

            return prepare_sandbox_flow.prepare(
                request_actions=request_actions
            )

    def CleanupSandboxInfra(self, context, request):
        """

        :param ResourceCommandContext context:
        :param str request:
        :return:
        :rtype: str
        """
        with LoggingSessionContext(context) as logger:
            logger.info("Starting Cleanup Sandbox Infra command...")
            api = CloudShellSessionContext(context).get_api()
            resource_config = GCPResourceConfig.from_context(
                context=context,
                api=api
            )

            request_actions = CleanupSandboxInfraRequestActions.from_request(
                request
            )

            cleanup_flow = CleanUpGCPInfraFlow(
                config=resource_config,
                logger=logger,
            )

            return cleanup_flow.cleanup(
                request_actions=request_actions
            )

    def get_inventory(self, context):
        return AutoLoadDetails([], [])

    def GetAccessKey(self, context, ports):
        pass

    def SetAppSecurityGroups(self, context, request):
        pass

    def GetVmDetails(self, context, requests, cancellation_context):
        """

        :param ResourceCommandContext context:
        :param str requests:
        :param CancellationContext cancellation_context:
        :return:
        """
        with LoggingSessionContext(context) as logger:
            logger.info("Starting Get VM Details command...")
            logger.debug(f"Requests: {requests}")
            api = CloudShellSessionContext(context).get_api()
            resource_config = GCPResourceConfig.from_context(
                context=context,
                api=api
            )

            for deployed_app_cls in (
                    InstanceFromScratchDeployedApp,
                    InstanceFromTemplateDeployedApp,
                    InstanceFromMachineImageDeployedApp,
            ):
                GCPGetVMDetailsRequestActions.register_deployment_path(
                    deployed_app_cls
                )

            request_actions = GCPGetVMDetailsRequestActions.from_request(
                request=requests,
                cs_api=api
            )

            # cancellation_manager = CancellationContextManager(cancellation_context)

            vm_details_flow = GCPGetVMDetailsFlow(
                logger=logger,
                config=resource_config,
            )

            return vm_details_flow.get_vm_details(
                request_actions=request_actions
            )

    def cleanup(self):
        pass
