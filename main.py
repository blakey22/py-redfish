from optparse import OptionParser, OptionGroup, SUPPRESS_HELP
from com.blakey.redfish.session import RedfishSession
from com.blakey.redfish.service import Service
from com.blakey.commands import get_activated_commands, \
    ExecutionResult, EXEC_SUCCESS, EXEC_INSUFFICIENT_ARGUMENT, EXEC_UNKNOWN_COMMAND_ACTION, EXEC_INVALID_CREDENTIAL, \
    EXEC_INVALID_ARGUMENT, EXEC_UNKNOWN_COMMAND, EXEC_GENERAL_ERROR, EXEC_HOST_NOT_REACHABLE
from com.blakey.exception import *
import sys


def build_version_info():
    return "Redfish Utility v%s\n" % ("0.1",)

def build_opt():
    parser = OptionParser(version=build_version_info())
    parser.add_option("-H", "--host", dest="host", default=None,
                        help="IP address of Redfish Interface")
    parser.add_option("-U", "--username", dest="username", default=None,
                        help="Username of BMC")
    parser.add_option("-P", "--password", dest="password", default=None,
                        help="Password of BMC")
    return parser


def print_help(parser):
    parser.print_help()
    from com.blakey.commands import get_available_commands
    cmds = get_available_commands()
    print "Commands:"
    for k, v in cmds.iteritems():
        v.brief_help()

if __name__ == '__main__':
    parser = build_opt()

    # TODO: remote test arguments
    #test_args = ["user", "create", "test", "password", "Oem.Hp.LoginName=test"]
    #test_args = ["user"]
    #test_args = ["user", "create", "test", "password", "administrator"]
    #test_args = ["user", "delete", "8"]
    #test_args = ["user", "list"]
    #test_args = ["raw", "list", "/rest/v1"]
    #test_args = ["nic", "list"]
    (options, args) = parser.parse_args()

    if len(args) == 0:
        print_help(parser)
        sys.exit(EXEC_UNKNOWN_COMMAND)
    elif (options.host is None) or (options.username is None) or (options.password is None):
        print_help(parser)
        sys.exit(EXEC_INSUFFICIENT_ARGUMENT)

    try:
        #session = RedfishSession("10.99.87.126", "admin", "password", False)
        session = None
        session = RedfishSession(options.host, options.username, options.password, False)
        session.login()
        services = Service.create(session, session.get_services_list())

        # Get available commands
        activated_cmds = get_activated_commands(services, session)

        command = args[0]
        if command not in activated_cmds:
            raise CommandNotFoundError()
        cmd = activated_cmds[command]
        result = cmd.process(args[1:])

    except InvalidCredentialError, e:
        result = ExecutionResult(EXEC_INVALID_CREDENTIAL)
    except CommandNotFoundError, e:
        result = ExecutionResult(EXEC_UNKNOWN_COMMAND)
    except InsufficientArgumentError, e:
        result = ExecutionResult(EXEC_INSUFFICIENT_ARGUMENT)
    except UnknownCommandActionError, e:
        result = ExecutionResult(EXEC_UNKNOWN_COMMAND_ACTION)
    except InvalidArgumentError, e:
        result = ExecutionResult(EXEC_INVALID_ARGUMENT)
    except HostIsNotReachableError, e:
        result = ExecutionResult(EXEC_HOST_NOT_REACHABLE)
    except Exception, e:
        import traceback
        print(traceback.format_exc())
        result = ExecutionResult(EXEC_GENERAL_ERROR, str(e))
    finally:
        if session is not None:
            session.logout()

    if result is None:
        print "Houston, We Have a Problem. => Developer should return ExecutionResult!"
        sys.exit(1)

    if result.status != EXEC_SUCCESS:
        print "Error) " + result.message
    else:
        print "Executed Successfully"

    sys.exit(result.status)

