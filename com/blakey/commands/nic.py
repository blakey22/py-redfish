from . import register_command
from .command import *
from com.blakey.exception import UnsupportedCommand

# TODO: find a better way to handle oem extension instead of calling func directly

@register_command("nic", "BMC network configuration")
class NicCommand(CommandBase):
    @staticmethod
    def is_associated_service(service_name):
        return service_name == "Managers"

    def detail_help(self, args=None):
        print "Dump raw data model\n\tdump"

    def init(self):
        #url = self.service.data_model.links.Member[0].href

        if self.service.data_model.links.Member[0].href is not None:
            url = self.service.data_model.links.Member[0].href
            data_model = self.service.get_data_model(url)
            self.url = data_model.links.EthernetNICs.href
        else:
            raise UnsupportedCommand()
        #print "System: " + str(self.service.data_model.Total)
        self.data_model = self.service.get_data_model(self.url)

    def list(self, args=None):
        #print "%-10s%-20s%-20s%s" % ("Status", "MacAddress", "IP v4 Addresses", "IP v6 Addresses")
        if self.data_model.Items is not None:
            for item in self.data_model.Items:
                #print "%-10s%-20s%-10s" % (item.Status.State, item.MacAddress, item.IPv4Addresses[0].Address)
                print "%-20s: %s" % ("Status", item.Status.State,)
                print "%-20s: %s" % ("Mac Address", item.MacAddress,)
                for addr in item.IPv4Addresses:
                    print "%-20s: %s" % ("IP Address", addr.Address,)
                    print "%-20s: %s" % ("SubnetMask", addr.SubnetMask,)
                    print "%-20s: %s" % ("AddressOrigin", addr.AddressOrigin,)
                    print "%-20s: %s" % ("Gateway", addr.Gateway,)
