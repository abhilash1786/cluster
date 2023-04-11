# Softprime Consulting Pvt Ltd
# Copyright (C) Softprime Consulting Pvt Ltd
# All Rights Reserved
# https://softprimeconsulting.com/
from odoo import _, api, fields, models
from odoo.exceptions import Warning


class ResUsers(models.Model):
    _inherit = "res.users"

    def write(self, vals):
        self.clear_caches()
        return super().write(vals)

    @api.model
    def create(self, vals):
        self.clear_caches()
        return super().create(vals)

    usr_stock_location_ids = fields.Many2many(
        "stock.location",
        "location_warehouse_user_rel",
        "user_id",
        "location_id",
        "Stock Locations",
        domain=[("usage", "=", "internal")],
    )
    warehouse_ids = fields.Many2many(
        "stock.warehouse", "user_warehouse_ref", "user_id", "wh_id"
    )


class StockMove(models.Model):
    _inherit = "stock.move"

    def write(self, vals):
        self.clear_caches()
        return super().write(vals)

    @api.model
    def create(self, vals):
        self.clear_caches()
        return super().create(vals)


class StockPicking(models.Model):
    _inherit = "stock.picking"

    def write(self, vals):
        self.clear_caches()
        return super().write(vals)

    @api.model
    def create(self, vals):
        self.clear_caches()
        return super().create(vals)

    def action_done(self):
        """move done with allowed location"""
        for rec in self:
            if self.env.context.get("sale_cancel"):
                return super().action_done()
            user_locations = self.env.user.usr_stock_location_ids
            restriction_user = self.env.user.has_group(
                "warehouse_stock_restrictions.warehouse_restriction_group"
            )
            if restriction_user and not self.env.context.get("force_confirm", False):
                message = _(
                    "Invalid Location. You cannot process this move since you do"
                    'not control the location "%s". '
                    "Please contact your Administrator."
                )
                if (
                    rec.location_dest_id.id not in user_locations.ids
                    and rec.location_dest_id.usage == "internal"
                ) or (
                    rec.location_id.id not in user_locations.ids
                    and rec.location_id.usage == "internal"
                ):
                    raise Warning(message % rec.location_dest_id.display_name)
            return super().action_done()


class StockLocation(models.Model):
    _inherit = "stock.location"

    def write(self, vals):
        self.clear_caches()
        return super().write(vals)

    @api.model
    def create(self, vals):
        self.clear_caches()
        return super().create(vals)


class Quant(models.Model):
    _inherit = "stock.quant"

    def write(self, vals):
        self.clear_caches()
        return super().write(vals)

    @api.model
    def create(self, vals):
        self.clear_caches()
        return super().create(vals)
