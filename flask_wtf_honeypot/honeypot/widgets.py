from __future__ import unicode_literals

from wtforms.widgets import HTMLString, html_params

__all__ = ["HoneyPotWidget"]


class HoneyPotWidget(object):
    """
    Renders a list of hidden fields
    """
    def __call__(self, field, **kwargs):
        html_list = []
        for subfield in field:
            html_list.append(
                '%s' % (subfield(**field.style))
            )
        return HTMLString(''.join(html_list))
