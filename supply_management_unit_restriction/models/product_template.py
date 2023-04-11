# -*- coding: utf-8 -*-

# Softprime Consulting Pvt Ltd
# Copyright (C) Softprime Consulting Pvt Ltd
# All Rights Reserved
# https://softprimeconsulting.com/
from odoo import models, fields, api


class ProductTemplate(models.Model):
    _inherit = "product.product"

    all_uom_ids = fields.Many2many('uom.uom', 'product_template_supply_management_rel', compute='compute_all_uom')

    @api.onchange('uom_id', 'uom_po_id')
    def compute_all_uom(self):
        """
        Compute uom
        """
        for product in self:
            product.all_uom_ids = []
            uom = []
            if product.uom_id:
                uom.append(product.uom_id.id)
            if product.uom_po_id:
                uom.append(product.uom_po_id.id)
            if uom:
                product.all_uom_ids = [(6, 0, uom)]


