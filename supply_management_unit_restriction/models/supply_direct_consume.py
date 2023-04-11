# -*- coding: utf-8 -*-

# Softprime Consulting Pvt Ltd
# Copyright (C) Softprime Consulting Pvt Ltd
# All Rights Reserved
# https://softprimeconsulting.com/
from odoo import models, fields, api


class InternalMaterialRequestLine(models.Model):
    _inherit = 'internal.material.request.line'

    all_uom_ids = fields.Many2many(related="product_id.all_uom_ids")

