from odoo.exceptions import UserError

from odoo import models, api, _


class StockLocation(models.Model):
    _inherit = 'stock.location'

    def unlink(self):
        '''
        Inherited to restrict deletion of location if transaction exists for same location
        '''
        for location in self:
            query_stock_move = _("""select * from stock_move_line 
                                where location_id = %s or location_dest_id = %s limit 1""") % (location.id, location.id)
            self.env.cr.execute(query_stock_move)
            moves = self.env.cr.fetchall()
            if moves:
                raise UserError(_('Can not delete because transaction exist for %s location!!! ' % str(location.name)))
            else:
                super(StockLocation, self).unlink()

    def write(self, values):
        """
        inherited to restrice location type change if transaction exist for same location
        """
        if values.get('usage', False):
            for location in self:
                query_stock_move = _("""select * from stock_move_line 
                                                where location_id = %s or location_dest_id = %s limit 1""") % (
                location.id, location.id)
                location.env.cr.execute(query_stock_move)
                moves = location.env.cr.fetchall()
                if moves:
                    raise UserError(_(
                        "You cannot change the location type as transaction exists for same location"
                    ))
        res = super(StockLocation, self).write(values)
        return res

    @api.constrains('name', 'warehouse_id')
    def _check_location_duplicity(self):
        """
        check for duplicate location creation
        """
        existing_location = self.search([
            ('complete_name', '=', self.complete_name),
            ('id', '!=', self.id),
        ])
        if existing_location:
            raise UserError(_('Already Exist.!!!'))