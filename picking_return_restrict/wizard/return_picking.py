# Copyright Softprime Consulting Pvt Ltd.
from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class ReturnPicking(models.TransientModel):
    _inherit = "stock.return.picking"

    @api.model
    def _prepare_stock_return_picking_line_vals_from_move(self, stock_move):
        """
        Return: Delivered quantity that can to returned
        """
        res = super()._prepare_stock_return_picking_line_vals_from_move(stock_move)
        res["qty_to_return"] = res["quantity"]
        return res

    def create_returns(self):
        """
        inherit return wizard for check quantity
        """
        res = super().create_returns()
        for wizard in self:
            if wizard.product_return_moves:
                for line in wizard.product_return_moves:
                    if line.qty_to_return < line.quantity:
                        raise ValidationError(
                            _(
                                "Return Quantity should not be greater than Delivered Quantity"
                            )
                        )
                    if line.quantity <= 0.0:
                        raise ValidationError(
                            _("Return Quantity can not be equal or less than 0")
                        )
        return res


class ReturnLine(models.TransientModel):
    _inherit = "stock.return.picking.line"

    qty_to_return = fields.Float("")
