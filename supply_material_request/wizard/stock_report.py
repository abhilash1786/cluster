# Softprime Consulting Pvt Ltd
# Copyright (C) Softprime Consulting Pvt Ltd
# All Rights Reserved
# https://softprimeconsulting.com/
from odoo import api, fields, models


class StockDailyReport(models.TransientModel):
    _inherit = "stock.wiz"

    supply_request = fields.Boolean()

    @api.onchange("supply_request", "company_id")
    def onchange_supply_stock(self):
        """to show location based on user"""
        if self.supply_request:
            if self.env.user.int_trans_loc_ids:
                return {
                    "domain": {
                        "location_ids": [
                            ("id", "in", self.env.user.int_trans_loc_ids.ids)
                        ]
                    }
                }
            return {"domain": {"location_ids": [("id", "in", [])]}}
