# -*- coding: utf-8 -*-
# Softprime Consulting Pvt Ltd
# Copyright (C) Softprime Consulting Pvt Ltd
# All Rights Reserved
# https://softprimeconsulting.com/
from odoo.exceptions import UserError

from odoo import api, fields, models, _


class InternalMaterialRequest(models.Model):
    _inherit = 'internal.material.request'

    assigned_to = fields.Many2one('res.users', 'Approver', required=False,
                                  domain=lambda self: [('id', 'in', self.env.user.supply_req_approve_user.ids)])

    def button_approved(self):
        """
        Set state as approved after validating for current user as an assigned approver
        """
        if self.state != 'to_approve':
            raise UserError(_('Record has been Processed Already.!!!!'))
        if not self.line_ids:
            raise UserError(_('material line is not added'))
        if self.state != 'approved':
            if self.env.uid != self.assigned_to.id:
                raise UserError(
                    _('You are not assigned approver so can not authorise to approve this material request'))
            self.write({'state': 'approved', 'material_approval_date': fields.Date.context_today(self)})
            self.create_material_request()

    def create_material_issuance(self, record_vals):
        """
        Create Record Vals
        """
        res = super(InternalMaterialRequest, self).create_material_issuance(record_vals=record_vals)
        res.approved_by = self.env.user.id
        return res

    @api.model
    def create(self, vals):
        """
        Validated for empty request lines, not same locations, same approver
        """
        res = super(InternalMaterialRequest, self).create(vals)
        if res.assigned_to == res.requested_by:
            raise UserError(_("Requester and Approver can not be same, Please change Approver!!!"))
        self.clear_caches()
        return res


class MaterialRequestLine(models.Model):
    _inherit = "internal.material.request.line"

    assigned_to = fields.Many2one('res.users', related='request_id.assigned_to', string='Assigned to', readonly=True)


class MaterialRequestIssue(models.Model):
    _inherit = 'supply.material.issue'

    approved_by = fields.Many2one('res.users', 'Approved By', copy=False)
