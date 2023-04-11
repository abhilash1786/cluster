from odoo import _, api, models
from odoo.exceptions import UserError


class ProductCategory(models.Model):
    _inherit = "product.category"

    @api.model
    def create(self, vals):
        """Inherit to make default property_cost_method and property valuation"""
        vals["property_cost_method"] = "average"
        vals["property_valuation"] = "real_time"
        return super().create(vals)

    @api.constrains("property_cost_method", "property_valuation")
    def check_costing_method_inventory_valuation(self):
        """Constrains used to restrict costing method and inventory valuation change
        if category linked with any transacted product;;
        """
        for product_categ in self:
            if product_categ:
                query_product = _(
                    """select * from stock_move sm join product_product pp
                                    ON sm.product_id = pp.id join product_template pt
                                    on pt.id = pp.product_tmpl_id join product_category pc
                                    ON pt.categ_id = %s limit 1"""
                )
                self.env.cr.execute(
                    query_product,
                    [
                        self.id,
                    ],
                )
                prd_categ = self.env.cr.fetchall()
                if prd_categ:
                    raise UserError(
                        _(
                            "Product category %s contain some products for which "
                            "transaction exists! If indeed required, kindly create "
                            "a new category with required configuration"
                            % str(product_categ.name)
                        )
                    )
