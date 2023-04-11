# -*- coding: utf-8 -*-

# Softprime Consulting Pvt Ltd
# Copyright (C) Softprime Consulting Pvt Ltd
# All Rights Reserved
# https://softprimeconsulting.com/
from odoo import api, fields, models, _
from odoo.exceptions import UserError, Warning, ValidationError


class MaterialRequestIssue(models.Model):
    _inherit = 'supply.material.issue'

    return_request = fields.Boolean('Return Request')
    state = fields.Selection(selection_add=[('return_received', 'Return Received')])

    def direct_consume_return(self):
        """
        Material Direct Consume Return
        """
        quant_obj = self.env['stock.quant']
        if self.material_issue_line and self.source_location_id and self.dest_location_id:
            for line in self.material_issue_line.filtered(lambda line: line.issue_qty > 0.0):
                available_qty = quant_obj._get_available_quantity(product_id=line.product_id,
                                                                  location_id=self.source_location_id,
                                                                  strict=False)
                if not available_qty:
                    raise UserError(_('%s product not have enough qty for issue' % (line.product_id.name)))
                move_vals = line.prep_stock_move_vals(location_id=self.source_location_id,
                                                      name=_('Supply request move for %s' % (self.name)),
                                                      dest_loac_id=self.sudo().supply_req_id.company_id.supply_transit_loc)
                move_vals.update({
                    'is_material_return': True
                })
                if move_vals:
                    move_id = self.env['stock.move'].create(move_vals)
                    move_id._action_confirm()
                    move_id._action_assign()
                    for mv_ln in move_id.move_line_ids:
                        mv_ln.unlink()
                    qty = line.qty_approved
                    for smvl in line.int_material_request_line_id.stock_move_line_ids.filtered(lambda x: x.total_issued_qty > 0.0):
                        if qty > 0.0:
                            asg = qty
                            if smvl.total_issued_qty >= qty:
                                asg = qty
                            if smvl.total_issued_qty <= qty:
                                asg = smvl.total_issued_qty
                            self.env['stock.move.line'].sudo().create({
                                'product_id': line.product_id.id,
                                'location_id': move_id.location_id.id,
                                'location_dest_id': move_id.location_dest_id.id,
                                'lot_id': smvl.lot_id and smvl.lot_id.id or False,
                                'lot_name': smvl.lot_id and smvl.lot_id.name or False,
                                'qty_done': asg,
                                'product_uom_id': line.product_id.uom_id.id,
                                'move_id': move_id.id,
                                'origin': move_id.name,
                            })
                            qty = qty - asg
                            smvl.total_issued_qty = smvl.total_issued_qty - asg
                    ctx = {'acc_dest': self.source_location_id.valuation_in_account_id.id}
                    move_id.with_context(ctx)._action_done()
                    line.source_transit_move = move_id.id
                    self.supply_issue_move_ids = [(4, move_id.id)]
                    self.sudo().supply_req_id.supply_req_move_ids = [(4, move_id.id)]
                    line.total_issue_qty += line.issue_qty
                confirm_move_vals = line.prep_stock_move_vals(dest_loac_id=self.dest_location_id,
                                                              name=_('Supply request move for %s' % (self.name)),
                                                              location_id=self.sudo().supply_req_id.company_id.supply_transit_loc)
                confirm_move_vals.update({
                    'is_material_return': True
                })
                if confirm_move_vals:
                    if confirm_move_vals:
                        second_move_id = self.env['stock.move'].create(confirm_move_vals)
                        second_move_id._action_confirm()
                        second_move_id._action_assign()
                        for sec_mv_ln in second_move_id.move_line_ids:
                            sec_mv_ln.unlink()
                        qty = line.qty_approved
                        for smvl in line.int_material_request_line_id.stock_move_line_ids.filtered(
                                lambda x: x.sec_total_issued_qty > 0.0):
                            if qty > 0.0:
                                asg = qty
                                if smvl.sec_total_issued_qty >= qty:
                                    asg = qty
                                if smvl.sec_total_issued_qty <= qty:
                                    asg = smvl.sec_total_issued_qty
                                self.env['stock.move.line'].sudo().create({
                                    'product_id': line.product_id.id,
                                    'location_id': second_move_id.location_id.id,
                                    'location_dest_id': second_move_id.location_dest_id.id,
                                    'lot_id': smvl.lot_id and smvl.lot_id.id or False,
                                    'lot_name': smvl.lot_id and smvl.lot_id.name or False,
                                    'qty_done': asg,
                                    'product_uom_id': line.product_id.uom_id.id,
                                    'move_id': second_move_id.id,
                                    'origin': second_move_id.name,
                                })
                                qty = qty - asg
                                smvl.sec_total_issued_qty = smvl.sec_total_issued_qty - asg
                        second_move_id._action_confirm()
                        second_move_id.state = 'assigned'
                        line.transit_dest_move = second_move_id.id
                        line.sudo().int_material_request_line_id.transit_stock_move_id = second_move_id.id
                        self.supply_issue_move_ids = [(4, second_move_id.id)]
                        self.sudo().supply_req_id.supply_req_move_ids = [(4, second_move_id.id)]
                line.issue_qty = 0.0
        self.issued_by = self.env.user.id
        if all(line.qty_approved == line.total_issue_qty for line in self.material_issue_line):
            self.state = 'draft'

    def material_issue_return(self):
        """
        material issue and create stock move and link with material line
        """
        if self.state not in ['draft', 'partial_issue']:
            raise UserError(_('Document already process'))
        if all(line.issue_qty == 0.0 for line in self.material_issue_line):
            raise UserError(_('fill issue qty in request line'))
        if not self.sudo().supply_req_id.company_id.supply_transit_loc:
            raise UserError(_('Configure supply transit location'))
        self.direct_consume_return()

    def action_receive_all_qty(self):
        """
        receive all quantity
        """
        for line in self.supply_issue_move_ids.filtered(lambda line: line.state == 'assigned'):
            line.sudo()._action_done()
        if all(line.state == 'done' for line in self.supply_issue_move_ids):
            self.state = 'return_received'
