# Softprime Consulting Pvt Ltd
# Copyright (C) Softprime Consulting Pvt Ltd
# All Rights Reserved
# https://softprimeconsulting.com/
from odoo import _, models


class ProductTemplate(models.Model):
    _inherit = "product.template"

    def action_open_quants_non_editable(self):
        return self.product_variant_ids.filtered(
            lambda p: p.active or p.qty_available != 0
        ).action_open_quants_non_editable()


class ProductProduct(models.Model):
    _inherit = "product.product"

    def action_open_quants_non_editable(self):
        domain = [("product_id", "in", self.ids)]
        hide_location = not self.user_has_groups("stock.group_stock_multi_locations")
        hide_lot = all(product.tracking == "none" for product in self)
        self = self.with_context(
            hide_location=hide_location,
            hide_lot=hide_lot,
            no_at_date=True,
            search_default_on_hand=True,
        )

        # If user have rights to write on quant, we define the view as editable.
        if self.user_has_groups("stock.group_stock_manager"):
            self = self.with_context(inventory_mode=True)
            # Set default location id if multilocations is inactive
            if not self.user_has_groups("stock.group_stock_multi_locations"):
                user_company = self.env.company
                warehouse = self.env["stock.warehouse"].search(
                    [("company_id", "=", user_company.id)], limit=1
                )
                if warehouse:
                    self = self.with_context(
                        default_location_id=warehouse.lot_stock_id.id
                    )
        # Set default product id if quants concern only one product
        if len(self) == 1:
            self = self.with_context(default_product_id=self.id, single_product=True)
        else:
            self = self.with_context(product_tmpl_ids=self.product_tmpl_id.ids)
        action = self.env["stock.quant"].action_view_inventory_non_editable()
        action["domain"] = domain
        action["name"] = _("Onhand Quantity")
        return action
