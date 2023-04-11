# -*- coding: utf-8 -*-
# Softprime Consulting Pvt Ltd
# Copyright (C) Softprime Consulting Pvt Ltd
# All Rights Reserved
# https://softprimeconsulting.com/
from odoo import models, fields, api


class Location(models.Model):
    _inherit = 'stock.location'

    maintenance_consume = fields.Boolean('Maintenance Consume', copy=False)
