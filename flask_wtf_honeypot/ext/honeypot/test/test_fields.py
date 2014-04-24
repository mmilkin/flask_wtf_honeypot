from __future__ import unicode_literals

from datetime import datetime
from mock import patch, Mock, call, MagicMock
from wtforms import TextField
from ext.honeypot.fields import HoneyPotField, RANDOM_STYLES, HONEY_POT_PREFIX
from ext.honeypot.test import WTFHoneyPotTestCase


class HoneyPotFieldTestCase(WTFHoneyPotTestCase):
    @patch('ext.honeypot.fields.current_app')
    @patch('ext.honeypot.fields.HoneyPotField.random')
    def get_field(self, random,current_app):
        random.return_value = 'be_random'
        current_app.config = {'WTF_HONEY_POT_PRIVATE_KEY': 'abc'}
        field = HoneyPotField().bind(None, 'other', prefix='', translations=None)
        return field


class HoneyPotFieldRootTestCase(HoneyPotFieldTestCase):

    @patch('ext.honeypot.fields.current_app')
    @patch('ext.honeypot.fields.randint')
    @patch('ext.honeypot.fields.HoneyPotField.random')
    def test_init(self, random, randint, current_app):
        randint.return_value = 3
        random.return_value = 'not_random'
        current_app.config = {'WTF_HONEY_POT_PRIVATE_KEY': 'abc'}
        field = HoneyPotField().bind(None, 'other', prefix='', translations=None)
        self.assertEqual(field.entrie_count, 3)
        self.assertIsNotNone(field.unbound_field)
        self.assertEqual(field.unbound_field.field_class, TextField)
        self.assertEqual(field.timeout, 300)

    #60-61, 72, 104-105, 140
    @patch('ext.honeypot.fields.current_app')
    def test_init_bad_key(self, current_app):
        current_app.config = {'WTF': 'abc'}
        with self.assertRaises(RuntimeError):
            HoneyPotField().bind(None, 'other', prefix='', translations=None)

    @patch('ext.honeypot.fields.current_app')
    @patch('ext.honeypot.fields.randint')
    @patch('ext.honeypot.fields.HoneyPotField.random')
    def test_init_timeout(self, random, randint, current_app):
        randint.return_value = 3
        random.return_value = 'not_random'
        current_app.config = {
            'WTF_HONEY_POT_PRIVATE_KEY': 'abc',
            'WTF_HONEY_POT_TIMEOUT': 20,
        }
        field = HoneyPotField().bind(None, 'other', prefix='', translations=None)
        self.assertEqual(field.entrie_count, 3)
        self.assertIsNotNone(field.unbound_field)
        self.assertEqual(field.unbound_field.field_class, TextField)
        self.assertEqual(field.timeout, 20)

    @patch('ext.honeypot.fields.HoneyPotField.random')
    def test_short_name(self, random):
        random.return_value = 'be_random'
        field = self.get_field()
        self.assertEqual(field.short_name, 'be_random')

    @patch('ext.honeypot.fields.choice')
    def test_style(self, choice):
        field = self.get_field()
        _ = field.style
        choice.assert_called_with(RANDOM_STYLES)

    def test_hash_entries(self):
        field = self.get_field()
        field.private_key = 'private'
        first = Mock(name='first')
        first.name = u'first'
        second = Mock(name='second')
        second.name = u'second'
        third = Mock(name='third')
        third.name = u'3third'
        field.entries = [first, second, third]
        expected = field.hash_entries(12345)
        self.assertEqual(expected, '2e0ecd36fe260c06cf50fecac17ea0242a0046bcb697dadaa2cb5c3abb7c32df')

    @patch('ext.honeypot.fields.HoneyPotField.random')
    @patch('ext.honeypot.fields.HoneyPotField._get_epoch')
    def test_reset(self, _get_epoch, random):
        random.return_value = '1'
        _get_epoch.return_value = 123
        field = self.get_field()
        field.unbound_field = Mock(name=u'UnboundField')
        field.entrie_count = 1
        field.entries = [u'some entries']

        bound_field = Mock()
        field.unbound_field.bind.return_value = bound_field

        field.reset_honeypot(None)
        actual_bind = field.unbound_field.bind.call_args_list
        actual_processed = bound_field.process.call_args_list

        expected_bind = [
            call(id=u'1', form=None, name=u'hp_1'),
            call(id=u'1', form=None, name=u'hp_check_123')
        ]

        expected_processed = [
            call(None, None),
            call(None, u'dd130a849d7b29e5541b05d2f7f86a4acd4f1ec598c1c9438783f56bc4f0ff80')
        ]

        self.assertEqual(expected_bind, actual_bind)
        self.assertEqual(expected_processed, actual_processed)

    def test_iteration(self):
        field = self.get_field()
        field.entries = ['one']

        for entrie in field:
            self.assertEqual(entrie, 'one')

    def test_test_index(self):
        field = self.get_field()
        field.entries = ['one', 'two', 'three']

        self.assertEqual(field[0], 'one')
        self.assertEqual(field[1], 'two')
        self.assertEqual(field[2], 'three')

    def test_length(self):
        field = self.get_field()
        field.entries = ['one', 'two', 'three']
        self.assertEqual(len(field), 3)


class HoneyPotFieldProcessTestCase(HoneyPotFieldTestCase):

    @patch('ext.honeypot.fields.HoneyPotField.reset_honeypot')
    def test_process_empty_formdata(self, reset_honeypot):
        field = self.get_field()
        field.process(None)
        self.assertTrue(reset_honeypot.called)

    @patch('ext.honeypot.fields.HoneyPotField.reset_honeypot')
    def test_process_empty_formdata_exception(self, reset_honeypot):
        field = self.get_field()

        formdata = MagicMock()
        formdata.__getitem__.side_effect = StopIteration
        formdata.__iter__ = Mock(return_value=iter([HONEY_POT_PREFIX + '_1']))

        unbound_field = Mock(name='UnboundField')
        bound_field = Mock(name='BoundField')
        unbound_field.bind.return_value = bound_field
        field.unbound_field = unbound_field

        field.process(formdata)

        actual_process = bound_field.process.call_args_list

        expected_process = [
            call(formdata, u''),
        ]

        self.assertEqual(expected_process, actual_process)


    @patch('ext.honeypot.fields.HoneyPotField.random')
    def test_process_form_with_formdata(self, random):
        random.return_value = 'random'
        formdata = {
            'some_field': 'dataf',
            HONEY_POT_PREFIX + '_1': 'data_1',
            HONEY_POT_PREFIX + '_2': 'data_2'
        }

        field = self.get_field()
        unbound_field = Mock(name='UnboundField')
        bound_field = Mock(name='BoundField')
        unbound_field.bind.return_value = bound_field
        field.unbound_field = unbound_field

        field.process(formdata)

        actual_bind = field.unbound_field.bind.call_args_list
        actual_process = bound_field.process.call_args_list

        expected_bind = [
            call(id=u'random', form=None, name=HONEY_POT_PREFIX + '_1'),
            call(id=u'random', form=None, name=HONEY_POT_PREFIX + '_2')
        ]

        expected_process = [
            call(formdata, u'data_1'),
            call(formdata, u'data_2')
        ]

        self.assertEqual(expected_bind, actual_bind)
        self.assertEqual(expected_process, actual_process)


class HoneyPotFieldValidationTestCase(HoneyPotFieldTestCase):

    def _populate_field(self, field, hp_field_data=None, hash_control=None):
        field.private_key = 'private'
        field.timeout = 2000
        first = Mock(name='first')
        first.data = hp_field_data
        first.name = u'first'
        control = Mock(control='control')
        now = datetime.now().strftime('%s')
        control.name = HoneyPotField.get_control_prefix() + now
        field.entries = [first]
        control.data = hash_control if hash_control else field.hash_entries(now)
        field.entries.append(control)

    def test_invalid_time(self):
        field = self.get_field()
        field.timeout = 200
        self.assertFalse(field.validate_time('not a date'))

    def test_validate_time_future(self):
        field = self.get_field()
        field.timeout = 200
        self.assertTrue(field.validate_time(int(datetime.now().strftime('%s'))))

    def test_validate_time_past(self):
        field = self.get_field()
        field.timeout = -2
        self.assertFalse(field.validate_time(int(datetime.now().strftime('%s'))))

    def test_validation_valid(self):
        field = self.get_field()
        self._populate_field(field)
        self.assertTrue(field.validate(None))

    def test_validation_no_data(self):
        field = self.get_field()
        self._populate_field(field)
        field.entries = []
        control = Mock(control='control')
        now = datetime.now().strftime('%s')
        control.name = HoneyPotField.get_control_prefix() + now
        control.data = None
        field.entries = [control]
        self.assertFalse(field.validate(None))

    def test_validation_no_controll_field(self):
        field = self.get_field()
        self._populate_field(field)
        field.entries = field.entries[:-1]
        self.assertFalse(field.validate(None))

    def test_validation_invalid_input(self):
        field = self.get_field()
        self._populate_field(field, hp_field_data=u'some data')
        self.assertFalse(field.validate(None))

    @patch('ext.honeypot.fields.HoneyPotField.validate_time')
    def test_validation_invalid_time(self, validate_time):
        validate_time.return_value = False
        field = self.get_field()
        self._populate_field(field)
        self.assertFalse(field.validate(None))

    def test_validation_bad_hash(self):
        field = self.get_field()
        self._populate_field(field, hash_control='not hashed')
        self.assertFalse(field.validate(None))

    @patch('ext.honeypot.fields.HoneyPotField.reset_honeypot')
    def test_validation_cleanup(self, reset_honeypot):
        field = self.get_field()
        self._populate_field(field, hash_control='not hashed')
        self.assertFalse(field.validate(None))
        reset_honeypot.assert_called_with(None)
