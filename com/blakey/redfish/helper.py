from model import DataModel


def dump_json_obj(json_obj, ident="  "):
    if isinstance(json_obj, list):
        for item in json_obj:
            if isinstance(item, basestring):
                print ident + item
            elif isinstance(item, (int, long, float, complex)):
                print ident + str(item)
            elif isinstance(item, dict):
                dump_json_obj(item, ident + "  ")
            else:
                print "Unknown type: " + str(item)
    elif isinstance(json_obj, dict):
        for key, value in json_obj.iteritems():
            if isinstance(value, dict) or isinstance(value, list):
                print "%s(%s)" % (ident, key)
                dump_json_obj(value, ident + "  ")
            else:
                print "%s%s: %s" % (ident, key, value)

    else:
        print "Unknown type: " + str(json_obj)


def dump_data_model(data_model, ident="  ", ignores=()):
    if isinstance(data_model, DataModel):
        for key, value in data_model:
            # ignore specified attributes
            if key in ignores:
                continue

            if isinstance(value, basestring):
                print ident + key + "=" + value
                continue
            elif isinstance(value, (int, long, float, complex)):
                print ident + key + "=" + str(value)
                continue
            print ident + key + ": "
            if isinstance(value, dict):
                dump_data_model(value, ident + "  ", ignores)
            elif isinstance(value, DataModel):
                dump_data_model(value, ident + "  ", ignores)
            elif isinstance(value, list):
                dump_data_model(value, ident + "  ", ignores)
    elif isinstance(data_model, list):
        count = 0
        for item in data_model:
            if isinstance(item, basestring):
                print ident + item
            else:
                print ident + str(count) + ") "
                dump_data_model(item, ident + "  ", ignores)
            count += 1
    else:
        print "Unknown type: " + str(data_model)

def print_data_model(data_model):
    dump_data_model(data_model, "  ", ("links", "Total", "Type", "Description", "MemberType", "Name"))

def oem_to_list(data_model):
    if data_model.Oem is None:
        return []
    return _oem_to_list(data_model.Oem, "Oem")

def _oem_to_list(data_model, attribute_name):
    result = []

    for k, v in data_model:
        if isinstance(v, DataModel):
            result.extend(_oem_to_list(v, attribute_name + "." + k))
        elif isinstance(v, basestring) or isinstance(v, bool):
            result.append("%s.%s=%s" % (attribute_name, k, v))
        elif v is None:
            result.append("%s.%s=" % (attribute_name, k))
        else:
            print "Unknown type: " + "%s=%s" % (k, str(v))
    return result

def is_bool(value):
    return value.lower() in ("true", "false", "1", "0")

def str2bool(value):
    return value.lower() in ("true", "1")
