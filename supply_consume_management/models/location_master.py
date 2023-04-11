# -*- coding: utf-8 -*-

# Softprime Consulting Pvt Ltd
# Copyright (C) Softprime Consulting Pvt Ltd
# All Rights Reserved
# https://softprimeconsulting.com/
from odoo import fields, models, api, _


class StockLocation(models.Model):
    _inherit = 'stock.location'

    is_consume_loc = fields.Boolean(string='Consumption Location')