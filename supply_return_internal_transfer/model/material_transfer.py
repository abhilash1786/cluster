# -*- coding: utf-8 -*-
# Softprime Consulting Pvt Ltd
# Copyright (C) Softprime Consulting Pvt Ltd
# All Rights Reserved
# https://softprimeconsulting.com/
from odoo.exceptions import UserError
from odoo import api, fields, models, _


class MaterialRequest(models.Model):
    _inherit = 'internal.material.request'

    reason_to_return = fields.Char('Reason To Return', tracking=True)
    received_move_lines = fields.One2many('stock.move', 'material_request_id', string='Received Move IDS')
    return_line_ids = fields.One2many('internal.material.request.line', 'request_id', 'Products to Request')

    def prepare_material_issue_return(self):
        """
        prepare material issue
        """
        source_location_id = self.dest_location_id.id
        if self.is_direct_consume:
            source_location_id = self.direct_dest_location_id.id
        return {
            'name': self.name,
            'dest_location_id': self.source_location_id.id,
            'source_location_id': source_location_id,
            'company_id': self.company_id.id,
            'supply_req_id': self.id,
            'return_request': True,
            'request_by': self.env.user.id,
        }

    def prepare_material_issue_line_return(self):
        """
        prepare material issue line
        """
        record = []
        for rec in self.return_line_ids.filtered(lambda x: x.qty_to_return > 0.0):
            record.append((0, 0, {
                'product_id': rec.product_id.id,
                'uom_id': rec.product_id.uom_id.id,
                'qty_approved': rec.qty_to_return,
                'total_qty': rec.qty_to_return,
                'issue_qty': rec.qty_to_return,
                'onhand_qty': rec.onhand_qty,
                'int_material_request_line_id': rec.id,
            }))
            rec.total_returned += rec.qty_to_return
            rec.qty_to_return = 0.0
        return record

    def create_material_request_return(self):
        """
        Creates internal material request with adding stock picking id and request date in request
        """
        if self.state not in ['received']:
            raise UserError(_('Document already process'))
        issue_line_vals = self.prepare_material_issue_line_return()
        if issue_line_vals:
            issue_vals = self.prepare_material_issue_return()
            if issue_vals:
                issue_vals.update({'material_issue_line': issue_line_vals})
                supply_move = self.env['supply.material.issue'].sudo().create(issue_vals)
                self.supply_issue_ids = [(4, supply_move.id)]
                return supply_move

    def create_return_request_receive(self):
        """
        Create Return Request Receive
        """
        if not self.reason_to_return:
            raise UserError(_('Please Add reason to return before processing.!!!'))
        lines = self.return_line_ids.filtered(lambda x: x.qty_to_return > 0.0)
        if self.state == 'received' and lines:
            return_issue_id = self.create_material_request_return()
            if return_issue_id:
                return_issue_id.material_issue_return()


class MaterialRequestLine(models.Model):
    _inherit = 'internal.material.request.line'

    qty_to_return = fields.Float('Qty to Return')
    total_returned = fields.Float('Total Returned')

    @api.constrains('qty_to_return')
    def constrains_qty_to_returned(self):
        """
        onchange Qty to returned
        """
        for rec in self:
            if rec.qty_to_return > 0.0 and rec.total_returned + rec.qty_to_return > rec.total_received_qty:
                raise UserError(_('One can not assign return qty more than received Qty.!!!'))

    def create_return_request_vals(self, source_location, destination_location, original_move):
        """
        Create Return Request Vals
        """
        vals = {
            'name': 'Return Of ' + self.product_id.name,
            'product_id': self.product_id.id,
            'product_uom_qty': self.qty_to_return,
            'product_uom': self.product_uom_id.id,
            'location_id': destination_location.id,
            'location_dest_id': source_location.id,
            'origin_returned_move_id': original_move.id,
            'int_material_request_line_id': self.id,
            'supply_req_id': self.request_id.id
        }
        return vals


class StockMove(models.Model):
    _inherit = 'stock.move'

    supply_movement_line = fields.Boolean('Supply Movement Record')
    material_request_id = fields.Many2one('internal.material.request', string='Material Request')
    return_qty = fields.Float('Returned Quantity', default=0.0)
