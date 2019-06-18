import os


class Validator:

    def __init__(self):
        self.value = ''

    def __call__(self, value):
        self.value = value
        return self.validate(value)

    @staticmethod
    def validate(value):
        raise NotImplementedError

    def tooltip(self):
        return ''


class FileValidator(Validator):

    @staticmethod
    def validate(value):
        return os.path.isfile(value)

    def tooltip(self):
        return "Not a valid file"


class DirectoryValidator(Validator):

    @staticmethod
    def validate(value):
        return os.path.isdir(value)

    def tooltip(self):
        return "Not a valid directory"


class PdbValidator(Validator):

    @staticmethod
    def validate(value):
        ext = os.path.splitext(value)[-1]
        return os.path.isfile(value) and ext.lower() == '.pdb'

    def tooltip(self):
        return "'{}' is not a valid PDB file".format(self.value)


class EnlightenValidator(Validator):

    @staticmethod
    def validate(value):
        return (os.path.isdir(value) and
                os.path.isfile(os.path.join(value, 'prep.py')))

    def tooltip(self):
        return "'{}' is not a valid Enlighten path.\n"\
               "Check that the path contains prep.py script.".format(self.value)


class AmberValidator(Validator):

    @staticmethod
    def validate(value):
        amber_bin_path = os.path.join(value, 'bin')
        if not os.path.isdir(amber_bin_path):
            return False
        for filename in ('antechamber', 'pdb4amber', 'reduce'):
            if not os.path.isfile(os.path.join(amber_bin_path, filename)):
                return False
        return True

    def tooltip(self):
        return "'{}' is not a valid Amber path.\n"\
               "Check that the path contains 'bin' directory with "\
               "antechamber, pdb4amber and reduce executables.".format(self.value)
