from __future__ import annotations

from cloudshell.shell.core.driver_context import ResourceCommandContext
from cloudshell.shell.core.resource_driver_interface import ResourceDriverInterface


class GoogleCloudProviderShell2GDriver(ResourceDriverInterface):
    SHELL_NAME = constants.SHELL_NAME

    def __init__(self):
        """Init function."""
        pass

    def initialize(self, context):
        pass

    def Deploy(self, context, request=None, cancellation_context=None):
        pass

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
