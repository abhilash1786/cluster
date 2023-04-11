# -*- coding: utf-8 -*-
# Softprime Consulting Pvt Ltd
# Copyright (C) Softprime Consulting Pvt Ltd
# All Rights Reserved
# https://softprimeconsulting.com/
from odoo import fields, models, api, _


class SupplyReqLine(models.Model):
    _inherit = 'internal.material.request.line'

    pr_created = fields.Boolean(copy=False)
