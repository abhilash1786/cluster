# -*- coding: utf-8 -*-
# Softprime Consulting Pvt Ltd
# Copyright (C) Softprime Consulting Pvt Ltd
# All Rights Reserved
# https://softprimeconsulting.com/
from odoo import fields, models, api, _


class PurchaseReq(models.Model):
    _inherit = 'sp.purchase.request'

    is_supply_req_create = fields.Boolean(copy=False)
