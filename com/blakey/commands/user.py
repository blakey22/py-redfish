import com.blakey.redfish
from . import register_command
from .command import *

# TODO: find a better way to handle oem extension instead of calling func directly

@register_command("user", "Configure BMC users")
class UserCommand(CommandBase):
    @staticmethod
    def is_associated_service(service_name):
        return service_name == "AccountService"

    def detail_help(self, args=None):
        print "List current BMC users\n\tlist"
        print "Create new BMC user\n\tcreate [username] [password] [privilege]"
        print "Update current BMC user setting\n\tupdate [id]"
        print "Delete BMC user\n\tdelete [id]"
        print "Dump raw data model\n\tdump"

    def init(self):
        self.url = self.service.data_model.links.Accounts.href
        self.data_model = self.service.get_data_model(self.url)

    def list(self, args=None):
        # TODO: add modified control

        print "%-10s%-30s%s" % ("ID", "UserName", "Oem")
        if self.data_model.Items is not None:
            for item in self.data_model.Items:
                print "%-10s%-30s" % (item.links.self.href.replace(self.url + "/", ""), item.UserName)
                oems = com.blakey.redfish.oem_to_list(item)
                for o in oems:
                    print "%-10s%-30s%s" % ("", "", o)
        return ExecutionResult(EXEC_SUCCESS)

    def create(self, args):
        #if not self.data_model.create:
        #    return ExecuteResult(EXEC_FORBIDDEN_OPERATION)

        # validate argument
        self.validate_args_number(args, 3)

        username = args[0]
        password = args[1]
        privilege = args[2]
        post_args = {"UserName": username, "Password": password}

        # update extra arguments from user
        if len(args) > 3:
            extra_args = self.args2dict(args[3:])
            post_args.update(extra_args)

        # call oem extension
        post_args.update(self.oem.user_create(username, password, privilege))
        post_data = self.dict2json_str(post_args)
        resp = self.session.create(self.url, post_data)
        return ExecutionResult.parse(resp)

    def update(self, args):
        #if not self.data_model.update:
        #    return ExecuteResult(EXEC_FORBIDDEN_OPERATION)
        id = args[0]
        args = args[1:]
        post_data = self.dict2json_str(args)
        url = self.get_member(id)
        resp = self.session.update(url, post_data)
        #self.init()
        return ExecutionResult.parse(resp)

    def delete(self, args):
        #if not self.data_model.delete:
        #    return ExecuteResult(EXEC_FORBIDDEN_OPERATION)
        id = args[0]
        url = self.get_member(id)
        resp = self.session.delete(url)
        #self.init()
        return ExecutionResult.parse(resp)

    def oem(self, args=None):
        pass


