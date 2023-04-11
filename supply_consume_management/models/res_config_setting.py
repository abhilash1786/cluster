# -*- coding: utf-8 -*-

# Softprime Consulting Pvt Ltd
# Copyright (C) Softprime Consulting Pvt Ltd
# All Rights Reserved
# https://softprimeconsulting.com/
from odoo import fields, models, api, _


class ResUsers(models.Model):
    _inherit = 'res.users'

    view_consume_loc_ids = fields.Many2many('stock.location', 'users_location_material_consume',
                                            string='Assigned Consume Locations')