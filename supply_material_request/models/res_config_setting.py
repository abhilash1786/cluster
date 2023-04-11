# -*- coding: utf-8 -*-
# Softprime Consulting Pvt Ltd
# Copyright (C) Softprime Consulting Pvt Ltd
# All Rights Reserved
# https://softprimeconsulting.com/
from odoo import fields, models


class ResCompany(models.Model):
    _inherit = 'res.company'

    module_supply_request_approval = fields.Boolean('Approval for Internal Transfer')
    supply_transit_loc = fields.Many2one('stock.location')
    supply_transit_days = fields.Integer('Days Transit', default=1)


class ResConfigSetting(models.TransientModel):
    _inherit = 'res.config.settings'

    supply_transit_loc = fields.Many2one('stock.location', string='Supply Transit Location',
                                         related='company_id.supply_transit_loc', readonly=False)
    supply_transit_days = fields.Integer(related='company_id.supply_transit_days', readonly=False)
    module_supply_request_approval = fields.Boolean(string='Supply Transfer Approval Required',
                                                    readonly=False)


class ResUsers(models.Model):
    _inherit = 'res.users'

    int_trans_loc_ids = fields.Many2many('stock.location', 'users_location_int_material',
                                         string='Assigned Supply Locations')
    source_trans_location = fields.Many2many('stock.location', 'users_location_source_int_material_ref',
                                             'supply_loc_user', 'user_id', string='Assigned Supply Source Location')

    def write(self, vals):
        self.clear_caches()
        return super(ResUsers, self).write(vals)
