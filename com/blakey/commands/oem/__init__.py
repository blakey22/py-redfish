import generic
import hp

oem_table = {
    "hp": hp,
}

def get_oem_handler(name, version):
    for k, v in oem_table.iteritems():
        if k in name.lower():
            return v.OEMHandler(name, version)

    return generic.OEMHandler(name, version)