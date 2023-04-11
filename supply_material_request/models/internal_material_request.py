# -*- coding: utf-8 -*-
# Softprime Consulting Pvt Ltd
# Copyright (C) Softprime Consulting Pvt Ltd
# All Rights Reserved
# https://softprimeconsulting.com/
# -*- coding: utf-8 -*-
import logging

from odoo.exceptions import UserError, ValidationError

from odoo import api, fields, models, _

_logger = logging.getLogger(__name__)

_STATES = [
    ('draft', 'Draft'),
    ('to_approve', 'To be approved'),
    ('approved', 'Approved'),
    ('rejected', 'Rejected'),
    ('partial_receive', 'Partial Receive'),
    ('issued', 'Issued'),
    ('received', 'Received'),
    ('requested', 'Requested'),
    ('return_requested', 'Return Requested'),
    ('return_received', 'Return Received')
]


class InternalMaterialRequest(models.Model):
    _name = 'internal.material.request'
    _description = 'Internal Material Request'
    _inherit = ['mail.thread']
    _order = 'name desc'

    @api.depends('state')
    def _compute_is_editable(self):
        """
        Compute field for editable or not editable state
        """
        for rec in self:
            if rec.state in ('to_approve', 'approved', 'rejected', 'requested', 'received'):
                rec.is_editable = False
            else:
                rec.is_editable = True

    def _get_default_location(self):
        """
        Get Default Location assigned to user
        """
        location = self.env.user.int_trans_loc_ids.ids
        if len(location) == 1:
            return location[0]
        else:
            return False

    def _get_default_source_location(self):
        """
        Get Default Location assigned to user
        """
        location = self.env.user.source_trans_location.ids
        if len(location) == 1:
            return location[0]
        else:
            return False
        # return False

    def _get_default_warehouse(self):
        """
        Get Default Warehouse
        """
        warehouse = self.env['stock.warehouse'].search([])
        if len(warehouse) == 1:
            return warehouse[0]
        else:
            return False

    @api.model
    def create(self, vals):
        """
        Validated for empty request lines, not same locations, same approver
        """
        supply = super(InternalMaterialRequest, self).create(vals)
        supply.name = supply.env['ir.sequence'].next_by_code('internal.material.request')
        self.clear_caches()
        return supply

    @api.constrains('source_location_id', 'dest_location_id', 'line_ids')
    def supply_request_validation(self):
        """
        all supply restriction
        """
        for supply in self:
            if supply.source_location_id == supply.dest_location_id:
                raise UserError(_('Source and destination location can not be same'))
            if not supply.line_ids:
                raise UserError(_('Supply request can not have empty product lines'))
            if not supply.company_id.supply_transit_loc:
                raise UserError(_('Please Configure supply transit location'))

    name = fields.Char('Request Reference', size=32, tracking=True)
    origin = fields.Char('Source Document', size=32)
    date_start = fields.Date('Creation date', help="Date when the user initiated the request.", tracking=True,
                             default=fields.Date.context_today)
    requested_by = fields.Many2one('res.users', 'Requested by', required=True, readonly=1, tracking=True,
                                   default=lambda self: self.env.user.id)
    company_id = fields.Many2one('res.company', 'Company', required=True, default=lambda self: self.env.company.id,
                                 tracking=True)
    line_ids = fields.One2many('internal.material.request.line', 'request_id', 'Products to Purchase', readonly=False,
                               copy=True, tracking=True)
    state = fields.Selection(selection=_STATES, string='Status', index=True, tracking=True, required=True, copy=False,
                             default='draft')
    is_editable = fields.Boolean(string="Is editable", compute="_compute_is_editable", readonly=True)
    warehouse_id = fields.Many2one('stock.warehouse', 'Warehouse', default=_get_default_warehouse,
                                   domain=[('company_id', '=', 'company_id')])
    is_internal_transfer = fields.Boolean(copy=False, default=False)
    it_source_location_id = fields.Many2one('stock.location', domain=lambda self: [
        ('id', 'not in', self.env.user.source_trans_location.ids), ('usage', '=', 'internal')])
    it_issue_validation = fields.Boolean(compute='_it_issue_receive_validation', default=True)
    it_receive_validation = fields.Boolean(compute='_it_issue_receive_validation', default=True)
    it_user_validation = fields.Boolean(compute='_it_issue_receive_validation', default=True)
    dest_location_id = fields.Many2one('stock.location', string='Destination Location', store=True, required=0,
                                       domain=lambda self: [('id', 'in', self.env.user.int_trans_loc_ids.ids)],
                                       default=_get_default_location)
    source_location_id = fields.Many2one('stock.location', string='Source Location', store=True, required=0,
                                         domain=lambda self: [('id', 'in', self.env.user.source_trans_location.ids)],
                                         default=_get_default_source_location)
    description = fields.Text('Description', required=1)
    material_request_date = fields.Date(string='Requested Date', copy=False)
    material_approval_date = fields.Date(string='Approval Date', copy=False)
    approval_show = fields.Boolean(compute='_check_approvals_required', store=False)
    validate_date = fields.Date('Validation Date', copy=False)
    show_button = fields.Boolean(copy=False)
    received_state = fields.Boolean(store=1, copy=False)
    partial_received_state = fields.Boolean(store=1, copy=False)
    supply_req_move_ids = fields.Many2many('stock.move', 'supply_move_ref', 'supply_id', 'move_id', copy=False)
    supply_issue_ids = fields.Many2many('supply.material.issue', 'supply_issue_material_ref', 'request_id', 'issue_id')
    supply_line_product_ids = fields.Many2many('product.product', 'product_supply_request_rel', 'request_id',
                                               'product_id', string='Supply Product IDS',
                                               compute='_get_supply_line_product_ids')

    @api.depends('line_ids')
    def _get_supply_line_product_ids(self):
        """
        Get Supply Lines Product IDS
        """
        for rec in self:
            product_ids = rec.line_ids.mapped('product_id').ids
            rec.supply_line_product_ids = [(6, 0, product_ids)]

    @api.onchange('it_source_location_id', 'dest_location_id')
    def onchange_source_dest_internal_location(self):
        """
        Onchange Source and Destination Internal Transfer Location
        """
        if self.it_source_location_id and self.dest_location_id:
            if self.it_source_location_id.id == self.dest_location_id.id:
                message = 'Source and destination Location Can not be same'
                self.it_source_location_id = False
                return {'warning': {'title': 'Location Warning', "message": message}}

    def _it_issue_receive_validation(self):
        """
        Internal Transfer Issue Validation
        """
        for rec in self:
            user = rec.env.user
            if rec.it_source_location_id.id in user.int_trans_loc_ids.ids and rec.state == 'requested':
                rec.it_issue_validation = False
            else:
                rec.it_issue_validation = True
            if rec.create_uid.id == user.id and rec.state == 'issued':
                rec.it_receive_validation = False
            else:
                rec.it_receive_validation = True
            if rec.requested_by.id == rec.env.user.id and rec.state == 'rejected':
                rec.it_user_validation = False
            else:
                rec.it_user_validation = True

    def get_material_request(self):
        """
        Get Current Record Internal Transfer
        """
        action = self.env.ref('supply_material_request.action_supply_internal_transfer_request_call').sudo().read()[0]
        action['domain'] = [
            ('is_internal_transfer', '=', True),
            ('state', '=', 'requested'),
            ('it_source_location_id', 'in', self.env.user.int_trans_loc_ids.ids)
        ]
        action['context'] = {'create': False, 'delete': False}
        return action

    def material_internal_transfer_request(self):
        """
        Material Internal Transfer Request
        """
        if self.env.user.id != self.requested_by.id:
            raise UserError(_('You can not request Material Request.!!!'))
        if self.state != 'draft':
            raise UserError(_('Record has been processed already.!!!'))
        if any(line.product_qty == '0.0' for line in self.line_ids):
            raise UserError(_('Please Enter Requested Quantity for all lines.!!!'))
        self.material_request_date = fields.Date.context_today(self)
        self.state = 'requested'

    def create_material_transfer(self):
        """
        Create Material Transfer Lines
        This method Usage to Create Move for Internal Material Request
        """

        if self.it_source_location_id.id not in self.env.user.int_trans_loc_ids.ids:
            raise UserError(_('You can not approve this request as you do not handle this location.!!!'))
        quant_obj = self.env['stock.quant']
        if self.state != 'requested':
            raise UserError(_('Document already process'))
        if any(line.product_qty == '0.0' for line in self.line_ids):
            raise UserError(_('There is not Quantity to Process.!!!'))
        if self.line_ids and self.it_source_location_id and self.dest_location_id:
            for line in self.line_ids.filtered(lambda line: line.product_qty > 0.0):
                available_qty = quant_obj._get_available_quantity(product_id=line.product_id,
                                                                  location_id=self.it_source_location_id,
                                                                  strict=False)
                if not available_qty:
                    raise UserError(_('%s product not have enough qty for issue' % (line.product_id.name)))
                move_vals = line.prep_stock_move_vals(location_id=self.it_source_location_id,
                                                      name=_('Supply request move for %s' % (self.name)),
                                                      dest_loac_id=self.dest_location_id)
                if move_vals:
                    move_id = self.env['stock.move'].create(move_vals)
                    move_id._action_confirm()
                    move_id._action_assign()
                    # todo need to check why delete move line
                    for mv_ln in move_id.move_line_ids:
                        if mv_ln.product_qty <= 0.0:
                            mv_ln.unlink()
                        else:
                            mv_ln.qty_done = mv_ln.product_uom_qty
                    self.supply_req_move_ids = [(4, move_id.id)]
                    line.internal_transfer_qty += line.product_qty
            self.state = 'issued'

    def receive_issued_internal_transfer(self):
        """
        received Issued Internal Transfer
        """
        if self.requested_by.id != self.env.user.id:
            raise UserError(_('Item can be received by only the user who have requested it.!!!'))
        if self.state != 'issued':
            raise UserError(_('Record has been Processed Already.!!!'))
        if not self.supply_req_move_ids:
            raise UserError(_('There is no Move to Process Further.!!!'))
        for move in self.supply_req_move_ids:
            move._action_done()
        self.state = 'received'

    @api.depends('company_id.module_supply_request_approval', 'state')
    def _check_approvals_required(self):
        """
        Checks whether request approval required or not which is configured in settings
        """
        for request in self:
            request.approval_show = False
            request.show_button = False
            if request.env.user.company_id.module_supply_request_approval:
                request.approval_show = True
            if request.env.user.company_id.module_supply_request_approval and request.state == 'approved':
                request.show_button = True
            if not request.env.user.company_id.module_supply_request_approval and request.state == 'draft':
                request.show_button = True

    def button_draft(self):
        """
        Set state as Draft
        """
        if self.state != 'draft':
            return self.write({'state': 'draft'})

    def button_to_approve(self):
        """
        Set state as to approve
        """
        if not self.line_ids:
            raise UserError(_('material line is not added'))
        if self.state != 'to_approve':
            return self.write({'state': 'to_approve'})

    def button_internal_transfer_reject(self):
        """
        This button is used to reject Internal Transfer
        """
        if self.state not in ('draft', 'requested'):
            raise UserError(_('Record has been processed already.!!!'))
        self.state = 'rejected'

    def button_rejected(self):
        """
        Set state as to rejected
        """
        if self.state not in ('to_approve', 'approved'):
            raise UserError(_('Record has been processed already.!!!'))
        if any(line.total_transfer_qty > 0.0 or line.transfer_qty > 0.0 for line in self.line_ids):
            raise UserError(_('transfer already issue you can not cancel'))
        if self.supply_issue_ids:
            for issue in self.supply_issue_ids:
                if issue.state != 'draft':
                    raise UserError(_('Supply already issue you can not cancel'))
                issue.state = 'cancel'
        if self.state != 'rejected':
            return self.write({'state': 'rejected'})

    def button_reset(self):
        """
        Reset state as to draft
        """
        if self.state in ('cancel', 'rejected'):
            return self.write({'state': 'draft'})

    def action_receive_qty(self):
        """
        receive quantity from transfer
        link transit move in line who have issue from issue
        after receive qty transit move will be blank
        """
        if self.line_ids:
            for line in self.line_ids.filtered(lambda transfer_line: transfer_line.transfer_qty > 0.0):
                move_line = line.transit_stock_move_ids.filtered(lambda move: move.state not in ('done', 'cancel'))
                if not move_line:
                    continue
                if line.received_qty != line.transfer_qty:
                    raise UserError(_('Receive qty should not less than issued qty'))
                move_line.write({'quantity_done': line.received_qty, 'is_supply_receive': True})
                for mv in move_line:
                    for mv_ln in mv.move_line_ids:
                        mv_ln.qty_done = mv_ln.product_uom_qty
                        mv_ln.total_issued_qty = mv_ln.product_uom_qty
                        mv_ln.sec_total_issued_qty = mv_ln.product_uom_qty
                        line.stock_move_line_ids = [(4, mv_ln.id)]
                    mv._action_done()
                line.total_received_qty += line.received_qty
                line.received_qty = 0.0
                line.transfer_qty = 0.0
        if all(line.product_qty == line.total_received_qty for line in self.line_ids):
            self.state = 'received'
            self.received_state = True
            self.partial_received_state = False
        if any(line.product_qty != line.total_received_qty and line.total_received_qty > 0.0 for line in self.line_ids):
            self.partial_received_state = True
            self.state = 'partial_receive'

    def write(self, vals):
        self.clear_caches()
        return super(InternalMaterialRequest, self).write(vals)

    def action_receive_all_qty(self):
        """
        receive all quantity
        """
        if self.line_ids:
            for line in self.line_ids.filtered(lambda transfer_line: transfer_line.transfer_qty > 0.0):
                move_line = line.transit_stock_move_ids.filtered(lambda move: move.state not in ('done', 'cancel'))
                if not move_line:
                    continue
                line.received_qty = line.transfer_qty
                if line.received_qty != line.transfer_qty:
                    raise UserError(_('Receive qty should not less than issued qty'))
                move_line.write({'quantity_done': line.received_qty, 'is_supply_receive': True})
                for mv in move_line:
                    for mv_ln in mv.move_line_ids:
                        mv_ln.qty_done = mv_ln.product_uom_qty
                        mv_ln.total_issued_qty = mv_ln.product_uom_qty
                        mv_ln.sec_total_issued_qty = mv_ln.product_uom_qty
                        line.stock_move_line_ids = [(4, mv_ln.id)]
                    mv._action_done()
                line.total_received_qty += line.received_qty
                line.received_qty = 0.0
                line.transfer_qty = 0.0
        if all(line.product_qty == line.total_received_qty for line in self.line_ids):
            self.state = 'received'
            self.received_state = True
            self.partial_received_state = False
        if any(line.product_qty != line.total_received_qty and line.total_received_qty > 0.0 for line in self.line_ids):
            self.partial_received_state = True
            self.state = 'partial_receive'

    def prepare_material_issue(self):
        """
        prepare material issue
        """
        return {
            'name': self.name,
            'dest_location_id': self.dest_location_id.id,
            'source_location_id': self.source_location_id.id,
            'company_id': self.company_id.id,
            'supply_req_id': self.id,
            'request_by': self.create_uid.id,
        }

    def prepare_material_issue_line(self):
        """
        prepare material issue line
        """
        record = []
        for rec in self.line_ids:
            if not rec.product_qty:
                raise UserError("There is not request qty for inventory !")
            record.append((0, 0, {
                'product_id': rec.product_id.id,
                'uom_id': rec.product_uom_id.id,
                'qty_approved': rec.product_qty,
                'total_qty': rec.product_qty,
                'issue_qty': rec.product_qty,
                'onhand_qty': rec.onhand_qty,
                'int_material_request_line_id': rec.id,
            }))
        return record

    def create_material_issuance(self, record_vals):
        """
        Create Material Issuance
        """
        supply_move_id = self.env['supply.material.issue'].sudo().create(record_vals)
        return supply_move_id

    def create_material_request(self):
        """
        Creates internal material request with adding stock picking id and request date in request
        """
        if self.state == 'requested':
            raise UserError(_('Request has been processed already.!!!'))
        if not self.line_ids:
            raise UserError(_('material line is not added'))
        if self.state not in ['draft', 'approved']:
            raise UserError(_('Document already process'))
        issue_line_vals = self.prepare_material_issue_line()
        if issue_line_vals:
            issue_vals = self.prepare_material_issue()
            if issue_vals:
                issue_vals.update({'material_issue_line': issue_line_vals})
                supply_move = self.create_material_issuance(record_vals=issue_vals)
                self.supply_issue_ids = [(4, supply_move.id)]
        self.state = 'requested'
        self.material_request_date = fields.Date.context_today(self)


class MaterialRequestLine(models.Model):
    _name = "internal.material.request.line"
    _description = "Internal Material Request Line"
    _inherit = ['mail.thread']

    @api.depends('product_id', 'name', 'product_uom_id', 'product_qty', 'analytic_account_id', 'date_required',
                 'specifications')
    def _compute_is_editable(self):
        """
        Compute field for editable or not editable state
        """
        for rec in self:
            if rec.request_id.state in (
                    'to_approve', 'approved', 'rejected', 'received', 'requested', 'partial_receive'):
                rec.is_editable = False
            else:
                rec.is_editable = True

    state = fields.Selection(related='request_id.state', store=True)
    product_id = fields.Many2one('product.product', 'Product', tracking=True)
    name = fields.Char('Description', size=256, tracking=True)
    product_uom_id = fields.Many2one('uom.uom', 'Product Unit of Measure', tracking=True)
    product_qty = fields.Float('Request Quantity', tracking=True)
    request_id = fields.Many2one('internal.material.request', 'Material Request', ondelete='cascade', readonly=True)
    company_id = fields.Many2one('res.company', 'Company', required=True, default=lambda self: self.env.company.id)
    analytic_account_id = fields.Many2one('account.analytic.account', 'Analytic Account', tracking=True)
    requested_by = fields.Many2one('res.users', related='request_id.requested_by', string='Requested by', store=True,
                                   readonly=True)
    date_start = fields.Date(related='request_id.date_start', string='Start Date', readonly=True, store=True)
    origin = fields.Char(related='request_id.origin', size=32, string='Source Document', readonly=True, store=True)
    date_required = fields.Date(string='Request Date', required=True, tracking=True, default=fields.Date.context_today)
    is_editable = fields.Boolean(string='Is editable', compute="_compute_is_editable", readonly=True)
    specifications = fields.Text(string='Specifications')
    request_state = fields.Selection(string='Request state', readonly=True, related='request_id.state', store=True)
    cancelled = fields.Boolean(string="Cancelled", readonly=True, default=False, copy=False)
    source_location_id = fields.Many2one('stock.location', 'Source Location', domain=[('usage', '=', 'internal')])
    onhand_qty = fields.Float('Onhand Qty', compute='_get_available_product_qty', store=True)
    received_qty = fields.Integer('Received Qty', copy=False)
    transfer_qty = fields.Integer('Transfer Qty', copy=False)
    total_received_qty = fields.Float('Total Received', copy=False)
    transit_stock_move_id = fields.Many2one('stock.move', copy=False)
    transit_stock_move_ids = fields.Many2many('stock.move', 'transfer_move_line_rel', 'line_id', 'move_id', copy=False)
    total_transfer_qty = fields.Float('Total transferd', copy=False)
    product_uom_category_id = fields.Many2one(related='product_id.uom_id.category_id', readonly=True)
    internal_transfer_qty = fields.Float('Internal Transfer Quantity')
    stock_move_line_ids = fields.Many2many('stock.move.line', 'transfer_stock_move_line_rel', 'transfer_line_id',
                                           'move_line_id', string='Move Line IDS')

    @api.constrains('onhand_qty', 'product_qty')
    def constrains_qty_available_product_qty(self):
        """
        Check Quantity Available Quantity and
        product quantity and if available quantity is less than Qty than restrictions
        """
        for rec in self:
            if rec.product_qty > rec.onhand_qty:
                raise UserError(_("Available Quantity for %s is less than requested quantity") % rec.product_id.name)

    def prep_stock_move_vals(self, location_id, dest_loac_id, name):
        """
        prepare stock move vals
        """
        return {
            'location_id': location_id.id,
            'location_dest_id': dest_loac_id.id,
            'product_id': self.product_id.id,
            'product_uom': self.product_uom_id.id,
            'product_uom_qty': self.product_qty,
            'quantity_done': self.product_qty,
            'int_material_request_line_id': self.id,
            'origin': self.request_id.name,
            'name': name,
            'supply_req_id': self.request_id.id
        }

    def unlink(self):
        if self.request_id and self.request_id.state != 'draft':
            raise ValidationError(_('You can delete Material Line'))
        return super(MaterialRequestLine, self).unlink()

    @api.constrains('product_qty', 'received_qty')
    def check_negetive_qty(self):
        """
        Constrains for negative product quantity
        """
        for product in self:
            move_ids = self.env['stock.move'].search([
                ('product_id', '=', product.product_id.id),
                ('supply_issue_line_id', '!=', False),
                ('int_material_request_line_id', '!=', False),
                ('location_dest_id', '=', product.request_id.dest_location_id.id),
                ('state', '=', 'assigned')])
            if move_ids and product.request_id.state in ('draft', 'to_approve', 'approved'):
                for mv in move_ids:
                    diff = fields.Date.context_today(self) - mv.date.date()
                    if diff.days > product.company_id.supply_transit_days:
                        raise UserError(_('%s product is already have in transit location'
                                          ' you can not create new supply request' % (product.product_id.name)))
            if product.product_qty <= 0:
                raise UserError(_("Quantity can't be less than or equal to 0!!!"))
            if product.received_qty < 0.0:
                raise UserError(_('Received qty should not less then 0'))
            if product.received_qty > product.transfer_qty:
                raise UserError(_('Received qty should not greater than transfer qty'))

    @api.depends('product_id')
    def _get_available_product_qty(self):
        """
        Method to get available product qty
        :return:
        """
        for rec in self:
            if rec.product_id and rec.source_location_id:
                query = """
                    select sum(q.quantity - q.reserved_quantity) 
                    from stock_quant as q
                    left join stock_location as sl on (q.location_id = sl.id)
                    where 
                        sl.usage = 'internal' 
                        and q.location_id = %s
                        and q.product_id = %s
                    """ % (rec.source_location_id.id, rec.product_id.id)
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
            move_ids = self.env['stock.move'].search([
                ('product_id', '=', self.product_id.id),
                ('supply_issue_line_id', '!=', False),
                ('location_dest_id', '=', self.request_id.dest_location_id.id),
                ('int_material_request_line_id', '!=', False),
                ('state', '=', 'assigned')])
            if move_ids:
                for mv in move_ids:
                    diff = fields.Date.context_today(self) - mv.date.date()
                    if diff.days > self.company_id.supply_transit_days:
                        raise UserError(_('%s product is already have in transit location'
                                          ' you can not create new supply request' % (self.product_id.name)))
            name = self.product_id.name
            if self.product_id.code:
                name = '[%s] %s' % (name, self.product_id.code)
            if self.product_id.description_purchase:
                name += '\n' + self.product_id.description_purchase
            self.product_uom_id = self.product_id.uom_id.id
            self.product_qty = 1
            self.name = name


class StockMoveLine(models.Model):
    _inherit = 'stock.move.line'

    total_issued_qty = fields.Float('Total Issued Quantity')
    sec_total_issued_qty = fields.Float('Total Issued Quantity')
