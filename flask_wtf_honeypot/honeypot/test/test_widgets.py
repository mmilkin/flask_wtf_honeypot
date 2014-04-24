from mock import Mock
from flask_wtf_honeypot.honeypot.test import WTFHoneyPotTestCase
from flask_wtf_honeypot.honeypot.widgets import HoneyPotWidget


class HoneyPotWidgetTestCase(WTFHoneyPotTestCase):

    def test_widget(self):
        subfield_1 = Mock(name='subfield_1')
        subfield_1.return_value = u'[first input]'
        subfield_2 = Mock(name='subfield_2')
        subfield_2.return_value = u'[second input]'
        field = Mock(name='field')
        field.style = {'style': 'display:none;'}
        field.__iter__ = Mock(return_value=iter([subfield_1, subfield_2]))
        widget = HoneyPotWidget()
        actual = widget(field)
        subfield_2.assert_called_with(style='display:none;')
        subfield_1.assert_called_with(style='display:none;')
        self.assertEqual(actual, '[first input][second input]')
