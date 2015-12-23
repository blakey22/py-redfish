class OEMHandler(object):
    """
    Handler class for oem extension

    Any vendor specified oem attribute should extend this class,
    For example, HP server requires at least one extra attribute to create user account.
        In this case, vendor can implement method from generic OEMHandler class to add the attribute(s)
    """
    def __init__(self, oem_name, version):
        self.oem_name = oem_name
        self.version = version

    def user_create(self, username, password, privilege):
        """
        For "user" command to extend "create" method calls

        :param username: username for creation
        :param password: password for creation
        :param privilege: privilege for this user
        :return: dict object with oem specified attribute(s)
        """
        return {}