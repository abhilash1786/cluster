# -*- coding: utf-8 -*-
# Softprime Consulting Pvt Ltd
# Copyright (C) Softprime Consulting Pvt Ltd
# All Rights Reserved
# https://softprimeconsulting.com/
from odoo import api, fields, models, _


class StockMove(models.Model):
    _inherit = 'stock.move'

    int_material_request_line_id = fields.Many2one('internal.material.request.line', copy=False)
    supply_issue_line_id = fields.Many2one('material.issue.line', copy=False)
    is_supply_receive = fields.Boolean(copy=False)
    material_issue_id = fields.Many2one('supply.material.issue', copy=False)
    supply_req_id = fields.Many2one('internal.material.request', copy=False)
    is_material_return = fields.Boolean(copy=False)

    def action_supply_request_validate(self):
        """
        Action Supply request Validate
        """
        if self.sudo().int_material_request_line_id and not self.sudo().is_supply_receive:
            if not self.sudo().is_material_return:
                self.sudo().int_material_request_line_id.transfer_qty += self.quantity_done
                self.sudo().int_material_request_line_id.total_transfer_qty += self.quantity_done

    def _action_done(self, cancel_backorder=False):
        """
        This method is overload to update material_request transfer qty from validated move
        """
        res = super(StockMove, self)._action_done(cancel_backorder=cancel_backorder)
        for stock_move in self:
            stock_move.action_supply_request_validate()
        return res


class StockQuant(models.Model):
    _inherit = 'stock.quant'

    def get_supply_quant_report(self):
        """
        get report
        """
        return {
            'name': _('Inventory Report'),
            'type': 'ir.actions.act_window',
            'view_mode': 'tree',
            'view_id': self.env.ref('supply_material_request.material_transit_stock_quant').id,
            'res_model': 'stock.quant',
            'target': 'current',
            'context': {'create': False, 'edit': False, 'delete': False},
            'domain': [('location_id', 'in', self.env.user.int_trans_loc_ids.ids if
                            self.env.user.int_trans_loc_ids else [])]
        }