# -*- coding: utf-8 -*-
# Copyright  Softprime consulting Pvt Ltd
from odoo import api, fields, models


class ResCompany(models.Model):
    _inherit = 'res.company'

    holding_account_id = fields.Many2one('account.account', string='Holding Account')
    is_allow_email = fields.Boolean('Allow Landed Cost Approval Email')
