# -*- coding: utf-8 -*-

# Softprime Consulting Pvt Ltd
# Copyright (C) Softprime Consulting Pvt Ltd
# All Rights Reserved
# https://softprimeconsulting.com/
from odoo import api, fields, models


class StockMove(models.Model):
    _inherit = 'stock.move'

    def _get_accounting_data_for_valuation(self):
        """
        Account Move Valuation Data
        """
        res = super(StockMove, self)._get_accounting_data_for_valuation()
        if self.location_id and self.location_id.usage == 'customer' and self.location_id.valuation_in_account_id:
            res = list(res)
            res[2] = self.location_id.valuation_in_account_id.id
            res = tuple(res)
        return res