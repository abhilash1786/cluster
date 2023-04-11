# -*- coding: utf-8 -*-
# Softprime Consulting Pvt Ltd
# Copyright (C) Softprime Consulting Pvt Ltd
# All Rights Reserved
# https://softprimeconsulting.com/
from odoo import fields, models


class ResUsers(models.Model):
    _inherit = 'res.users'

    supply_req_approve_user = fields.Many2many('res.users', 'supply_req_approval_ref', 'user_id' 'supply_id',
                                               domain=lambda self: [('groups_id', 'in', self.env.ref('supply_request_approval.group_internal_material_request_manager').id)])
