from command import *
from com.blakey.redfish.service import Service

registered_commands = {}

def register_command(name, desc):
    def register_command_decorator(cls):
        cls.CMD_NAME = name
        cls.CMD_DESCRIPTION = desc
        registered_commands[name] = cls
        return cls
    return register_command_decorator

def get_available_commands():
    return registered_commands

def get_activated_commands(services, session):
    cmds = {}
    service_cmd = ServiceCommand(session, None)
    #raw_cmd = RawCommand(session)

    # load oem extension
    oem = get_oem_handler(session.get_vendor(), 0)

    # get command
    for key, value in services.iteritems():
        service_cmd.add(key, value)
        for c_key, c_cls in registered_commands.iteritems():
            if c_cls.is_associated_service(key):
                # TODO: use gevent?
                cmds[c_key] = c_cls(session, value, oem)

    # bulit-in commands
    cmds[service_cmd.CMD_NAME] = service_cmd
    #cmds[raw_cmd.CMD_NAME] = raw_cmd

    return cmds


@register_command("service", "Print raw data model for all root services")
class ServiceCommand(CommandBase):

    @staticmethod
    def is_associated_service(service_name):
        return False

    def __init__(self, session, service, oem=None):
        super(ServiceCommand, self).__init__(session, service, oem)
        self.services = {}
        self.actions = {CMD_ACTION_DUMP: self.dump,
                        CMD_ACTION_HELP: self.detail_help}

    def init(self):
        # Place holder
        pass

    def add(self, name, service):
        self.services[name] = service

    def dump(self, args=None):
        # Override dump
        for name, service in self.services.iteritems():
            print "\n== Data Model Dump =="
            print name
            service.dump()
        return ExecutionResult(EXEC_SUCCESS)

    def detail_help(self, args=None):
        print "dump\t\tDump raw data model for all services"

@register_command("raw", "Perform raw operation")
class RawCommand(CommandBase):
    @staticmethod
    def is_associated_service(service_name):
        return True

    def init(self):
        # keep original dump method
        self._dump = self.dump
        # re-route "dump" method to "list"
        self.dump = self.list
        pass

    def detail_help(self, args=None):
        print "List data model of specified resource\n\tlist [url]"
        print "Create new resource\n\tcreate [url] [attribute_1] [attribute_2] ... [attribute_n]"
        print "Update specified resource\n\tupdate [url] [attribute_1] [attribute_2] ... [attribute_n]"
        print "Delete specified resource\n\tdelete [url]"
        print "Dump data model of specified resource\n\tdump [url]"

    def update(self, args):
        self.validate_args_number(args, 2)
        url = args[0]
        post_data = self.args2json_str(args[1:])
        self.session.create(url, post_data)

    def list(self, args=None):
        self.validate_args_number(args, 1)
        self.url = args[0]
        self.service = Service("User Defined URL", self.url, self.session)
        self.data_model = self.service.data_model
        self._dump()

    def create(self, args):
        self.validate_args_number(args, 2)
        url = args[0]
        post_data = self.args2json_str(args[1:])
        self.session.create(url, post_data)

    def delete(self, args):
        self.validate_args_number(args, 2)
        url = args[0]
        self.session.delete(url)


# import all command classes
from oem import get_oem_handler
import user
import system
import manage
import nic