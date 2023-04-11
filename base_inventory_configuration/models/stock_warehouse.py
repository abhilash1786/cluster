from odoo.exceptions import UserError

from odoo import models, _


class StockWarehouse(models.Model):
    _inherit = 'stock.warehouse'

    def unlink(self):
        """
        Inherited to restrict deletion of warehouse if transaction exists for same location
        """
        for rec in self:
            move_ids = rec.env['stock.move'].search([
                ('warehouse_id', '=', rec.id),
            ])
            if move_ids:
                raise UserError(_('Can not delete because transaction exist for %s warehouse!!! ' % str(rec.name)))
            else:
                super(StockWarehouse, self).unlink()
