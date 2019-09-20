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


class NotEmptyValidator(Validator):

    def __init__(self, name='Field'):
        self.name = name

    @staticmethod
    def validate(value):
        return len(value) > 0

    def tooltip(self):
        return "{} must not be empty".format(self.name)


class IntegerValidator(Validator):

    def __init__(self, name='Field'):
        self.name = name

    @staticmethod
    def validate(value):
        try:
            int(value)
            return True
        except ValueError:
            return False

    def tooltip(self):
        return "{} '{}' is not an integer".format(self.name, self.value)


class FileValidator(Validator):

    @staticmethod
    def validate(value):
        return os.path.isfile(value)

    def tooltip(self):
        return "{} is not a valid file".format(self.value)


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


class AtomValidator(Validator):

    @classmethod
    def validate(cls, value):
        if not value:
            return True
        try:
            res, name = cls._split_value(value)
        except AttributeError:
            return False

        try:
            return cls._validate_with_pymol(res, name)
        except ImportError:
            return True

    @staticmethod
    def _split_value(value):
        import re
        return re.match('([0-9]+).([a-zA-Z0-9]+)$', value).groups()

    @staticmethod
    def _validate_with_pymol(res, name):
        import pymol
        selection = 'resi {} and name {}'.format(res, name)
        return pymol.cmd.count_atoms(selection) == 1

    def tooltip(self):
        return "Selection {} has zero or more than one atom.".format(self.value)
