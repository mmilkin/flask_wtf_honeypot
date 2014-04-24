from __future__ import unicode_literals

from datetime import datetime, timedelta
from random import randint, choice
import string
from flask import current_app
from wtforms.fields import TextField, Field
from hashlib import sha256
from . import widgets

__all__ = ['HoneyPotField']

HONEY_POT_PREFIX = 'hp'


RANDOM_STYLES = [{'style': 'display:none; border: none;'}, {'style': 'width:1px; height:1px; border: none;'}]
_unset_value = object()


class HoneyPotField(Field):
    """
    The HoneyPotField
    """
    widget = widgets.HoneyPotWidget()

    def __init__(self, *args, **kwargs):
        try:
            self.private_key = current_app.config['WTF_HONEY_POT_PRIVATE_KEY']
        except KeyError:
            raise RuntimeError("No WTF_HONEY_POT_PRIVATE_KEY config set")

        self.timeout = current_app.config.get('WTF_HONEY_POT_TIMEOUT', 300)
        self.unbound_field = TextField(self.random())
        self.entrie_count = randint(1, 5)
        super(HoneyPotField, self).__init__(*args, **kwargs)

    def random(self):
        return ''.join(choice(string.ascii_lowercase + string.digits) for _ in range(randint(5,12)))

    @property
    def short_name(self):
        return self.random()

    @short_name.setter
    def short_name(self, value):
        pass

    @property
    def style(self):
        return choice(RANDOM_STYLES)

    def process(self, formdata, data=_unset_value):
        self.entries = []

        if formdata:
            indices = sorted(set(self._extract_indices(HONEY_POT_PREFIX, formdata)))
            for name in indices:
                try:
                    obj_data = formdata[name]
                except StopIteration:
                    obj_data = u''

                self._add_entry(formdata, obj_data, name=name)

        else:
            self.reset_honeypot(formdata)

    def validate(self, form, extra_validators=tuple()):
        success = True
        try:
            control_field = self._get_control_field()
        except ValueError:
            return False

        if not self.data or not control_field.data:
            success = False

        for entrie in self.entries:
            if entrie.data and not entrie.name.startswith(self.get_control_prefix()):
                success = False
                # No need to continue the trap is caught
                break

        current_time = int(control_field.name[9:])
        success = success and self.validate_time(current_time)
        success = success and control_field.data == self.hash_entries(current_time)

        # If the honey_pot caught a bot or a bear resetting the trap
        if not success:
            self.reset_honeypot(None)

        return success

    def hash_entries(self, current_time):
        names = [str(current_time), self.private_key]
        for entrie in self.entries:
            if not entrie.name.startswith(self.get_control_prefix()):
                names.append(entrie.name)

        name_values = u''.join(sorted(names))

        return unicode(sha256(name_values).hexdigest())

    def validate_time(self, epoch):
        now = datetime.now()
        try:
            then = datetime.fromtimestamp(epoch)
        except Exception:
            return False
        else:
            window = timedelta(seconds=self.timeout)
            if (then + window) < now:
                return False
        return True

    def reset_honeypot(self, formdata):
        self.entries = []
        while len(self.entries) < self.entrie_count:
            self._add_entry(formdata, None)
        # Adding control form element
        self._add_control_field(formdata)

    @classmethod
    def get_control_prefix(self):
        return '{0}_{1}_'.format(HONEY_POT_PREFIX, 'check')

    def _get_epoch(self):
        """
        Function to help unittest
        """
        return datetime.now().strftime('%s')

    def _add_control_field(self, formdata):
        """
        Create control field to validate honeypot
        """
        current_time = self._get_epoch()
        value = self.hash_entries(current_time)
        self._add_entry(formdata=formdata, data=value, name="{0}{1}".format(self.get_control_prefix(), current_time))

    def _get_control_field(self):
        control_fields = [entrie for entrie in self.entries if entrie.name.startswith(self.get_control_prefix())]
        if len(control_fields) != 1:
            raise ValueError('Must one control_field')
        return control_fields[0]

    def _extract_indices(self, prefix, formdata):
        """
        Yield all the names given the honey pot prefix.

        This will yeild all the fields example hp_vazzg or hp_2gpkdef3ch
        """
        for k in formdata:
            if k.startswith(prefix):
                yield k

    def _add_entry(self, formdata=None, data=_unset_value, name=None, identifier=None):
        name = name if name else 'hp_' + self.random()
        identifier = identifier if identifier else self.random()

        field = self.unbound_field.bind(form=None, name=name, id=identifier)
        field.process(formdata, data)
        self.entries.append(field)
        return field

    def __iter__(self):
        return iter(self.entries)

    def __len__(self):
        return len(self.entries)

    def __getitem__(self, index):
        return self.entries[index]

    @property
    def data(self):
        return [f.data for f in self.entries]
