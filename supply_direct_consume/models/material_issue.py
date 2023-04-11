# -*- coding: utf-8 -*-
# Softprime Consulting Pvt Ltd
# Copyright (C) Softprime Consulting Pvt Ltd
# All Rights Reserved
# https://softprimeconsulting.com/
from odoo import api, fields, models, _, Command


class MaterialIssue(models.Model):
    _inherit = 'supply.material.issue'

    is_direct_consume = fields.Boolean(copy=False, string='Direct Consume')


class MaterialIssueLine(models.Model):
    _inherit = 'material.issue.line'

    def prep_stock_move_vals(self, location_id, dest_loac_id, name):
        """
        inherit for update direct consume
        """
        res = super(MaterialIssueLine, self).prep_stock_move_vals(
            location_id=location_id,
            dest_loac_id=dest_loac_id,
            name=name
        )
        if self.issue_id.is_direct_consume:
            res.update({'direct_consume_entry': True})
        return res
