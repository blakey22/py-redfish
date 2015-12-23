import com.blakey.redfish
from . import register_command
from .command import *


# TODO: find a better way to handle oem extension instead of calling func directly

@register_command("manage", "BMC management info")
class SystemCommand(CommandBase):
    @staticmethod
    def is_associated_service(service_name):
        return service_name == "Managers"

    def detail_help(self, args=None):
        print "Dump raw data model\n\tdump"

    def init(self):
        self.url = self.service.data_model.links.Member[0].href
        print "System: " + str(self.service.data_model.Total)
        self.data_model = self.service.get_data_model(self.url)
