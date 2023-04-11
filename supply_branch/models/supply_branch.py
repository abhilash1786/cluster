# -*- coding: utf-8 -*-
# Softprime Consulting Pvt Ltd
# Copyright (C) Softprime Consulting Pvt Ltd
# All Rights Reserved
# https://softprimeconsulting.com/
from odoo import api, fields, models


class SupplyBranch(models.Model):
    _inherit = "supply.material.consume"

    def _domain_branch(self):
        """
        Branch domain of requester
        """
        return [('id', 'in', self.env.user.branch_ids.ids)]

    branch_id = fields.Many2one('res.branch', copy=False, tracking=True,
                                domain=lambda self: self._domain_branch())

    @api.model
    def default_get(self, fields):
        res = super(SupplyBranch, self).default_get(fields)
        if len(self.env.user.branch_ids.ids) == 1:
            res['branch_id'] = self.env.user.branch_ids.id
        return res

    def picking_vals_list_prep(self):
        """
        inherit for update task sale
        """
        res = super(SupplyBranch, self).picking_vals_list_prep()
        if res:
            res.update({
                        'branch_id': self.branch_id.id
            })
        return res


class StockMove(models.Model):
    _inherit = 'stock.move'

    def _prepare_account_move_vals(self, credit_account_id, debit_account_id, journal_id, qty, description, svl_id, cost):
        res = super(StockMove, self)._prepare_account_move_vals(credit_account_id, debit_account_id, journal_id, qty, description, svl_id, cost)
        if self.task_id and self.task_id.branch_id:
            res.update({'branch_id': self.task_id.branch_id.id})
            for line in range(len(res['line_ids'])):
                res['line_ids'][line][2].update({
                    'branch_id': self.task_id.branch_id.id,
                })
        return res

