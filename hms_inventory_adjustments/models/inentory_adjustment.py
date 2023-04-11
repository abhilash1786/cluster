# Copyright  Softprime consulting Pvt Ltd
from odoo import _, api, fields, models
from odoo.exceptions import UserError


class InventoryAdj(models.Model):
    _name = "res.inventory.adjustment"
    _description = "Inventory Adjustment Location"
    _order = "id desc"
    _inherit = ["mail.thread", "mail.activity.mixin"]

    date = fields.Date("Date", required=True, default=fields.Date.context_today)
    name = fields.Char("Reference", copy=False)
    state = fields.Selection(
        [("draft", "Draft"), ("confirm", "Confirmed"), ("cancel", "Canceled")],
        default="draft",
    )
    company_id = fields.Many2one(
        "res.company",
        "Company",
        required=True,
        default=lambda self: self.env.company,
        tracking=True,
    )
    location_id = fields.Many2one("stock.location", "Location", tracking=True)
    adjustment_line = fields.One2many("inventory.adjustment.line", "adjustment_id")
    category_id = fields.Many2one("product.category", "Category", tracking=True)
    analytic_account_id = fields.Many2one(
        "account.analytic.account", "Analytic Account", tracking=True
    )
    product_ids = fields.Many2many('product.product', string="Products")

    def prepare_quant_list(self, line):
        """
        prepare quant dict
        """
        if line:
            return {
                "location_id": line.location_id.id,
                "product_id": line.product_id.id,
                "inventory_quantity": line.counted,
                "inventory_diff_quantity": line.counted - line.onhand_qty,
                "inventory_date": self.date,
                "company_id": line.company_id.id,
                "res_adjustment_id": self.id,
                "adjustment_line_id": line.id,
            }

    def stock_quant_check(self, line):
        """
        stock quant check if already available
        """
        if line:
            if line.lot_id:
                quant_id = self.env["stock.quant"].search(
                    [
                        ("product_id", "=", line.product_id.id),
                        ("company_id", "=", self.company_id.id),
                        ("location_id", "=", line.location_id.id),
                        ("lot_id", "=", line.lot_id.id),
                    ]
                )
            else:
                quant_id = self.env["stock.quant"].search(
                    [
                        ("product_id", "=", line.product_id.id),
                        ("location_id", "=", line.location_id.id),
                        ("company_id", "=", self.company_id.id),
                    ]
                )
            if quant_id:
                return quant_id

    def check_duplicate_product(self, product, lot=False):
        """
        check duplicate product in line
        """
        if product.company_id and self.company_id.id != product.company_id.id:
            raise UserError(
                _("%s this product is link with different company" % (product.name))
            )
        adj_line_ref = self.env["inventory.adjustment.line"]
        domain = [("product_id", "=", product.id), ("adjustment_id", "=", self.id)]
        if product.tracking != "none" and lot:
            domain += [("lot_id", "=", lot.id)]
        ids = adj_line_ref.search(domain)
        if ids and len(ids) > 1:
            raise UserError(_("%s product is added multiple in line" % (product.name)))

    # @api.constrains('adjustment_line', 'adjustment_line.product_id')
    # def check_product_duplicate(self):
    #     if self.adjustment_line:
    #         product_list_ids = []
    #         for line in self.adjustment_line:
    #             product_list_ids = (self.env["inventory.adjustment.line"].
    #                                 search([("product_id", "=", line.product_id.id),
    #                                         ('adjustment_id', '=', self._origin.id)]))
    #         if product_list_ids and len(product_list_ids) > 1:
    #             raise UserError(_("%s product is added multiple in line" % (line.product_id.name)))

    # @api.onchange('adjustment_line', 'adjustment_line.product_id')
    # def check_product_duplicate(self):
    #     if self.adjustment_line:
    #         for line in self.adjustment_line:
    #             product_list_ids = (self.env["inventory.adjustment.line"].
    #                                 search([("product_id", "=", line.product_id.id),
    #                                         ('adjustment_id', '=', self._origin.id)]))
    #             if product_list_ids:
    #                 record_product_names = {
    #                     'product_ids': line.product_id,
    #                 }
    #                 self.product_ids.create(record_product_names)

    def action_confirm_adjustment(self):
        """
        confirm adjustment to create new stock quant
        """
        if self.state == "confirm":
            return True
        if self.adjustment_line:
            for line in self.adjustment_line:
                if line.product_id.tracking != "none" and not line.lot_id:
                    raise UserError(
                        _(
                            "Product is tracking you need to add lot for this product %s"
                            % (line.product_id.name)
                        )
                    )
                self.check_duplicate_product(product=line.product_id, lot=line.lot_id)
                avl_quant_id = self.stock_quant_check(line=line)
                if avl_quant_id:
                    avl_quant_id._onchange_location_or_product_id()
                    avl_quant_id.inventory_quantity = line.counted
                    avl_quant_id.inventory_date = self.date
                    avl_quant_id.adjustment_line_id = line.id
                    avl_quant_id.res_adjustment_id = self.id
                    avl_quant_id.location_id = self.location_id.id
                    avl_quant_id.inventory_diff_quantity = (
                            line.counted - line.onhand_qty
                    )
                    avl_quant_id._compute_inventory_diff_quantity()
                    line.stock_quant_id = avl_quant_id.id
                    avl_quant_id._apply_inventory()
                else:
                    values = self.prepare_quant_list(line=line)
                    quant_id = self.env["stock.quant"].create(values)
                    line.stock_quant_id = quant_id.id
                    quant_id.inventory_diff_quantity = line.counted - line.onhand_qty
                    quant_id._compute_inventory_diff_quantity()
                    quant_id._apply_inventory()
        self.state = "confirm"

    def action_show_stock_quant(self):
        """
        Method to show stock quant
        """
        if self.adjustment_line.stock_quant_id:
            for rec in self:
                return {
                    "type": "ir.actions.act_window",
                    "name": "Stock Quant",
                    "res_model": "stock.quant",
                    "view_mode": "tree",
                    "context": {"create": False},
                    "domain": [("id", "=", rec.adjustment_line.stock_quant_id.ids)],
                }


class AdjustmentLine(models.Model):
    _name = "inventory.adjustment.line"
    _description = "Adjustment Line"

    location_id = fields.Many2one(
        "stock.location", related="adjustment_id.location_id", store=True
    )
    adjustment_id = fields.Many2one("res.inventory.adjustment", ondelete="cascade")
    product_id = fields.Many2one("product.product", "Product")
    onhand_qty = fields.Float("On Hand Qty")
    counted = fields.Float("Counted Qty")
    company_id = fields.Many2one(
        "res.company", "Company", required=True, default=lambda self: self.env.company
    )
    average_cost = fields.Float("Average Cost")
    value = fields.Float("Value")
    stock_quant_id = fields.Many2one("stock.quant", "Quant")
    lot_id = fields.Many2one("stock.lot", "Lot/Serial")
    analytic_account_id = fields.Many2one(
        "account.analytic.account", related="adjustment_id.analytic_account_id"
    )

    @api.constrains("counted")
    def counted_validation(self):
        for line in self:
            if line.counted < 0.0:
                raise UserError(_("Counted Quantity Should Not less than 0"))

    @api.onchange("product_id", "location_id")
    def onchange_product_id(self):
        """
        onchange product for get on hand quantity
        """
        if self.product_id:
            self.average_cost = self.product_id.standard_price
            if not self.lot_id:
                self.onhand_qty = (
                    self.product_id.sudo()
                    .with_context(location=self.location_id.id)
                    .qty_available
                )
            else:
                self.onhand_qty = (
                    self.product_id.sudo()
                    .with_context(location=self.location_id.id, lot_id=self.lot_id.id)
                    .qty_available
                )

    @api.onchange('product_id', 'adjustment_id')
    def onchange_product_id(self):
        for rec in self:
            product_list_ids = [line.product_id.id for line in rec.adjustment_id.adjustment_line]
            if len(product_list_ids) > 0:
                return {'domain': {'product_id': [("id", "not in", product_list_ids)]}}
            return {'domain': {'product_id': [("id", "=", False)]}}


