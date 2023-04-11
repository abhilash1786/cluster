# -*- coding: utf-8 -*-
# Softprime Consulting Pvt Ltd
# Copyright (C) Softprime Consulting Pvt Ltd
# All Rights Reserved
# https://softprimeconsulting.com/
from odoo import models, fields, api,_
from odoo.exceptions import UserError


class Consume(models.Model):
    _inherit = 'supply.material.consume'

    maintenance_id = fields.Many2one('maintenance.request', copy=False)

    def unlink(self):
        res = super().unlink()
        if self.maintenance_id:
            raise UserError(_('Can not delete because link with maintenance request'))
        return res

