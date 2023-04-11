# Softprime Consulting Pvt Ltd
# Copyright (C) Softprime Consulting Pvt Ltd
# All Rights Reserved
# https://softprimeconsulting.com/
from odoo import _, api, models


class Product(models.Model):
    _inherit = "product.template"

    def write(self, vals):
        self.clear_caches()
        return super().write(vals)

    @api.model
    def create(self, vals):
        self.clear_caches()
        return super().create(vals)

    def stock_head_location_product(self):
        """open product list view to show qty as per location"""
        form_view_id = self.env.ref("product.product_template_only_form_view").id
        kanban_view_id = self.env.ref("product.product_template_kanban_view").id
        tree_view_id = self.env.ref("product.product_template_tree_view").id
        ctx = self.env.context.copy()
        user_env_user = self.env.user.has_group(
            "warehouse_stock_restrictions.warehouse_restriction_group"
        )
        if user_env_user:
            ctx["location"] = self.env.user.usr_stock_location_ids.ids
        loc = self.env["stock.location"].search([("usage", "=", "internal")])
        if not user_env_user:
            ctx["location"] = loc.ids
        ctx["quantity_available_locations_domain"] = "internal"
        value = {
            "name": _("Stock Products"),
            "view_mode": "tree,kanban,form",
            "res_model": "product.template",
            "views": [
                [tree_view_id, "list"],
                [form_view_id, "form"],
                [kanban_view_id, "kanban"],
            ],
            "type": "ir.actions.act_window",
            "context": ctx,
        }
        return value
