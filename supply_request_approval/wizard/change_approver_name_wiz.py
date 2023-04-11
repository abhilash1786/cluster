# -*- coding: utf-8 -*-

# Softprime Consulting Pvt Ltd
# Copyright (C) Softprime Consulting Pvt Ltd
# All Rights Reserved
# https://softprimeconsulting.com/
from odoo import models, fields, api, _

class ChangeApproverNameWiz(models.TransientModel):
    _name = 'change.approver.name.wiz'
    _description = 'Approver Name Change Wizard'

    approver_id = fields.Many2one('res.users', required=1, string='New Approver', domain=lambda self: [('id', 'in', self.env.user.supply_req_approve_user.ids)])
    mat_req_id =  fields.Many2one('internal.material.request', default=lambda self: self._context.get('active_ids'))

    def change_approver(self):
        active_id = self.env.context.get('active_ids', [])
        pick_id = self.env['internal.material.request'].browse(active_id)
        for pick in self:
            if pick_id.assigned_to.id != pick.env.user.id:
                pick_id.assigned_to = pick.approver_id
