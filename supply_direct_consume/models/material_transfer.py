# -*- coding: utf-8 -*-
# Softprime Consulting Pvt Ltd
# Copyright (C) Softprime Consulting Pvt Ltd
# All Rights Reserved
# https://softprimeconsulting.com/
from odoo import api, fields, models


class MaterialRequest(models.Model):
    _inherit = 'internal.material.request'

    is_direct_consume = fields.Boolean(copy=False)

    @api.depends('company_id.module_supply_request_approval', 'state',
                 'company_id.module_supply_direct_consume_approval')
    def _check_approvals_required(self):
        """
        over write for show hide button for direct approval
        """
        for request in self:
            request.approval_show = False
            request.show_button = False
            if request.env.user.company_id.module_supply_request_approval or request.env.user.company_id.module_supply_direct_consume_approval:
                request.approval_show = True
            if (
                    request.env.user.company_id.module_supply_request_approval or request.env.user.company_id.module_supply_direct_consume_approval) and request.state == 'approved':
                request.show_button = True
            if not (
                    request.env.user.company_id.module_supply_request_approval or request.env.user.company_id.module_supply_direct_consume_approval) and request.state == 'draft':
                request.show_button = True

    def _get_default_direct_dest_location(self):
        """
        Get Default Location assigned to user
        """
        location = self.env.user.view_consume_loc_ids.ids
        if len(location) == 1:
            return location[0]
        else:
            return False

    direct_dest_location_id = fields.Many2one('stock.location', string='Consume Location', store=True, required=0,
                                              domain=lambda self: [
                                                  ('id', 'in', self.env.user.view_consume_loc_ids.ids)],
                                              default=_get_default_direct_dest_location)

    def prepare_material_issue(self):
        """
        update dest location for direct consume only
        """
        res = super(MaterialRequest, self).prepare_material_issue()
        if self.is_direct_consume:
            res['dest_location_id'] = self.direct_dest_location_id.id
        return res
