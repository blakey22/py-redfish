import json
from com.blakey.redfish.helper import is_bool, str2bool, dump_data_model
from com.blakey.exception import UnknownCommandActionError, NoMemberFoundError, InsufficientArgumentError, \
    InvalidArgumentError, HostIsNotReachableError

# return code
EXEC_SUCCESS = 0x0
EXEC_INVALID_CREDENTIAL = 0x1
EXEC_UNKNOWN_COMMAND = 0x2
EXEC_UNKNOWN_COMMAND_ACTION = 0x3
EXEC_INVALID_RESOURCE_ID = 0x4
EXEC_INVALID_REQUEST = 0x5
EXEC_INSUFFICIENT_ARGUMENT = 0x6
EXEC_SERVER_ERROR = 0x7
EXEC_FORBIDDEN_OPERATION = 0x8
EXEC_INVALID_ARGUMENT = 0x9
EXEC_HOST_NOT_REACHABLE = 0xA
EXEC_GENERAL_ERROR = 0xFF

exec_msg_map = {
    EXEC_SUCCESS: "Success",
    EXEC_INVALID_CREDENTIAL: "Invalid Credential",
    EXEC_UNKNOWN_COMMAND: "Unknown Command",
    EXEC_UNKNOWN_COMMAND_ACTION: "Unknown Command Action",
    EXEC_INVALID_RESOURCE_ID: "Invalid Resource ID",
    EXEC_INVALID_REQUEST: "Invalid Request",
    EXEC_INSUFFICIENT_ARGUMENT: "Insufficient argument(s)",
    EXEC_SERVER_ERROR: "Server Encountered Error",
    EXEC_FORBIDDEN_OPERATION: "Forbidden Operation",
    EXEC_INVALID_ARGUMENT: "Invalid Argument",
    EXEC_HOST_NOT_REACHABLE: "Host is not reachable",
    EXEC_GENERAL_ERROR: "General error"
}

CMD_ACTION_DUMP = "dump"
CMD_ACTION_HELP = "help"
CMD_ACTION_LIST = "list"
CMD_ACTION_CREATE = "create"
CMD_ACTION_UPDATE = "update"
CMD_ACTION_DELETE = "delete"


class ExecutionResult(object):
    @classmethod
    def parse(cls, http_response):
        json_obj = json.loads(http_response.body)
        if not http_response.is_successful():
            if http_response.status in range(500, 599):
                status = EXEC_SERVER_ERROR
            elif http_response.status in range(400, 499):
                status = EXEC_INVALID_REQUEST
            else:
                status = EXEC_GENERAL_ERROR
        else:
            status = EXEC_SUCCESS
        message = ""
        for i in json_obj["Messages"]:
            if isinstance(i, dict):
                for k, v in i.iteritems():
                    message += "%s: %s, " % (k, v)
            else:
                message += str(i) + ", "

        return ExecutionResult(status, message[0:-2])

    @classmethod
    def status2message(cls, status):
        if status in exec_msg_map:
            return exec_msg_map[status]
        return "%s (%d)" % (exec_msg_map[EXEC_GENERAL_ERROR], status)

    def __init__(self, status=EXEC_SUCCESS, message=""):
        self.status = status
        if len(message) == 0:
            self.message = self.status2message(status)
        else:
            self.message = message


class CommandBase(object):
    CMD_NAME = ""
    CMD_DESCRIPTION = ""

    @staticmethod
    def is_associated_service(service_name):
        raise NotImplementedError()

    @classmethod
    def brief_help(cls):
        print "    %-20s%-50s" % (cls.CMD_NAME, cls.CMD_DESCRIPTION)

    def __init__(self, session, service, oem_extension=None):
        self.session = session
        self.service = service
        self.oem = oem_extension
        self.data_model = None
        self.url = ""
        self.actions = {CMD_ACTION_DUMP: self.dump,
                        CMD_ACTION_HELP: self.detail_help,
                        CMD_ACTION_LIST: self.list,
                        CMD_ACTION_CREATE: self.create,
                        CMD_ACTION_UPDATE: self.update,
                        CMD_ACTION_DELETE: self.delete}

    def init(self):
        raise NotImplementedError()

    def dump(self, args=None):
        if self.data_model:
            print self.url
            dump_data_model(self.data_model)
        else:
            print "Unable to dump data model for: " + self.url

    def detail_help(self, args=None):
        raise NotImplementedError()

    def list(self, args=None):
        raise NotImplementedError()

    def create(self, args):
        raise NotImplementedError()

    def update(self, args):
        raise NotImplementedError()

    def delete(self, args):
        raise NotImplementedError()

    def oem(self, args=None):
        raise NotImplementedError()

    def process(self, args):
        if len(args) == 0 or (args[0] not in self.actions):
            if CMD_ACTION_HELP in self.actions:
                self.actions[CMD_ACTION_HELP](args)
            else:
                print "Developer Error! missing 'help' func"
            raise UnknownCommandActionError()
        name = args[0]
        if name in self.actions:
            if name != CMD_ACTION_HELP:
                self.init()
            try:
                return self.actions[name](args[1:])
            except NoMemberFoundError, e:
                return ExecutionResult(EXEC_INVALID_RESOURCE_ID)

    @classmethod
    def args2dict(cls, args):
        data = {}
        for i in args:
            item = i.split("=")
            try:
                data[item[0]] = item[1]
            except:
                raise InvalidArgumentError()
        return data

    @classmethod
    def dict2json_str(cls, args):
        dict_obj = {}
        for key, value in args.iteritems():
            current = dict_obj
            if "." in key:
                levels = key.split(".")
                for i, name in enumerate(levels):
                    if name.isdigit():
                        raise NotImplementedError()
                    elif i == len(levels) - 1:
                        v = value
                        if is_bool(value):
                            v = str2bool(value)
                        current[name] = v
                    else:
                        current[name] = {}
                        current = current[name]
            else:
                dict_obj[key] = value
        json_str = json.dumps(dict_obj)
        return json_str

    @classmethod
    def args2json_str(cls, args):
        dict_args = cls.args2dict(args)
        return cls.dict2json_str(dict_args)

    @classmethod
    def validate_args_number(cls, args, excepted_num):
        if len(args) < excepted_num:
            raise InsufficientArgumentError()

    def parse_args2(self, args):
        data = args.split(";")
        dict_obj = {}
        for d in data:
            item = d.split("=")
            current = dict_obj
            if "." in item[0]:
                levels = item[0].split(".")
                for i, name in enumerate(levels):
                    if name.isdigit():
                        raise NotImplementedError()
                    elif i == len(levels) - 1:
                        v = item[1]
                        if is_bool(item[1]):
                            v = str2bool(item[1])
                        current[name] = v
                    else:
                        current[name] = {}
                        current = current[name]
            else:
                dict_obj[item[0]] = item[1]
        json_str = json.dumps(dict_obj)
        return json_str

    def get_member(self, id):
        if self.data_model is None:
            raise NoMemberFoundError()

        for member in self.data_model.links.Member:
            url = self.url + "/" + str(id)
            if url == member.href:
                return url

        raise NoMemberFoundError()
