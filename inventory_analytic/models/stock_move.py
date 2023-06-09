# -*- coding: utf-8 -*-
# Part of Softprime Consulting Pvt Ltd.

from odoo import models, api, fields


# noinspection PyProtectedMember
class StockMove(models.Model):
    _inherit = "stock.move"

    analytic_account_id = fields.Many2one(
        string='Analytic Account',
        comodel_name='account.analytic.account',
    )

    def _prepare_account_move_line(self, qty, cost,
                                   credit_account_id, debit_account_id, description):
        self.ensure_one()
        res = super(StockMove, self)._prepare_account_move_line(
            qty, cost, credit_account_id, debit_account_id, description)
        # Add analytic account in debit line
        if not self.analytic_account_id or not res:
            return res

        for num in range(0, 2):
            if res[num][2]["account_id"] != self.product_id. \
                    categ_id.property_stock_valuation_account_id.id:
                res[num][2].update({
                    'analytic_account_id': self.analytic_account_id.id,
                })
        return res


class StockMoveLine(models.Model):
    _inherit = "stock.move.line"

    analytic_account_id = fields.Many2one(
        related='move_id.analytic_account_id')
