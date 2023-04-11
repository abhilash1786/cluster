# -*- coding: utf-8 -*-

# Softprime Consulting Pvt Ltd
# Copyright (C) Softprime Consulting Pvt Ltd
# All Rights Reserved
# https://softprimeconsulting.com/

from odoo import fields, api,models, _
from odoo.exceptions import ValidationError


class StockDailyMovementWiz(models.TransientModel):
    _name = "stock.movement.wiz"

    from_date = fields.Date('From')
    to_date = fields.Date('To')
    product_ids = fields.Many2many('product.product', string='Product')
    location_ids = fields.Many2many('stock.location', string='Internal Location')
    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.user.company_id)

    @api.constrains('from_date', 'to_date')
    def validate_date(self):
        """
        Validating from date and to date whether the date entered is valid or not
        """
        if self.from_date and self.to_date:
            if self.from_date > self.to_date:
                raise ValidationError(_('From date cannot be greater than to date'))

    def action_get_data(self):
        """
        Action to get data
        """
        action = self.env.ref('stock_daily_movement.action_stock_movement_db_view').read()[0]
        self.env['stock.daily.movement.db.view'].get_data(self.from_date, self.to_date, self.product_ids, self.location_ids, self.company_id)
        return action