# -*- coding: utf-8 -*-

from odoo.exceptions import UserError

# Softprime Consulting Pvt Ltd
# Copyright (C) Softprime Consulting Pvt Ltd
# All Rights Reserved
# https://softprimeconsulting.com/
from odoo import api, fields, models, _


class NuroConsumption(models.Model):
    _inherit = 'supply.material.consume'

    picking_id = fields.Many2one('stock.picking', string='Return Supply')
    reason_to_return = fields.Char('Reason To Return', tracking=True)
    warehouse_id = fields.Many2one('stock.warehouse', 'Warehouse')
    picking_type_id = fields.Many2one('stock.picking.type', 'Picking Type')

    def return_supply_qty(self):
        """
        :return: supply return quantity
        """
        consume_lines = self.sudo().line_ids.filtered(lambda con_ln: con_ln.qty_to_return > 0.0)
        if not consume_lines:
            raise UserError(_('There is no consume Lines to return.!!!'))
        if not self.reason_to_return:
            raise UserError(_('Please Add Reason to Return.!!!'))
        if not self.consume_location_id.id:
            raise UserError(_('Please select Receipt Location !'))
        picking_search = self.env['stock.picking.type'].search([
            ('code', '=', 'internal'), ('company_id', '=', self.company_id.id),
            ('supply_consume', '=', True)
        ], limit=1)
        if not picking_search:
            raise UserError(_('No Picking to create Return.!!!'))
        self.picking_type_id = picking_search.id
        picking_dict = {
            'picking_type_id': picking_search.id,
            'location_id': self.consume_location_id.id,
            'location_dest_id': self.source_location_id.id,
            'supply_material_consume_id': self.id,
            'origin': self.name,
        }
        internal_transfer = self.env['stock.picking'].create(picking_dict)
        self.picking_id = internal_transfer.id
        internal_transfer.location_id = self.consume_location_id.id
        internal_transfer.location_dest_id = self.source_location_id.id,
        for rec in consume_lines:
            move_id = self.env['stock.move'].create({
                'product_id': rec.product_id.id,
                'product_uom': rec.product_id.uom_id.id,
                'consume_mat_req_line_id': rec.id,
                'product_uom_qty': rec.qty_to_return,
                'location_id': self.consume_location_id.id,
                'location_dest_id': self.source_location_id.id,
                'name': ' Return Supply Request',
                'picking_id': internal_transfer.id
            })
            qty = rec.qty_to_return
            for smvl in rec.stock_move_line_ids.filtered(lambda x: x.total_issued_qty > 0.0):
                if qty > 0.0:
                    asg = qty
                    if smvl.total_issued_qty >= qty:
                        asg = qty
                    if smvl.total_issued_qty <= qty:
                        asg = smvl.total_issued_qty
                    self.env['stock.move.line'].sudo().create({
                        'product_id': rec.product_id.id,
                        'location_id': self.consume_location_id.id,
                        'location_dest_id': self.source_location_id.id,
                        'lot_id': smvl.lot_id and smvl.lot_id.id or False,
                        'lot_name': smvl.lot_id and smvl.lot_id.name or False,
                        'qty_done': asg,
                        'product_uom_id': rec.product_id.uom_id.id,
                        'picking_id': internal_transfer.id,
                        'move_id': move_id.id,
                        'origin': self.name,
                    })
                    qty = qty - asg
                    smvl.total_issued_qty = smvl.total_issued_qty - asg
        internal_transfer.sudo().action_confirm()
        ctx = {'acc_dest': self.consume_location_id.valuation_in_account_id.id}
        internal_transfer.sudo().with_context(ctx).button_validate()
        for line_details in self.line_ids:
            line_details.returned_qty += line_details.qty_to_return
            line_details.qty_to_return = 0.0


class NuroConsumptionLine(models.Model):
    _inherit = 'supply.material.consume.line'

    qty_to_return = fields.Float(string='Qty Return')
    returned_qty = fields.Float(string='Returned Qty')

    @api.constrains('qty_to_return')
    def return_quantity(self):
        """
        return to quantity
        """
        for rec in self:
            if rec.qty_to_return > 0.0:
                if rec.qty_to_return + rec.returned_qty > rec.product_qty:
                    raise UserError(_('Return Quantity Can Not Greater Then Done Qty?'))
