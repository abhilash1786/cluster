# Softprime Consulting Pvt Ltd
# Copyright (C) Softprime Consulting Pvt Ltd
# All Rights Reserved
# https://softprimeconsulting.com/
from odoo import _, api, fields, models
from odoo.exceptions import UserError

_STATES = [
    ("draft", "Draft"),
    ("partial_issue", "Partial Issue"),
    ("issued", "issued"),
    ("cancel", "Cancel"),
    ("return_received", "Return Received"),
]


class MaterialRequestIssue(models.Model):
    _name = "supply.material.issue"
    _description = "Supply Material Issue"
    _inherit = ["mail.thread"]
    _order = "name desc"

    name = fields.Char("Reference")
    warehouse_id = fields.Many2one("stock.warehouse", "Warehouse")
    dest_location_id = fields.Many2one("stock.location", "Location")
    date = fields.Date("Request Date", default=fields.Date.context_today)
    supply_req_id = fields.Many2one("internal.material.request", copy=False)
    material_issue_line = fields.One2many("material.issue.line", "issue_id", copy=False)
    state = fields.Selection(
        selection=_STATES,
        string="Status",
        index=True,
        tracking=True,
        required=True,
        copy=False,
        default="draft",
    )
    company_id = fields.Many2one(
        "res.company",
        string="Company",
        required=True,
        default=lambda self: self.env.company,
    )
    supply_issue_move_ids = fields.Many2many(
        "stock.move", "supply_issue_move_ref", "issue_id", "move_id", copy=False
    )
    request_by = fields.Many2one("res.users", "Request By", copy=False)
    issued_by = fields.Many2one("res.users", "Issued By", copy=False)
    source_location_id = fields.Many2one(
        "stock.location", "Source Location", copy=False
    )

    def material_issue(self):
        """material issue and create stock move and link with material line"""
        quant_obj = self.env["stock.quant"]
        if self.state not in ["draft", "partial_issue"]:
            raise UserError(_("Document already process"))
        if all(line.issue_qty == 0.0 for line in self.material_issue_line):
            raise UserError(_("fill issue qty in request line"))
        if not self.sudo().supply_req_id.company_id.supply_transit_loc:
            raise UserError(_("Configure supply transit location"))
        if (
            self.material_issue_line
            and self.source_location_id
            and self.dest_location_id
        ):
            for line in self.material_issue_line.filtered(
                lambda line: line.issue_qty > 0.0
            ):
                available_qty = quant_obj._get_available_quantity(
                    product_id=line.product_id,
                    location_id=self.source_location_id,
                    strict=True,
                )
                if not available_qty:
                    raise UserError(
                        _(
                            "%s product not have enough qty for issue"
                            % (line.product_id.name)
                        )
                    )
                move_vals = line.prep_stock_move_vals(
                    location_id=self.source_location_id,
                    name=_("Supply request move for %s" % (self.name)),
                    dest_loac_id=self.sudo().supply_req_id.company_id.supply_transit_loc,
                )
                if move_vals:
                    move_id = self.env["stock.move"].create(move_vals)
                    move_id._action_confirm()
                    move_id._action_assign()
                    for mv_ln in move_id.move_line_ids:
                        if mv_ln.product_qty <= 0.0:
                            mv_ln.unlink()
                        else:
                            mv_ln.qty_done = mv_ln.product_uom_qty
                    move_id._action_done()
                    line.source_transit_move = move_id.id
                    self.supply_issue_move_ids = [(4, move_id.id)]
                    self.sudo().supply_req_id.supply_req_move_ids = [(4, move_id.id)]
                    line.total_issue_qty += line.issue_qty
                confirm_move_vals = line.prep_stock_move_vals(
                    dest_loac_id=self.dest_location_id,
                    name=_("Supply request move for %s" % (self.name)),
                    location_id=self.sudo().supply_req_id.company_id.supply_transit_loc,
                )
                if confirm_move_vals:
                    if confirm_move_vals:
                        second_move_id = self.env["stock.move"].create(
                            confirm_move_vals
                        )
                        second_move_id._action_confirm()
                        second_move_id._action_assign()
                        line.transit_dest_move = second_move_id.id
                        line.sudo().int_material_request_line_id.transit_stock_move_ids = [
                            (4, second_move_id.id)
                        ]
                        self.supply_issue_move_ids = [(4, second_move_id.id)]
                        self.sudo().supply_req_id.supply_req_move_ids = [
                            (4, second_move_id.id)
                        ]
                line.issue_qty = 0.0
        self.issued_by = self.env.user.id
        if all(
            line.qty_approved == line.total_issue_qty
            for line in self.material_issue_line
        ):
            self.state = "issued"
        else:
            self.state = "partial_issue"

    def cancel_supply_issue_request(self):
        """This Method is Used for cancellation for supply issue record"""
        if self.state != "draft":
            raise UserError(_("Record has been Processed Already.!!!"))
        self.supply_req_id.sudo().state = "rejected"
        self.state = "cancel"

    def cancel_latest_material_issue(self):
        """cancel material issue and create return move"""
        if self.material_issue_line:
            for line in self.material_issue_line:
                if line.transit_dest_move and line.transit_dest_move.state == "done":
                    raise UserError(
                        _(
                            "%s product already received by request user "
                            "you can not cancel" % (line.product_id.name)
                        )
                    )
                else:
                    if line.int_material_request_line_id.transfer_qty > 0.0:
                        move_vals = line.prep_stock_move_vals(
                            dest_loac_id=self.source_location_id,
                            name=_("Cancel Supply Material Issue for %s" % (self.name)),
                            location_id=self.supply_req_id.company_id.supply_transit_loc,
                        )
                        move_id = self.env["stock.move"].sudo().create(move_vals)
                        move_id[
                            "quantity_done"
                        ] = line.source_transit_move.quantity_done
                        move_id.update({"is_material_return": True})
                        move_id._action_assign()
                        move_id._action_confirm()
                        move_id._action_done()
                        self.supply_issue_move_ids = [(4, move_id.id)]
                        self.supply_req_id.supply_req_move_ids = [(4, move_id.id)]
                        line.total_issue_qty -= line.transit_dest_move.quantity_done
                        line.int_material_request_line_id.transfer_qty -= (
                            line.transit_dest_move.quantity_done
                        )
                        line.int_material_request_line_id.total_transfer_qty -= (
                            line.transit_dest_move.quantity_done
                        )
                        line.transit_dest_move.sudo()._action_cancel()
            if all(
                line.qty_approved == line.total_issue_qty
                for line in self.material_issue_line
            ):
                self.state = "issued"
            else:
                self.state = "partial_issue"


class IssueLine(models.Model):
    _name = "material.issue.line"
    _description = "Supply Material Issue Line"

    issue_id = fields.Many2one("supply.material.issue")
    product_id = fields.Many2one("product.product", "Product")
    uom_id = fields.Many2one("uom.uom", "UOM")
    total_qty = fields.Float("Total Quantity")
    qty_approved = fields.Float("Qty Approved")
    issue_qty = fields.Float("Issue Qty")
    total_issue_qty = fields.Float("Total Issued Qty")
    company_id = fields.Many2one(
        "res.company",
        string="Company",
        required=True,
        default=lambda self: self.env.company,
    )
    int_material_request_line_id = fields.Many2one(
        "internal.material.request.line", copy=False
    )
    onhand_qty = fields.Integer("Onhand Qty", copy=False)
    source_transit_move = fields.Many2one("stock.move", copy=False)
    transit_dest_move = fields.Many2one("stock.move", copy=False)

    @api.constrains("issue_qty")
    def check_material_issue_qty(self):
        """check issue qty"""
        for rec in self:
            if rec.issue_qty > (rec.qty_approved - rec.total_issue_qty):
                raise UserError(
                    _("Issue qty should not greater than total approve qty")
                )

    def prep_stock_move_vals(self, location_id, dest_loac_id, name):
        """prepare stock move vals"""
        return {
            "location_id": location_id.id,
            "location_dest_id": dest_loac_id.id,
            "product_id": self.product_id.id,
            "product_uom": self.uom_id.id,
            "product_uom_qty": self.issue_qty,
            "quantity_done": self.issue_qty,
            "int_material_request_line_id": self.sudo().int_material_request_line_id.id,
            "supply_issue_line_id": self.id,
            "origin": self.issue_id.name,
            "name": name,
            "material_issue_id": self.issue_id.id,
            "supply_req_id": self.sudo().int_material_request_line_id.request_id.id,
        }
