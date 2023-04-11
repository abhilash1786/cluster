from odoo import models, fields


class ProductCategory(models.Model):
    _inherit = 'product.category'

    property_cost_method = fields.Selection([
        ('standard', 'Standard Price'),
        ('fifo', 'First In First Out (FIFO)'),
        ('average', 'Average Cost (AVCO)')], default='average', string="Costing Method",
        company_dependent=True, copy=True, required=True,
        help="""Standard Price: The products are valued at their standard cost defined on the product.
                                   Average Cost (AVCO): The products are valued at weighted average cost.
                                   First In First Out (FIFO): The products are valued supposing those that enter the company first will also leave it first.
                                   """)
    property_valuation = fields.Selection([
        ('manual_periodic', 'Manual'),
        ('real_time', 'Automated')], default='real_time', string='Inventory Valuation',
        company_dependent=True, copy=True, required=True,
        help="""Manual: The accounting entries to value the inventory are not posted automatically.
                                   Automated: An accounting entry is automatically created to value the inventory when a product enters or leaves the company.
                                   """)
