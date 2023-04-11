# Part of Softprime Consulting Pvt Ltd.
from odoo import api, fields, models


class StockMove(models.Model):
    _inherit = "stock.move"

    available_qty = fields.Float(
        "Available Quantity", compute="_compute_get_available_product_qty", store=True
    )

    @api.depends("product_id", "location_id")
    def _compute_get_available_product_qty(self):
        for rec in self:
            rec.available_qty = 0.0
            quant_obj = self.env["stock.quant"]
            if rec.product_id:
                available_qty = quant_obj._get_available_quantity(
                    product_id=rec.product_id, location_id=rec.location_id, strict=True
                )
                rec.available_qty = available_qty


class StockMoveLine(models.Model):
    _inherit = "stock.move.line"

    available_qty = fields.Float(
        "Available Quantity", compute="_compute_get_available_product_qty", store=True
    )

    @api.depends("product_id", "location_id")
    def _compute_get_available_product_qty(self):
        quant_obj = self.env["stock.quant"]
        for rec in self:
            rec.available_qty = 0.0
            if rec.product_id and rec.location_id:
                available_qty = quant_obj._get_available_quantity(
                    product_id=rec.product_id, location_id=rec.location_id, strict=True
                )
                rec.available_qty = available_qty

