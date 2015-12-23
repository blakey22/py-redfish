import com.blakey.redfish
from . import register_command
from .command import *

@register_command("system", "BMC system info")
class SystemCommand(CommandBase):

    @staticmethod
    def is_associated_service(service_name):
        return service_name == "Systems"

    def detail_help(self, args=None):
        print "Dump raw data model\n\tdump"

    def init(self):
        self.url = self.service.data_model.links.Member[0].href
        #print "System: " + str(self.service.data_model.Total)
        self.data_model = self.service.get_data_model(self.url)
