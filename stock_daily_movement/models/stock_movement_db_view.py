# -*- coding: utf-8 -*-

# Softprime Consulting Pvt Ltd
# Copyright (C) Softprime Consulting Pvt Ltd
# All Rights Reserved
# https://softprimeconsulting.com/

from odoo import fields, models, api, _


class StockMovementView(models.Model):
    _name = 'stock.daily.movement.db.view'
    _auto = False

    product_id = fields.Many2one('product.product', string='Item Name')
    reference = fields.Char('Reference')
    date = fields.Date('Date')
    name = fields.Char('Name')
    from_location_id = fields.Many2one('stock.location', string='From')
    to_location_id = fields.Many2one('stock.location', string='To')
    opening = fields.Float('Opening')
    purchase = fields.Float('Purchase')
    sale = fields.Float('Sales')
    sale_return = fields.Float('Sales Returned')
    internal_transfer = fields.Float('Internal Transfer')
    adjustment = fields.Float('Adjustment')
    value = fields.Float('Value')
    on_hand = fields.Float('On Hand')
    avg_cost = fields.Float('Average Cost')

    def where_query(self, from_date, to_date, product_ids, location_ids, company_id):
        """
        Filtering Data
        """
        query = ''
        if from_date and to_date:
            query += " AND d.date BETWEEN '%s' and '%s' " % (from_date, to_date)
        else:
            if from_date:
                query += " AND d.date >= '%s' " % from_date
            elif to_date:
                query += " AND d.date <= '%s' " % to_date
        if product_ids:
            if len(product_ids.ids) == 1:
                query += ' And d.product_id = {}'.format(product_ids.id)
            else:
                query += ' And d.product_id in {}'.format(tuple(product_ids.ids))
        if location_ids:
            if len(location_ids.ids) == 1:
                query += ' And (d.from = {} or d.to = {})'.format(location_ids.id, location_ids.id)
            else:
                query += ' And (d.from in {} or d.to in {}) '.format(tuple(location_ids.ids), tuple(location_ids.ids))
        if company_id:
            query += ' AND d.company_id = {} '.format(company_id.id)
        return query

    def _with(self, from_date):
        """
        Data from multiple tables
        """
        with_query = ''
        with_query += '''
                with sale as(
                    select sm.product_id as product_id,
                    sm.location_id as from,
                    sm.location_dest_id as to,
                    sum(sm.product_qty) as sale,
                    0.0 as purchase,
                    0.0 as sale_return,                    
                    0.0 as internal,
                    0.0 as adjustment,
                    0.0 as opening,
                    CAST(sm.date as DATE) as date,
                    sm.company_id as company_id,
                    sm.reference as reference,
                    sum(sq.quantity) as on_hand,
                    sum(svl.value) as value,
                    round(sum(svl.value)/sum(svl.quantity), 4) as avg
                    from stock_move sm
                    join stock_valuation_layer svl on svl.stock_move_id = sm.id
                    join stock_location sl on sl.id = sm.location_id
                    join stock_picking sp on sp.id = sm.picking_id
                    join stock_picking_type spt on spt.id = sp.picking_type_id
                    join stock_quant sq on sq.product_id=sm.product_id and sq.location_id = sm.location_id
                    where sl.usage = 'internal'
                    and spt.code = 'outgoing'
                    and sm.sale_line_id is not null
                    and sm.state = 'done'
                    group by sm.product_id, sm.location_id, sq.location_id, sm.location_dest_id, sm.date, sm.company_id, sm.reference    
                ),
                purchase as (
                    select sm.product_id as product_id,
                    sm.location_id as from,
                    sm.location_dest_id as to,
                    0.0 as sale,
                    sum(sm.product_qty) as purchase,
                    0.0 as sale_return,
                    0.0 as internal,
                    0.0 as adjustment,
                    0.0 as opening,
                    CAST(sm.date as DATE) as date,
                    sm.company_id as company_id,
                    sm.reference as reference,
                    sum(sq.quantity) as on_hand,
                    sum(svl.value) as value,
                    round(sum(svl.value)/sum(svl.quantity), 4) as avg
                    from stock_move sm
                    join stock_valuation_layer svl on svl.stock_move_id = sm.id
                    join stock_location sl on sl.id = sm.location_dest_id
                    join stock_picking sp on sp.id = sm.picking_id
                    join stock_picking_type spt on spt.id = sp.picking_type_id
                    join stock_quant sq on sq.product_id=sm.product_id and sm.location_dest_id = sq.location_id
                    where sl.usage = 'internal'
                    and spt.code = 'incoming'
                    and sm.purchase_line_id is not null
                    and sm.state = 'done'
                    group by sm.product_id, sm.location_id, sq.location_id, sm.location_dest_id, sm.date, sm.company_id, sm.reference 
                ),
                sale_return as(
                    select sm.product_id as product_id,
                    sm.location_id as from,
                    sm.location_dest_id as to,
                    0.0 as sale,
                    0.0 as purchase,
                    sum(sm.product_qty) as sale_return,
                    0.0 as internal,
                    0.0 as adjustment,
                    0.0 as opening,
                    CAST(sm.date as DATE) as date,
                    sm.company_id as company_id,
                    sm.reference as reference,
                    sum(sq.quantity) as on_hand,
                    sum(svl.value) as value,
                    round(sum(svl.value)/sum(svl.quantity), 4) as avg
                    from stock_move as sm
                    join stock_valuation_layer svl on svl.stock_move_id = sm.id
                    join stock_location sl on sl.id = sm.location_dest_id
                    join stock_picking sp on sp.id = sm.picking_id
                    join stock_picking_type spt on spt.id = sp.picking_type_id
                    join stock_quant sq on sq.product_id=sm.product_id and sm.location_dest_id = sq.location_id
                    where sl.usage = 'internal'
                    and sm.origin_returned_move_id is not null
                    and sm.sale_line_id is not null
                    and sm.state = 'done'
                    and spt.code = 'incoming'
                    group by sm.product_id, sm.location_id, sq.location_id, sm.location_dest_id, sm.date, sm.company_id, sm.reference
                ),
                internal_transfer as (
                    select sm.product_id as product_id,
                    sm.location_id as from,
                    sm.location_dest_id as to,
                    0.0 as sale,
                    0.0 as purchase,
                    0.0 as sale_return,
                    sum(sm.product_qty) as internal,
                    0.0 as adjustment,
                    0.0 as opening,
                    CAST(sm.date as DATE) as date,
                    sm.company_id as company_id,
                    sm.reference as reference,
                    sum(sq.quantity) as on_hand,
                    0.0 as value,
                    0.0 as avg
                    from stock_move sm
                    join stock_location sl on sl.id = sm.location_id
                    join stock_picking sp on sp.id = sm.picking_id
                    join stock_picking_type spt on spt.id = sp.picking_type_id
                    join stock_quant sq on sq.product_id=sm.product_id and sm.location_id = sq.location_id
                    where sm.state = 'done'
                    and spt.code = 'internal'
                    and sl.usage = 'internal'
                    and sm.sale_line_id is null
                    and sm.purchase_line_id is null
                    group by sm.product_id, sm.location_id, sq.location_id, sm.location_dest_id, sm.date, sm.company_id, sm.reference
                ),
                adjustment as(
                    select sm.product_id as product_id,
                    sm.location_id as from,
                    sm.location_dest_id as to,
                    0.0 as sale,
                    0.0 as purchase,
                    0.0 as sale_return,
                    0.0 as internal,
                    sum(sm.product_qty) as adjustment,
                    0.0 as opening,
                    CAST(sm.date as DATE) as date,
                    sm.company_id as company_id,
                    sm.reference as reference,
                    sum(sq.quantity) as on_hand,
                    sum(svl.value) as value,
                    round(sum(svl.value)/sum(svl.quantity), 4) as avg
                    from stock_move sm
                    join stock_valuation_layer svl on svl.stock_move_id = sm.id
                    join stock_location sl on sl.id = sm.location_id
                    join stock_quant sq on sq.product_id=sm.product_id and sm.location_id = sq.location_id
                    where sm.state = 'done'
                    and sl.usage = 'internal'
                    and sm.is_inventory = 'True'
                    group by sm.product_id, sm.location_id, sq.location_id, sm.location_dest_id, sm.date, sm.company_id, sm.reference
                ),
                
        '''
        data = '''
                data as (
                    select * from sale
                    union
                    select * from purchase
                    union
                    select * from sale_return 
                    union 
                    select * from internal_transfer
                    union 
                    select * from adjustment
                '''
        if from_date:
            with_query += '''opening as (
                            select sm.product_id as product_id,
                            sm.location_id as from,
                            sm.location_dest_id as to,
                            0.0 as sale,
                            0.0 as purchase,
                            0.0 as sale_return,
                            0.0 as internal,
                            0.0 as adjustment,
                            sum(sm.product_qty) as opening,
                            CAST('%s' as DATE) as date,
                            sm.company_id as company_id,
                            sm.reference as reference,
                            0.0 as on_hand,
                            0.0 as value,
                            0.0 as avg
                            from stock_move sm
                            join stock_valuation_layer svl on svl.stock_move_id = sm.id
                            join stock_location sl on sl.id = sm.location_id
                            where sm.state = 'done'
                            and CAST(sm.date as date) < '%s'
                            group by sm.product_id, sm.location_id, sm.location_dest_id, sm.date, sm.company_id, sm.reference
                        ),''' % (from_date, from_date)
            data += ''' union
                        select * from opening )'''
            query = with_query + data
            return query
        data += ')'
        query = with_query + data
        return query

    def get_data(self, from_date, to_date, product_ids, location_ids, company_id):
        """
        Get Data
        """
        where_query = self.where_query(from_date, to_date, product_ids, location_ids, company_id)
        with_query = self._with(from_date)
        if where_query:
            create_view = '''CREATE OR REPLACE VIEW  stock_daily_movement_db_view AS ( %s %s %s)'''
            select = '''
                        SELECT row_number() OVER() as id,
                        d.product_id as product_id,     
                        d.reference as reference,
                        d.from as from_location_id,
                        d.to as to_location_id,
                        d.opening as opening,
                        d.date as date,
                        d.sale as sale,
                        d.purchase as purchase,
                        d.sale_return as sale_return,
                        d.internal as internal_transfer,
                        d.adjustment as adjustment,
                        d.value as value,
                        d.on_hand as on_hand,
                        d.avg as avg_cost
                        FROM data as d
                        WHERE d.date is not null
                    '''
            query = create_view % (with_query, select, where_query)
            self._cr.execute(query)
        else:
            create_view = '''CREATE OR REPLACE VIEW  stock_daily_movement_db_view AS ( %s %s)'''
            select = '''
                        SELECT row_number() OVER() as id,
                        d.product_id as product_id,
                        d.reference as reference,
                        d.from as from_location_id,
                        d.to as to_location_id,
                        d.opening as opening,
                        d.date as date,
                        d.sale as sale,
                        d.purchase as purchase,
                        d.sale_return as sale_return,
                        d.internal as internal_transfer,
                        d.adjustment as adjustment,
                        d.value as value,
                        d.on_hand as on_hand,
                        d.avg as avg_cost
                        FROM data as d
                    '''
            query = create_view % (with_query, select)
            self._cr.execute(query)
