# -*- coding: utf-8 -*-
# Part of Softprime Consulting Pvt Ltd.
from odoo import fields, models, _, api
from odoo.exceptions import UserError, ValidationError


class StockPicking(models.Model):
    _inherit = 'stock.picking'
    _description = 'Stock Picking'

    @api.constrains('location_id', 'location_dest_id')
    def constrains_location(self):
        """
        Show warning if transfer having view location
        """
        if self.location_id.usage == "view" or self.location_dest_id.usage == "view":
            raise UserError(_("You Can Not Create Transfer For View Type Location !!!"))

    def button_validate(self):
        """
        This method is overload to validate internal transfer location
        :return:
        """

        for picking in self:
            for rec in picking.move_ids_without_package:
                if not (picking.location_id == rec.location_id):
                    raise ValidationError(_('Source Location should be same to validate!!!'))
                if not (picking.location_dest_id == rec.location_dest_id):
                    raise ValidationError(_('Destination Location should be same to validate!!!'))
        return super(StockPicking, self).button_validate()


class StockMove(models.Model):
    _inherit = 'stock.move'
    _description = 'Stock Move'

    @api.constrains('location_id', 'location_dest_id')
    def constrains_location_move(self):
        """
        Show warning if transfer having view location
        """
        if self.location_id.usage == "view" or self.location_dest_id.usage == "view":
            raise UserError(_("You Can Not Create Transfer For View Type Location !!!"))
