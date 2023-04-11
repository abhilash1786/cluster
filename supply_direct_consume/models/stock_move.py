# -*- coding: utf-8 -*-
# Softprime Consulting Pvt Ltd
# Copyright (C) Softprime Consulting Pvt Ltd
# All Rights Reserved
# https://softprimeconsulting.com/
from odoo import api, fields, models, _, Command


class StockMove(models.Model):
    _inherit = 'stock.move'

    direct_consume_entry = fields.Boolean(copy=False)
