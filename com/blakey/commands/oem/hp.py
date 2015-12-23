import generic
from ..command import CommandBase, ExecutionResult, EXEC_SUCCESS, CMD_ACTION_HELP
from com.blakey.commands import register_command


class OEMHandler(generic.OEMHandler):
    def user_create(self, username, password, privilege):
        extra_args = {"Oem.Hp.LoginName": username}
        return extra_args

@register_command("hp", "HP Oem commands")
class HpCommand(CommandBase):
    @staticmethod
    def is_associated_service(service_name):
        return service_name == "AccountService"

    def __init__(self, service, session, oem):
        super(HpCommand, self).__init__(service, session, oem)
        self.services = {}
        self.actions = {CMD_ACTION_HELP: self.detail_help,
                        "info": self.info}

    def init(self):
        # Place holder
        pass

    def detail_help(self, args=None):
        print "info\t\tHP OEM information"

    def info(self, args=None):
        print "Hello World"
        #return ExecuteResult(EXEC_SUCCESS)

