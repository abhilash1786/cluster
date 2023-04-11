# Softprime Consulting Pvt Ltd
# Copyright (C) Softprime Consulting Pvt Ltd
# All Rights Reserved
# https://softprimeconsulting.com/
from odoo import _, api, models


class StockQuant(models.Model):
    _inherit = "stock.quant"

    @api.model
    def action_view_inventory_non_editable(self):
        """Similar to _get_quants_action except specific for inventory adjustments
        (i.e. inventory counts)."""
        self = self._set_view_context()
        self._quant_tasks()

        ctx = dict(self.env.context or {})
        ctx["no_at_date"] = True
        if self.user_has_groups("stock.group_stock_user") and not self.user_has_groups(
            "stock.group_stock_manager"
        ):
            ctx["search_default_my_count"] = True
        action = {
            "name": _("Inventory Adjustments"),
            "view_mode": "list",
            "view_id": self.env.ref(
                "stock_onhand_readonly.stock_quant_non_editable_tree"
            ).id,
            "res_model": "stock.quant",
            "type": "ir.actions.act_window",
            "context": ctx,
            "domain": [("location_id.usage", "in", ["internal", "transit"])],
            "help": """
                    <p class="o_view_nocontent_smiling_face">
                        {}
                    </p><p>
                        {} <span class="fa fa-long-arrow-right"/> {}</p>
                    """.format(
                _("Your stock is currently empty"),
                _(
                    "Press the CREATE button to define quantity for each product in your stock or"
                    " import them from a spreadsheet throughout Favorites"
                ),
                _("Import"),
            ),
        }
        return action
