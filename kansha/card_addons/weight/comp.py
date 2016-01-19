#--
# Copyright (c) 2012-2014 Net-ng.
# All rights reserved.
#
# This software is licensed under the BSD License, as described in
# the file LICENSE.txt, which you should have received as part of
# this distribution.
#--

from nagare.i18n import _
from peak.rules import when
from nagare import component, editor, validator

from kansha.board import Board, excel_export
from kansha.cardextension import CardExtension
from kansha.services.actionlog.messages import render_event

from .models import DataCardWeight


@when(render_event, "action=='card_weight'")
def render_event_card_weight(action, data):
    return _(u'User %(author)s has weighted card "%(card)s" from (%(from)s) to (%(to)s)') % data


class CardWeightEditor(CardExtension):

    """ Card weight Form
    """

    LOAD_PRIORITY = 80

    # WEIGHTING TYPES
    WEIGHTING_OFF = 0
    WEIGHTING_FREE = 1
    WEIGHTING_LIST = 2

    def __init__(self, card, action_log, configurator):
        """
        In:
         - ``target`` -- Card instance
        """
        CardExtension.__init__(self, card, action_log, configurator)
        self.card = card
        self.weight = editor.Property(self.data.weight or u'')
        self.weight.validate(self.validate_weight)
        self.action_button = component.Component(self, 'action_button')

    def update(self, other):
        self.data.update(other.data)
        self.weight(self.data.weight or u'')

    @property
    def data(self):
        data = DataCardWeight.get_by_card(self.card.data)
        if data is None:
            data = DataCardWeight(card=self.card.data)
        return data

    def validate_weight(self, value):
        """
        Integer or empty
        """
        if value:
            validator.IntValidator(value).to_int()
        return value

    @property
    def weighting_switch(self):
        return self.configurator.weighting_cards if self.configurator else self.WEIGHTING_OFF

    @property
    def allowed_weights(self):
        return self.configurator.weights if self.configurator else ''

    def commit(self):
        success = False
        if self.weight.error is None:
            self.data.weight = self.weight.value
            success = True
        return success


@excel_export.get_extension_title_for(CardWeightEditor)
def get_extension_title_CardWeightEditor(card_extension):
    return _(u'Weight')


@excel_export.write_extension_data_for(CardWeightEditor)
def write_extension_data_CardWeightEditor(self, sheet, row, col, style):
    sheet.write(row, col, self.weight(), style)
