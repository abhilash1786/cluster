# Softprime Consulting Pvt Ltd
# Copyright (C) Softprime Consulting Pvt Ltd
# All Rights Reserved
# https://softprimeconsulting.com/
from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class MultiProductScrap(models.Model):
    _name = "res.product.scrap"
    _description = "Multi Product Scrap"
    _rec_name = "reference_no"
    _order = "id desc"
    _inherit = ["mail.thread", "mail.activity.mixin"]

    reference_no = fields.Char(
        required=True, readonly=True, default=lambda self: _("New")
    )
    source_location_id = fields.Many2one(
        "stock.location", string="Source Location", tracking=True
    )
    scrap_location_id = fields.Many2one(
        "stock.location", string="Scrap Location", tracking=True
    )
    source_document = fields.Char("Source Document")
    company_id = fields.Many2one(
        "res.company", string="Company", default=lambda self: self.env.company
    )
    state = fields.Selection(
        [("draft", "Draft"), ("done", "Done")],
        string="Status",
        default="draft",
        tracking=True,
    )
    multi_scrap_ids = fields.One2many("stock.scrap", "multi_product_scrap_id")
    confirm_date = fields.Datetime("Date", tracking=True)

    @api.onchange("source_location_id")
    def onchange_source_location(self):
        """
        blank scrap line if you change location
        """
        if self.state == "draft":
            self.multi_scrap_ids = False

    def action_validate(self):
        """
        Validate Stock Scrap
        """
        # todo i can not directly call action validate method because
        #  if product dont not have on hand qty it has return wizard
        #  and ask you want validate or not this process was not available
        #  in here it will do direct scrap
        if self.state == "done":
            return True
        if not self.multi_scrap_ids:
            raise ValidationError(_("Add Product Lines"))
        for scrap_id in self.multi_scrap_ids:
            if scrap_id.state == "draft":
                scrap_id.location_id = self.source_location_id.id
                scrap_id.scrap_location_id = self.scrap_location_id.id
                scrap_id.origin = self.source_document
                scrap_id.do_scrap()
        self.state = "done"
        self.confirm_date = fields.Datetime.now()

    @api.model
    def create(self, vals):
        """
        Sequence Generation for Multi Product Scrap
        """
        if vals.get("reference_no", _("New")) == _("New"):
            vals["reference_no"] = self.env["ir.sequence"].next_by_code(
                "res.product.scrap"
            ) or _("New")
        res = super().create(vals)
        return res


class StockScrap(models.Model):
    _inherit = "stock.scrap"

    multi_product_scrap_id = fields.Many2one("res.product.scrap")
    onhand_qty = fields.Float("On Hand Qty")

    @api.onchange("product_id", "location_id")
    def onchange_product_onhand(self):
        """
        get on hand qty
        """
        quant_obj = self.env["stock.quant"]
        if self.product_id:
            available_qty = quant_obj._get_available_quantity(
                product_id=self.product_id, location_id=self.location_id, strict=False
            )
            self.onhand_qty = available_qty

    @api.constrains("scrap_qty")
    def _check_qrt(self):
        for line in self:
            if line.product_id and line.onhand_qty < line.scrap_qty:
                raise ValidationError(
                    _("Scrap Quantity Should Be Less Than Onhand Qty for %s")
                    % line.product_id.name
                )
            if line.scrap_qty <= 0:
                raise ValidationError(
                    _("Scrap Quantity Should Be Greater Than 0 for %s")
                    % line.product_id.name
                )
