# -*- coding: utf-8 -*-
# Copyright  Softprime consulting Pvt Ltd
from datetime import datetime
from odoo.exceptions import UserError
from odoo.tools.float_utils import float_is_zero
from odoo import fields, models, api, _

SPLIT_METHOD = [
    ('equal', 'Equal'),
    ('by_quantity', 'By Quantity'),
    ('by_current_cost_price', 'By Current Cost'),
    ('by_weight', 'By Weight'),
    ('by_volume', 'By Volume'),
]


class LandedCost(models.Model):
    _inherit = 'stock.landed.cost'

    def _default_account_journal_id(self):
        """
        Take the journal configured in the company, else fallback on the stock journal.
        :return:
        """
        lc_journal = self.env['account.journal']
        if self.env.company.lc_journal_id:
            lc_journal = self.env.company.lc_journal_id
        return lc_journal

    account_journal_id = fields.Many2one('account.journal', 'Account Journal', required=True,
                                         states={'done': [('readonly', True)]},
                                         domain=[('type', '=', 'general')],
                                         default=lambda self: self._default_account_journal_id())
    po_ids = fields.Many2many('purchase.order', 'landed_cost_id', 'po_id', string='PO Name')
    po_picking_ids = fields.Many2many('stock.picking', 'landed_cost_picking_id', 'po_picking_id',
                                      string='Noted Transfers')
    holding_account_move_id = fields.Many2one('account.move', string='Transit Journal Entry')
    approve_person = fields.Boolean('Approve Person', compute='compute_approve_person')
    approve_by_id = fields.Many2one('res.users', string='Approve By')
    state = fields.Selection([
        ('draft', 'Draft'),
        ('waiting_approval', 'Waiting Approval'),
        ('approved', 'Approved'),
        ('transit', 'Transit'),
        ('done', 'Posted'),
        ('cancel', 'Cancelled')], 'State', default='draft',
        copy=False, readonly=True, tracking=True)
    transit_po_lines = fields.One2many('transit.po.product.list', 'landed_cost_id', string='Transit PO Lines')

    def unlink(self):
        """
        Unlink
        :return:
        """
        res = super(LandedCost, self).unlink()
        if res:
            raise UserError(_('You are not allowed to Delete the Delete.!!!'))
        return res

    def unlink_method(self):
        for rec in self.stock_valuation_layer_ids:
            rec.sudo().unlink()

    def approve_landed_cost(self):
        """
        This method update status to approved
        :return:
        """
        if self.state != 'waiting_approval':
            raise UserError(_('Document Has been processed already.!!!'))
        self.state = 'approved'

    def compute_approve_person(self):
        """
        Get the approve Person
        :return:
        """
        self.ensure_one()
        for rec in self:
            if self.env.user.id == rec.approve_by_id.id:
                rec.approve_person = True
            else:
                rec.approve_person = False

    def transit_po_line_vals(self, po_line, value):
        """
        return vals
        """
        if po_line:
            return {
                'product_id': po_line.product_id.id,
                'company_id': self.env.user.company_id.id,
                'product_qty': po_line.product_qty,
                'price_subtotal': po_line.price_subtotal,
                'landed_cost_id': self.id,
                'landed_cost_value': round(value, 2),
                'total_value': po_line.price_subtotal + value,
                'average_value': (po_line.price_subtotal + value) / po_line.product_qty
            }

    def compute_cost_lines_po(self):
        """
        Onchange Cost Line and PO ID
        :return:
        """
        if self.state not in ('draft', 'transit', 'waiting_approval'):
            raise UserError(_('You Can Not Perform Calculation if Record not in Draft or Transit State.!!!'))
        if not self.picking_ids and not self.cost_lines:
            raise UserError(_('Please Select Picking for before processing it.!!!!'))
        transit_po_product_list = self.env['transit.po.product.list']
        self.transit_po_lines = False
        if self.picking_ids and self.cost_lines:
            cost_without_adjustment_lines = self.filtered(lambda c: not c.valuation_adjustment_lines)
            if cost_without_adjustment_lines:
                cost_without_adjustment_lines.compute_landed_cost()
        for po in self.po_ids:
            for po_line in po.order_line:
                value = 0.0
                product_lines = self.valuation_adjustment_lines.filtered(
                    lambda c: c.product_id.id == po_line.product_id.id)
                search_transit_product = transit_po_product_list.search([
                    ('product_id', '=', po_line.product_id.id),
                    ('landed_cost_id', '=', self.id)
                ])
                for pr in product_lines:
                    value += pr.additional_landed_cost
                if not search_transit_product:
                    vals = self.transit_po_line_vals(po_line=po_line, value=value)
                    transit_po_product_list.create(vals)
                else:
                    product_qty = search_transit_product.product_qty + po_line.product_qty
                    price_subtotal = search_transit_product.price_subtotal + po_line.price_subtotal
                    total_value = search_transit_product.total_value + po_line.price_subtotal
                    average_value = total_value / product_qty
                    search_transit_product.write({
                        'product_qty': product_qty,
                        'price_subtotal': price_subtotal,
                        'total_value': total_value,
                        'average_value': average_value
                    })
        self.valuation_adjustment_lines = False

    def _create_debit_move_line_vals(self, partner_id, account_id, debit):
        """
        Debit Line Dictionary for the account move line
        :param partner_id:
        :return:
        """
        # debit = sum(self.cost_lines.filtered(lambda x: x.payment_by == 'cash').mapped('price_unit'))
        debit = debit
        credit = 0.0
        if debit > 0.0:
            debit_vals = {
                'name': self.name,
                'debit': abs(debit),
                'credit': abs(credit),
                'partner_id': partner_id.id,
                'account_id': account_id.id,
                'company_id': self.env.user.company_id.id,
                'date': datetime.now().date()
            }
            return debit_vals

    def _create_account_move_dict(self, journal_id, line_ids):
        """
        Creating Journal Entry for hospital Expense
        :param journal_id:
        :param line_ids:
        :return:
        """
        vals = {
            'move_type': 'entry',
            'journal_id': journal_id.id,
            'date': datetime.now().date(),
            'ref': self.name,
            'state': 'draft',
            'company_id': self.env.user.company_id.id,
            'line_ids': line_ids
        }
        return vals

    def send_for_approval(self):
        '''
        This method send landed cost for approval and approval group can confirm it
        :return:
        '''
        self.state = 'waiting_approval'

    def create_vendor_bill_and_line_ids(self, partner_id, line_ids):
        """
        Create vendor bill and line ids
        :param partner_id:
        :param line_ids:
        :return:
        """
        invoice = self.env['account.move']
        vendor_bill = invoice.create({
            'partner_id': partner_id.id,
            'ref': self.name + '-' + str(self.env.context.get('number')),
            'invoice_line_ids': [],
            'move_type': 'in_invoice',
            'company_id': self.env.user.company_id.id,
            'invoice_origin': self.name,
            'invoice_date': self.date,
        })
        vendor_bill.update({'invoice_line_ids': line_ids})
        vendor_bill.action_post()
        self.landed_cost_vendor_ids = [(4, vendor_bill.id)]
        return vendor_bill

    def confirm_landed_cost(self):
        """
        Confirm Landed Cost
        :return:
        """
        if self.state != 'approved':
            raise UserError(_('Document has been processed already.!!!'))
        self.state = 'transit'
        account_move_obj = self.env['account.move']
        line_ids = []
        for rec in self:
            total_debit_po_value = sum(self.po_ids.mapped('amount_total'))
            total_debit_cash = sum(self.cost_lines.filtered(lambda x: x.payment_by == 'cash').mapped('price_unit'))
            debit_account_id = self.env.company.holding_account_id
            for po_debit in self.po_ids:
                if total_debit_po_value > 0:
                    debit_amount = (po_debit.amount_total / total_debit_po_value) * total_debit_cash
                else:
                    debit_amount = 0
                debit_line = rec._create_debit_move_line_vals(
                    partner_id=po_debit.partner_id, account_id=debit_account_id, debit=debit_amount)
                if debit_line:
                    line_ids.append((0, 0, debit_line))
            vendor_ids = []
            for line in self.cost_lines:
                if line.payment_by == 'cash':
                    total_credit_po_value = sum(self.po_ids.mapped('amount_total'))
                    total_credit_cash = line.price_unit
                    for po_credit in self.po_ids:
                        credit_amount = (po_credit.amount_total / total_credit_po_value) * total_credit_cash
                        credit_line = line._create_credit_move_line_vals(partner_id=po_credit.partner_id,
                                                                         credit=credit_amount,
                                                                         account_id=line.journal_id.default_account_id.id)
                        line_ids.append((0, 0, credit_line))
                if line.payment_by == 'credit':
                    line.create_landed_cost_vendor_bill()
                    vendor_ids.append(line.vendor_id.id)
            vendor_unique_ids = set(vendor_ids)
            vendor_list_ids = self.env['res.partner'].search([('id', 'in', list(vendor_unique_ids))])
            # for update number in ref
            count = 0
            for vendor in vendor_list_ids:
                count += 1
                vendor_line_ids = self.cost_lines.filtered(
                    lambda x: x.payment_by == 'credit' and x.vendor_id.id == vendor.id)
                vendor_line_list = []
                for vendor_line in vendor_line_ids:
                    line_dict = vendor_line.create_landed_cost_vendor_bill()
                    vendor_line_list.append((0, 0, line_dict))
                if vendor_line_list:
                    vendor_bill_id = self.with_context(number=count).create_vendor_bill_and_line_ids(partner_id=vendor,
                                                                                                     line_ids=vendor_line_list)

                    for new_vendor in vendor_list_ids:
                        new_vendor.vendor_bill_id = vendor_bill_id.id
            if line_ids:
                move = rec._create_account_move_dict(
                    journal_id=self.account_journal_id, line_ids=[])
                move_ids = account_move_obj.create(move)
                move_ids.update({'line_ids': line_ids})
                move_ids.post()
                self.holding_account_move_id = move_ids.id

    def prepare_svl_vals(self, cost, line, linked_layer, cost_to_add):
        """
        prepare stock valuation
        """
        return {
            'value': cost_to_add,
            'unit_cost': 0,
            'quantity': 0,
            'remaining_qty': 0,
            'stock_valuation_layer_id': linked_layer.id,
            'description': cost.name,
            'stock_move_id': line.move_id.id,
            'product_id': line.move_id.product_id.id,
            'stock_landed_cost_id': cost.id,
            'company_id': cost.company_id.id,
        }

    def prepare_landed_cost_move(self, cost):
        """
        prepare landed cost move values
        """
        if cost:
            return {
                'journal_id': cost.account_journal_id.id,
                'date': cost.date,
                'ref': cost.name,
                'line_ids': [],
                'move_type': 'entry',
                'company_id': self.env.user.company_id.id,
            }

    def button_validate(self):
        line_ids = []
        if self.state != 'transit':
            raise UserError(_('Document has been processed already.!!!'))
        # todo need tio check why this function is overwritten here
        if not self.transit_po_lines:
            raise UserError(_('Please Calculate the PO Lines Before Validation.!!!'))
        if not all(cost.picking_ids for cost in self):
            raise UserError(_('Please define the transfers on which those additional costs should apply.'))
        cost_without_adjusment_lines = self.filtered(lambda c: not c.valuation_adjustment_lines)
        if cost_without_adjusment_lines:
            cost_without_adjusment_lines.compute_landed_cost()
        if not self._check_sum():
            raise UserError(_('Cost and adjustments lines do not match. You should maybe recompute the landed costs.'))
        for cost in self:
            move = self.env['account.move']
            move_vals = self.prepare_landed_cost_move(cost=cost)
            valuation_layer_ids = []
            for line in cost.valuation_adjustment_lines.filtered(lambda line: line.move_id):
                remaining_qty = sum(line.move_id.stock_valuation_layer_ids.mapped('quantity'))
                linked_layer = line.move_id.stock_valuation_layer_ids[:1]

                # Prorate the value at what's still in stock
                cost_to_add = (remaining_qty / line.move_id.product_qty) * line.additional_landed_cost
                if not cost.company_id.currency_id.is_zero(cost_to_add):
                    svl_vals = self.prepare_svl_vals(cost=cost, line=line, linked_layer=linked_layer,
                                                     cost_to_add=cost_to_add)
                    valuation_layer = self.env['stock.valuation.layer'].create(svl_vals)
                    linked_layer.remaining_value += cost_to_add
                    valuation_layer_ids.append(valuation_layer.id)
                # Update the AVCO
                product = line.move_id.product_id
                if product.cost_method == 'average' and not float_is_zero(product.quantity_svl,
                                                                          precision_rounding=product.uom_id.rounding):
                    product.with_context(
                        force_company=self.company_id.id).sudo().standard_price += cost_to_add / product.quantity_svl
                # `remaining_qty` is negative if the move is out and delivered products that were not
                # in stock.
                qty_out = 0
                if line.move_id._is_in():
                    qty_out = line.move_id.product_qty - remaining_qty
                elif line.move_id._is_out():
                    qty_out = line.move_id.product_qty
                line_ids += line._create_accounting_entries(move, qty_out)
            move_vals['stock_valuation_layer_ids'] = [(6, None, valuation_layer_ids)]
            move = move.create(move_vals)
            move.update({'line_ids': line_ids})
            cost.write({'state': 'done', 'account_move_id': move.id})
            move.post()
            if cost.vendor_bill_id and cost.vendor_bill_id.state == 'posted' and cost.company_id.anglo_saxon_accounting:
                all_amls = cost.vendor_bill_id.line_ids | cost.account_move_id.line_ids
                for product in cost.cost_lines.product_id:
                    accounts = product.product_tmpl_id.get_product_accounts()
                    input_account = accounts['stock_input']
                    all_amls.filtered(
                        lambda aml: aml.account_id == input_account and not aml.full_reconcile_id).reconcile()
        return True


# noinspection PyAttributeOutsideInit
class StockLandedCostLines(models.Model):
    _inherit = 'stock.landed.cost.lines'

    journal_id = fields.Many2one('account.journal', string='Journal', domain=[('type', 'in', ('bank', 'cash'))])
    payment_by = fields.Selection([('cash', 'Cash/Bank'), ('credit', 'credit')], string='Pay By')
    split_method = fields.Selection(SPLIT_METHOD, string='Split Method', default='by_current_cost_price', required=True)

    @api.onchange('product_id')
    def onchange_product_id(self):
        res = super(StockLandedCostLines, self).onchange_product_id()
        account_id = self.env.company.holding_account_id
        if not account_id:
            message = '''Please Configure the Holding Account Information'''
            return {'warning': {'title': 'Holding Account Not Configured', "message": message}}
        self.account_id = account_id.id
        return res

    def _create_credit_move_line_vals(self, partner_id, credit, account_id):
        """
        Credit Line Dictionary for the account move line
        :param partner_id:
        :return:
        """
        debit = 0.0
        credit = credit
        credit_vals = {
            'name': self.cost_id.name,
            'debit': abs(debit),
            'credit': abs(credit),
            'partner_id': partner_id.id,
            'account_id': account_id,
            'company_id': self.env.user.company_id.id,
            'date': datetime.now().date()
        }
        return credit_vals

    def create_landed_cost_vendor_bill(self):
        """
        Create Vendor Bill Lines
        :return:
        """
        debit_account_id = self.env.company.holding_account_id
        vendor_bill_line_ids = {
            'product_id': self.product_id.id,
            'name': self.product_id.name,
            'account_id': debit_account_id.id,
            'price_unit': self.price_unit
        }
        return vendor_bill_line_ids


class TransitPOProductList(models.Model):
    _name = 'transit.po.product.list'
    _description = 'Transit PO Product List'
    _order = 'id DESC'

    landed_cost_id = fields.Many2one('stock.landed.cost', string='Landed Cost ID')
    product_id = fields.Many2one('product.product', string='Product')
    product_qty = fields.Float('Quantity')
    price_subtotal = fields.Float('PO Value')
    landed_cost_value = fields.Float('Landed Cost Value')
    total_value = fields.Float('Total Value')
    average_value = fields.Float('Average Value')
    company_id = fields.Many2one('res.company', default=lambda self: self.env.user.company_id)
