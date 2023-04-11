from odoo import fields, models, api, _
from odoo.exceptions import UserError


class StockDailyReport(models.TransientModel):
    _name = 'stock.wiz'

    from_date = fields.Date('Start Date')
    to_date = fields.Date('End Date')
    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.user.company_id)
    warehouse_ids = fields.Many2many('stock.warehouse', string='Warehouses')
    location_ids = fields.Many2many('stock.location', string='Locations')
    product_ids = fields.Many2many('product.product', string="Products")

    @api.constrains('to_date', 'from_date')
    def validate_from_date(self):
        """
        Validating from date and to date
        """
        if self.from_date and self.to_date:
            if self.from_date > self.to_date:
                raise UserError(_("Start date cannot be more than End Date"))

    def action_report(self):
        """
        Stock Report Action
        """
        action = self.env.ref('stock_xlsx_report.action_stock_report').read()[0]
        action['context'] = {'from_date': self.from_date,
                             'to_date': self.to_date,
                             'company_id': self.company_id.id,
                             'warehouse_ids': self.warehouse_ids,
                             'location_ids': self.location_ids,
                             'product_ids': self.product_ids}
        self.env['stock.report.db.view'].get_data(self.from_date, self.to_date, self.product_ids, self.company_id, self.warehouse_ids, self.location_ids)
        return action

    def action_detail_report(self):
        """
        Stock Detailed Report Action
        """
        action = self.env.ref('stock_xlsx_report.action_stock_detail_report').read()[0]
        action['context'] = {'from_date': self.from_date,
                             'to_date': self.to_date,
                             'company_id': self.company_id.id,
                             'warehouse_ids': self.warehouse_ids,
                             'src_location_id': self.location_ids,
                             'product_ids': self.product_ids}
        self.env['stock.detail.report.db.view'].get_data(self.from_date, self.to_date, self.product_ids, self.company_id, self.warehouse_ids, self.location_ids)
        return action


