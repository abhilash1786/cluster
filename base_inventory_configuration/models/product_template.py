# -*- coding: utf-8 -*-
from odoo.exceptions import UserError, ValidationError

from odoo import models, api, _


class ProductProduct(models.Model):
    _inherit = 'product.product'

    #
    # @api.constrains('name')
    # def check_product_name_duplicity(self):
    #     """
    #     Constrains used to check duplicity for product;;
    #     """
    #     for product in self:
    #         company_clause = ''
    #         arg_list = ''
    #         if self.company_id:
    #             company_clause += 'and (company_id = %s)'
    #             arg_list += (tuple(product.env.company.id),)
    #         query_product = _('''select id from product_product
    #                                 where name = %s
    #                                 and id != %s
    #                                 ''' + company_clause + '''
    #                                 limit 1''')
    #         arg_list = (str(product.name), self.id,) + tuple(arg_list)
    #         self.env.cr.execute(query_product, arg_list)
    #         prd = self.env.cr.fetchall()
    #         if prd:
    #             raise UserError(_('Product %s already exist!' % str(product.name)))

    def unlink(self):
        """
        Restricted deletion of product if product have used for any previous transaction;;
        """
        for product in self:
            query_stock_move = _("""select id from stock_move_line 
                                    where product_id = %s limit 1""") % str(product.id)
            self.env.cr.execute(query_stock_move)
            moves = self.env.cr.fetchall()
            if moves:
                raise UserError(
                    _('Can not delete this product (%s) because transaction exist there!!! ' % str(product.name)))
            else:
                super(ProductProduct, self).unlink()


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    # @api.constrains('name')
    # def check_product_name_duplicity(self):
    #     """
    #     Constrains used to check duplicity for product;;
    #     """

    #     for product in self:
    #         company_clause = ''
    #         arg_list = ''
    #         if self.company_id:
    #             company_clause += 'and (company_id = %s)'
    #             arg_list += (tuple(product.env.company.id),)
    #         query_product = '''select id from product_template
    #                             where name = '%s'
    #                             and id != %s
    #                             limit 1''' % (product.name, self.id)
    #         print(query_product)
    #         # arg_list = (product.name, self.id,) + tuple(arg_list)
    #         self.env.cr.execute(query_product)
    #         prd = self.env.cr.fetchall()
    #         if prd:
    #             raise UserError(_('Product %s already exist!' % str(product.name)))

    @api.constrains('name')
    def check_product_name_duplicity(self):
        name_rec = self.search(
            [('name', '=', self.name)])
        if len(name_rec) > 1:
            raise ValidationError(_('Product already exist'))

    def unlink(self):
        """
        Restricted deletion of product if product have used for any previous transaction;;
        """
        for product in self:
            query_stock_move = _("""select id from stock_move_line 
                                    where product_id= %s limit 1""") % str(product._origin.id)
            self.env.cr.execute(query_stock_move)
            moves = self.env.cr.fetchall()
            if moves:
                raise UserError(
                    _('Can not delete this product (%s) because transaction exist there!!! ' % str(product.name)))
            else:
                super(ProductTemplate, self).unlink()

    # @api.constrains('categ_id')
    # def check_product_category(self):
    #     """
    #     Constrains used to check category change restriction for product;;
    #     """
    #     for product in self:
    #         if self.detailed_type == 'product':
    #             query_product = _('''select id from stock_move
    #                                        where product_id = %s
    #                                        limit 1''')
    #             self.env.cr.execute(query_product, [self.id])
    #             prd = self.env.cr.fetchall()
    #             if prd:
    #                 raise UserError(_('For product %s, transaction already exists! '
    #                                   'So can not change product category. If indeed required, '
    #                                   'can archive this product and create a new one.' % str(product.name)))

    # @api.constrains('categ_id')
    # def check_product_category(self):
    #     catg_rec = self.search([('categ_id', '=', self.categ_id.id)])
    #     for rec in range(len(catg_rec)):
    #         if catg_rec[rec] != self.categ_id:
    #             raise ValidationError("You can't change category of product once the sale order is created")
    #         else:
    #             break

    # @api.constrains('categ_id')
    # def check_product_category(self):
    #     result = self.env['product.template'].browse(self.categ_id)
    #     for rec in result:
    #         if rec == self.categ_id:
    #             break
    #         else:
    #             raise ValidationError("You can't change category of product once the sale order is created")

    @api.model
    def create(self, vals):
        """
        Override for product category validation check
        """
        res = super(ProductTemplate, self).create(vals)
        # res.check_product_category()
        return res

    def write(self, vals):
        """
        Override for product category validation check
        """
        if 'categ_id' in vals.keys():
            if vals['categ_id'] != self.categ_id.id:
                raise UserError(_("You cannot change category of product once the sale order is created"))
        # self.check_product_category(new_categ = vals)

        if 'detailed_type' in vals.keys():
            if vals['detailed_type'] != self.detailed_type:
                raise UserError(_("You cannot change product type once the sale order is created"))

        if 'invoice_policy' in vals.keys():
            if vals['invoice_policy'] != self.invoice_policy:
                raise UserError(_("You cannot change invoicing policy once the sale order is created"))

        res = super(ProductTemplate, self).write(vals)
        return res
