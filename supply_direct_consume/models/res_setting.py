# -*- coding: utf-8 -*-
# Softprime Consulting Pvt Ltd
# Copyright (C) Softprime Consulting Pvt Ltd
# All Rights Reserved
# https://softprimeconsulting.com/
from odoo import fields, models, api, _


class ResCompany(models.Model):
    _inherit = 'res.company'

    module_supply_direct_consume_approval = fields.Boolean('Approval for Direct Consume')


class ResConfigSetting(models.TransientModel):
    _inherit = 'res.config.settings'

    module_supply_direct_consume_approval = fields.Boolean(string='Supply Direct Consume Approval Required',
                                                    related='company_id.module_supply_direct_consume_approval', readonly=False)

    @api.onchange('module_supply_request_approval')
    def onchange_approval_process_supply(self):
        self.module_supply_direct_consume_approval = self.module_supply_request_approval