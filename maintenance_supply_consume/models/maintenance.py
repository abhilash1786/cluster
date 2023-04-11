# -*- coding: utf-8 -*-
# Softprime Consulting Pvt Ltd
# Copyright (C) Softprime Consulting Pvt Ltd
# All Rights Reserved
# https://softprimeconsulting.com/
from odoo import models, fields, api, _, Command
from odoo.exceptions import UserError


class Maintenance(models.Model):
    _inherit = 'maintenance.request'

    consume_id = fields.Many2one('supply.material.consume', copy=False)

    def maintenance_supply_vals(self, line):
        """
        prepare maintenance supply vals
        """
        return {
            'maintenance_id': self.id,
            'consumed_by': self.env.user.id,
            'source_location_id': self.consume_src_location_id.id,
            'consume_location_id': self.consume_dest_location_id.id,
            'line_ids': line
        }

    def create_maintenance_supply_consumption(self):
        """
        create supply consumption from maintenance
        """
        line_list = []
        if self.consume_product_ids:
            for line in self.consume_product_ids:
                line_list.append(Command.create(line.prepare_product_supply_vals()))
            if line_list:
                vals = self.maintenance_supply_vals(line=line_list)
                consume_id = self.env['supply.material.consume'].create(vals)
                if consume_id:
                    self.consume_id = consume_id.id

    def _get_default_source_location(self):
        """
        Get Default internal location assigned to user
        """
        location = self.env.user.int_trans_loc_ids.ids
        if len(location) == 1:
            return location[0]
        else:
            return False

    def _get_default_consume_location(self):
        """
        Get Default consume location assigned to user
        """
        location = self.env['stock.location'].search([('maintenance_consume', '=', True),
                                                      ('company_id', '=', self.company_id.id)])

        if len(location) == 1:
            return location[0]
        else:
            return False

    consume_src_location_id = fields.Many2one('stock.location', 'Source Location', copy=False)
    consume_dest_location_id = fields.Many2one('stock.location', 'Destination Location', copy=False,
                                               domain=lambda self: [
                                                   ('maintenance_consume', '=', True)],
                                               default=_get_default_consume_location
                                               )
    consume_product_ids = fields.One2many('maintenance.consume.line', 'maintenance_id', copy=False)
    consume_line_product_ids = fields.Many2many('product.product', 'product_consume_maintenance_rel', 'maintenance_id',
                                                'product_id', string='Product IDS',
                                                compute='_get_supply_line_product_ids')
    available_product_ids = fields.Many2many('product.product', 'product_consume_maintenance_ref', 'maintenance_id',
                                             'product_id')
    get_current_user_id = fields.Many2one('res.users', compute='_compute_get_current_user')
    allowed_location_ids = fields.Many2many('stock.location',
                                            'consume_maintenance_location_ref',
                                            'maintenance_id', 'location_id',
                                            copy=False)

    def _compute_get_current_user(self):
        """get current user"""
        for record in self:
            record.get_current_user_id = record.env.user.id
            if record.env.user.int_trans_loc_ids:
                record.allowed_location_ids = [
                    (6, 0, record.env.user.int_trans_loc_ids.ids)]

    def action_repaired(self):
        """
        inherit for create supply consume
        """
        res = super().action_repaired()
        if self.maintenance_by and self.maintenance_by == 'internal':
            if not self.consume_id:
                self.create_maintenance_supply_consumption()
        return res

    def action_open_consume(self):
        """
        open supply consumption
        """
        return {
            'name': _('Supply Consume'),
            'res_model': 'supply.material.consume',
            'view_mode': 'tree,form',
            'domain': [('id', '=', self.consume_id.id)],
            'target': 'current',
            'context': {'create': False, 'edit': False},
            'type': 'ir.actions.act_window',
        }

    @api.depends('consume_product_ids')
    def _get_supply_line_product_ids(self):
        """
        Get Supply Lines Product IDS
        """
        for rec in self:
            product_ids = rec.consume_product_ids.mapped('product_id').ids
            rec.consume_line_product_ids = [(6, 0, product_ids)]

    @api.onchange('consume_src_location_id')
    def onchange_source_product(self):
        """
        compute supply avl product
        """
        product_lst = []
        quant_obj = self.env['stock.quant']
        self.available_product_ids = False
        if self.state == 'draft':
            self.consume_product_ids = False
        if self.consume_src_location_id:
            products = self.env['product.product'].search([('type', '=', 'product'),
                                                           ('qty_available', '>', 0.0),
                                                           '|', ('company_id', '=', self.company_id.id),
                                                           ('company_id', '=', False)])
            if products:
                for prod in products:
                    available_qty = quant_obj._get_available_quantity(product_id=prod,
                                                                      location_id=self.consume_src_location_id,
                                                                      strict=True)
                    if available_qty:
                        product_lst.append(prod.id)
                self.available_product_ids = [(6, 0, product_lst)]


class MaintenanceLine(models.Model):
    _name = 'maintenance.consume.line'
    _description = "Supply Material Consume"

    maintenance_id = fields.Many2one('maintenance.request')
    product_id = fields.Many2one('product.product', 'Product', tracking=True)
    name = fields.Char('Description', size=256, tracking=True)
    product_uom_id = fields.Many2one('uom.uom', 'Product Unit of Measure', tracking=True)
    product_qty = fields.Float('Consume Quantity', tracking=True)
    company_id = fields.Many2one('res.company', 'Company', required=True, default=lambda self: self.env.company.id)
    onhand_qty = fields.Float('Onhand Qty', compute='_get_available_product_qty', store=True)
    qty_damage = fields.Float('Damage Qty')
    product_uom_category_id = fields.Many2one(related='product_id.uom_id.category_id', readonly=True)

    def prepare_product_supply_vals(self):
        """
        product supply line vals
        """
        return {
            'product_id': self.product_id.id,
            'name': self.product_id.name,
            'product_qty': self.product_qty,
            'qty_damage': self.qty_damage,
            'product_uom_id': self.product_uom_id.id,
        }

    @api.constrains('onhand_qty', 'product_qty', 'qty_damage')
    def constrains_qty_available_product_qty(self):
        """
        Check Quantity Available Quantity and
        product quantity and if available quantity is less than Qty than restrictions
        """
        for rec in self:
            if (rec.product_qty + rec.qty_damage) > rec.onhand_qty:
                raise UserError(_("Available Quantity for %s is less than requested quantity") % rec.product_id.name)

    @api.constrains('product_qty', 'qty_damage', 'onhand_qty')
    def check_negetive_qty(self):
        """
        Constrains for negative product quantity
        """
        for product in self:
            if product.product_qty <= 0:
                raise UserError(_("Quantity can't be less than or equal to 0!!!"))
            if product.qty_damage < 0:
                raise UserError(_("Damage Qty can't be less than 0!!!"))
            if product.onhand_qty < product.product_qty + product.qty_damage:
                raise UserError(
                    _('%s product (qty + damage qty) should not greater than On hand Qty' % (product.product_id.name)))

    @api.depends('product_id')
    def _get_available_product_qty(self):
        """
        Method to get available product qty
        :return:
        """
        for rec in self:
            if rec.product_id and rec.maintenance_id.consume_src_location_id:
                query = """
                                select 
                                sum(quant.quantity - quant.reserved_quantity) 
                                from stock_quant as quant
                                left join stock_location as sl on (quant.location_id = sl.id)
                                where 
                                sl.usage = 'internal' 
                                and quant.location_id = %s
                                and quant.product_id = %s
                                """ % (rec.maintenance_id.consume_src_location_id.id, rec.product_id.id)
                self.env.cr.execute(query)
                result = self.env.cr.fetchone()
                rec.onhand_qty = result and result[0] or 0.0
            else:
                rec.onhand_qty = 0.0

    @api.onchange('product_id')
    def onchange_product_id(self):
        """
        Onchange for product name in pop up list, uom and default qty
        """
        if self.product_id:
            name = self.product_id.name
            if self.product_id.code:
                name = '[%s] %s' % (name, self.product_id.code)
            if self.product_id.description_purchase:
                name += '\n' + self.product_id.description_purchase
            self.product_uom_id = self.product_id.uom_id.id
            self.product_qty = 1
            self.name = name
