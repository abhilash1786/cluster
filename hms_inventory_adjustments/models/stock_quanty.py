# Copyright  Softprime consulting Pvt Ltd
from odoo import fields, models


class StockQuant(models.Model):
    _inherit = "stock.quant"

    res_adjustment_id = fields.Many2one("res.inventory.adjustment", copy=False)
    adjustment_line_id = fields.Many2one("inventory.adjustment.line", copy=False)

    def _get_inventory_move_values(self, qty, location_id, location_dest_id, out=False):
        """
        Method to update analytic account.
        :param qty:
        :param cost:
        :param credit_account_id:
        :param debit_account_id:
        :param description:
        :return:
        """
        self.ensure_one()
        res = super()._get_inventory_move_values(
            qty, location_id, location_dest_id, out
        )
        if res and self.res_adjustment_id:
            res.update(
                {
                    "analytic_account_id": self.res_adjustment_id.analytic_account_id.id,
                }
            )
        return res
