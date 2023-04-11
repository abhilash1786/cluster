# -*- coding: utf-8 -*-
# Copyright  Softprime consulting Pvt Ltd
from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    holding_account_id = fields.Many2one('account.account', string='Holding Account',
                                         related='company_id.holding_account_id', readonly=False)
    is_allow_email = fields.Boolean('Allow Landed Cost Approval Email',
                                    related='company_id.is_allow_email', readonly=False)
