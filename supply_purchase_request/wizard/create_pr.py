# -*- coding: utf-8 -*-
# Softprime Consulting Pvt Ltd
# Copyright (C) Softprime Consulting Pvt Ltd
# All Rights Reserved
# https://softprimeconsulting.com/
from odoo import fields, models, api, _, Command
from odoo.exceptions import UserError


class SupplyPR(models.TransientModel):
    _name = 'supply.line.pr.wz'
    _description = 'Create PR Supply'

    company_id = fields.Many2one('res.company', 'Company', required=True,
                                 default=lambda self: self.env.company)
    product_line = fields.One2many('product.pr.wz.line', 'pr_wz_id')

    @api.model
    def default_get(self, fields):
        res = super(SupplyPR, self).default_get(fields)
        line_ids = self.env['internal.material.request.line'].search([
            ('id', '=', self._context.get('active_ids')),
            ('state', '=', 'requested'), ('product_qty', '>', 0.0)])
        prod_dict = {}
        if line_ids:
            if not all(line.company_id == self.env.company for line in line_ids):
                raise UserError(_('All Selected Record Should Be %s ' % (self.env.company.name)))
            for line in line_ids:
                prod_dict[line.product_id] = prod_dict.get(line.product_id, []) + [line]
            line_list = []
            for key, value in prod_dict.items():
                qty = 0
                ref = ''
                req_id = False
                for line in value:
                    qty += line.product_qty
                    ref = line.request_id.name
                    req_id = line.request_id.id
                line_list.append(Command.create({
                        'product_id': key.id,
                        'quantity': qty,
                        'uom_id': key.uom_id.id,
                        'ref': ref,
                        'request_id': req_id
                    }))
            if line_list:
                res['product_line'] = line_list
        return res

    def prepare_pr_line(self, line):
        """
        return PR line
        """
        return {
            'product_id': line.product_id.id,
            'name': line.ref,
            'product_qty': line.quantity,
            'company_id': self.env.company.id,
            'product_uom_id': line.product_id.uom_id.id
        }

    def prepare_pr_vals(self):
        """
        prepare PR vals
        """
        return {
            'date_start': fields.Date.context_today(self),
            'company_id': self.env.company.id,
            'is_supply_req_create': True,
            'description': ' '.join([ref for ref in self.product_line.mapped('ref') if ref])
        }

    def create_supply_pr(self):
        """
        create supply PR
        """
        if self.product_line:
            pr_vals = self.prepare_pr_vals()
            pr_list = []
            for line in self.product_line.filtered(lambda pl: pl.quantity > 0.0):
                pr_list.append(Command.create(self.prepare_pr_line(line=line)))
            if pr_list:
                pr_vals.update({'line_ids': pr_list})
                self.env['sp.purchase.request'].sudo().create(pr_vals)


class WzLine(models.TransientModel):
    _name = 'product.pr.wz.line'
    _description = 'Wz Line'

    product_id = fields.Many2one('product.product', 'Product')
    quantity = fields.Float('Quantity')
    uom_id = fields.Many2one('uom.uom', 'UOM')
    pr_wz_id = fields.Many2one('supply.line.pr.wz')
    ref = fields.Char('Ref')
    request_id = fields.Many2one('internal.material.request')
