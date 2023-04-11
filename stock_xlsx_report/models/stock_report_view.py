# -*- coding: utf-8 -*-
# Copyright  Softprime Consulting Pvt Ltd

from odoo import models, fields, api, _


class StockReportDbView(models.Model):
    _name = "stock.report.db.view"
    _auto = False

    product_id = fields.Many2one('product.product', 'Product Name')
    location_id = fields.Many2one('stock.location', string='Locations')
    opening = fields.Float('Opening')
    purchase = fields.Float('Purchase')
    purchase_return = fields.Float('Purchase Returned')
    sale = fields.Float('Sale')
    sale_return = fields.Float('Sale Returned')
    internal = fields.Float('Internal')
    adjustment = fields.Float('Adjustment')
    closing = fields.Float('Closing')
    date = fields.Date('Date')
    scrap = fields.Float('Scrap')

    def _where(self, from_date, to_date, product_ids, company_id, warehouse_ids, location_ids):
        """
        Where clause for query based on
        """
        query = ''
        if from_date and to_date:
            query += "AND d.date BETWEEN '%s' AND '%s' " % (from_date, to_date)
        else:
            if from_date:
                query += "AND d.date >= '%s' " % from_date
            if to_date:
                query += "AND d.date <= '%s' " % to_date

        if product_ids:
            if len(product_ids.ids) == 1:
                query += 'AND d.product = {} '.format(product_ids.id)
            else:
                query += 'AND d.product in {} '.format(tuple(product_ids.ids))
        if company_id:
            query += 'AND d.company = {}  '.format(company_id.id)
        if warehouse_ids:
            if len(warehouse_ids.ids) == 1 :
                query += 'AND sw.id = {}  '.format(warehouse_ids.id)
            else:
                if len(warehouse_ids.ids) == 1:
                    query += 'AND sw.id = {}  '.format(warehouse_ids)
                else:
                    query += 'AND sw.id in {}  '.format(tuple(warehouse_ids.ids))
        if location_ids:
            if len(location_ids.ids) == 1:
                query += 'AND d.location = {}'.format(location_ids.id)
            else:
                query += 'AND d.location in {}'.format(tuple(location_ids.ids))
        return query

    def internal_record(self):
        """
        Stock transaction within internal locations
        """
        location = self.env['stock.location'].search([('usage', '=', 'internal')])
        if len(location.ids) == 1:
            location = '= {}'.format(location.id)
        else:
            location = ' in {}'.format(tuple(location.ids))
        internal_src = '''
        internal_src as(
                    select sml.product_id as product,
                    sml.company_id as company,  
                    case 
                        when sml.location_id {} then sml.location_id
                        else 0
                    end
                    as location,
                    CAST(sml.date as DATE) as date,
                    0.0 as sale,
                    0.0 as purchase,                            
                    0.0 as sale_return,
                    0.0 as purchase_return,
                    0.0 as opening,
                    sum(sml.qty_done) * -1 as internal,
                    0.0 as adjustment,
                    0.0 as scrap
                    from stock_move_line sml
                    join stock_picking sp on sp.id=sml.picking_id
                    join stock_move sm on sm.id = sml.move_id
                    join stock_picking_type spt on spt.id=sp.picking_type_id
                    where sp.state='done'
                    and spt.code='internal'
                    group by sml.location_id, sml.product_id, sml.company_id, sm.to_refund, sml.location_dest_id, sml.date
                ),
        '''.format(location)
        internal_dest = '''
        internal_dest as(
                    select sml.product_id as product,
                    sml.company_id as company,  
                    case 
                        when sml.location_dest_id {} then sml.location_dest_id
                        else 0
                    end
                    as location,
                    CAST(sml.date as DATE) as date,
                    0.0 as sale,
                    0.0 as purchase,                            
                    0.0 as sale_return,
                    0.0 as purchase_return,
                    0.0 as opening,
                    sum(sml.qty_done) as internal,
                    0.0 as adjustment,
                    0.0 as scrap
                    from stock_move_line sml
                    join stock_picking sp on sp.id=sml.picking_id
                    join stock_move sm on sm.id = sml.move_id
                    join stock_picking_type spt on spt.id=sp.picking_type_id
                    where sp.state='done'
                    and spt.code='internal'
                    group by sml.location_id, sml.product_id, sml.company_id, sm.to_refund, sml.location_dest_id, sml.date
                ),
        '''.format(location)
        internal = internal_src + internal_dest
        return internal, location

    def with_query(self, from_date):
        """
            Variables to store data from different queries
        """
        internal, location = self.internal_record()
        with_query = '''
                with sale as (
                    select sml.product_id as product,  
                    sml.company_id as company,                 
                    sml.location_id as location,
                    CAST(sml.date as DATE) as date,
                    SUM(sml.qty_done) as sale,
                    0.0 as purchase,
                    0.0 as sale_return, 
                    0.0 as purchase_return,
                    0.0 as opening,
                    0.0 as internal,
                    0.0 as adjustment,
                    0.0 as scrap
                    from stock_move_line as sml
                    join stock_picking sp on sp.id=sml.picking_id
                    join stock_move sm on sm.id=sml.move_id
                    join stock_picking_type spt on spt.id=sp.picking_type_id
                    where sml.picking_id is not null
                    and sml.state='done' 
                    and spt.code = 'outgoing'
                    and sm.sale_line_id is not null
                    group by sml.product_id, sml.location_id, sml.company_id, sml.date
                ),
                purchase as(
                    select sml.product_id as product,
                    sml.company_id as company,                 
                    sml.location_dest_id as location,
                    CAST(sml.date as DATE) as date,
                    0.0 as sale,
                    sum(sml.qty_done) as purchase,
                    0.0 as sale_return, 
                    0.0 as purchase_return,
                    0.0 as opening,
                    0.0 as internal,
                    0.0 as adjustment,
                    0.0 as scrap
                    from stock_move_line sml   
                    join stock_picking sp on sp.id = sml.picking_id
                    join stock_move sm on sm.id=sml.move_id
                    join stock_picking_type spt on spt.id=sp.picking_type_id
                    where sml.picking_id is not null
                    and sp.state='done'
                    and sml.picking_id is not null
                    and sm.purchase_line_id is not null
                    and spt.code = 'incoming'
                    group by sml.product_id, sml.location_dest_id, sml.company_id, sml.date
                ),
                sale_return as (
                    select sml.product_id as product,
                    sml.company_id as company,                 
                    sml.location_dest_id as location,
                    CAST(sml.date as DATE) as date,
                    0.0 as sale,
                    0.0 as purchase,
                    sum(sml.qty_done) as sale_return, 
                    0.0 as purchase_return,
                    0.0 as opening,
                    0.0 as internal,
                    0.0 as adjustment,
                    0.0 as scrap
                    from stock_move_line sml   
                    left join stock_location sl on sl.id=sml.location_dest_id
                    join stock_picking sp on sp.id = sml.picking_id
                    join stock_move sm on sm.id=sml.move_id
                    join stock_picking_type spt on spt.id=sp.picking_type_id
                    where sp.state='done'
                    and sm.sale_line_id is not null
                    and sl.usage='internal'
                    group by sml.product_id, sml.location_dest_id, sml.company_id, sml.date
                ),
                purchase_return as (
                    select sml.product_id as product,
                    sml.company_id as company,                 
                    sml.location_id as location,
                    CAST(sml.date as DATE) as date,
                    0.0 as sale,
                    0.0 as purchase,
                    0.0 as sale_return,
                    sum(sml.qty_done) as purchase_return,
                    0.0 as opening,
                    0.0 as internal,
                    0.0 as adjustment,
                    0.0 as scrap
                    from stock_move_line sml    
                    left join stock_location sl on sl.id=sml.location_dest_id
                    join stock_picking sp on sp.id=sml.picking_id
                    join stock_move sm on sm.id=sml.move_id
                    where sl.usage='supplier'
                    and sp.state='done'
                    and sm.purchase_line_id is not null
                    group by sml.location_id, sml.product_id, sml.company_id, sml.date
                ),
                adjustment as (
                    select sml.product_id as product,
                    sml.company_id as company,                 
                    sml.location_id as location,
                    CAST(sml.date as DATE) as date,
                    0.0 as sale,
                    0.0 as purchase,
                    0.0 as sale_return,
                    0.0 as purchase_return,
                    0.0 as opening,
                    0.0 as internal,
                    sum(sml.qty_done) as adjustment,
                    0.0 as scrap
                    from stock_move_line sml
                    left join stock_location sl on sl.id=sml.location_id
                    join stock_move sm on sm.id=sml.move_id
                    where sm.state='done'
                    and sl.usage ='internal'
                    and sm.is_inventory = 'true'
                    group by sml.location_id, sml.product_id, sml.company_id, sml.date
                
                ),
                scrap as(
                    select sml.product_id as product,
                    sml.company_id as company,                 
                    sml.location_id as location,
                    CAST(sml.date as DATE) as date,
                    0.0 as sale,
                    0.0 as purchase,
                    0.0 as sale_return,
                    0.0 as purchase_return,
                    0.0 as opening,
                    0.0 as internal,
                    0.0 as adjustment,
                    sum(sml.qty_done) as scrap
                    from stock_move_line sml
                    left join stock_location sl on sl.id=sml.location_dest_id
                    join stock_move sm on sm.id=sml.move_id
                    where sm.state='done'
                    and sl.usage ='inventory'
                    and sm.scrapped = 'true'
                    group by sml.location_id, sml.product_id, sml.company_id, sml.date
                ),   
                '''

        with_query += internal
        if from_date:
            with_query += '''
                    opening as (
                        select sml.product_id as product,
                            sml.company_id as company,    
                            case             
                                when sml.location_id {} then sml.location_id
                                when sml.location_dest_id {} then sml.location_dest_id
                            end as location,
                            CAST('{}' as Date) as date,
                            0.0 as sale,
                            0.0 as purchase,
                            0.0 as sale_return,
                            0.0 as purchase_return,
                            sum(sml.qty_done) as opening,
                            0.0 as internal,
                            0.0 as adjustment,
                            0.0 as scrap
                            from stock_move_line sml
                            join stock_picking sp on sp.id=sml.picking_id
                            where sp.state = 'done'
                            and CAST(sml.date as DATE) < '{}'
                            group by sml.location_id, sml.location_dest_id, sml.product_id, sml.company_id, sml.date
                            ),
                    data as(
                            select * from sale
                            union 
                            select * from purchase
                            union
                            select * from sale_return
                            union
                            select * from purchase_return
                            union 
                            select * from opening
                            union
                            select * from internal_src
                            union
                            select * from internal_dest
                            union
                            select * from adjustment
                            union 
                            select * from scrap
                        )
                    '''.format(location, location, from_date, from_date)
            return with_query
        with_query += '''
                data as(
                    select * from sale
                    union 
                    select * from purchase
                    union
                    select * from sale_return
                    union
                    select * from purchase_return
                    union
                    select * from internal_src
                    union
                    select * from internal_dest
                    union
                    select * from adjustment
                    union 
                    select * from scrap
                )
                '''
        return with_query

    def get_data(self, from_date, to_date, product_ids, company_id, warehouse_ids, location_ids):
        """
        Extracting data for stock report from database
        """
        where_query = self._where(from_date, to_date, product_ids, company_id, warehouse_ids, location_ids)
        with_query = self.with_query(from_date)
        if where_query:
            select_query = '''
                    SELECT row_number() OVER() as id,
                    d.location as location_id,
                    d.product as product_id,
                    sum(d.purchase) as purchase,
                    sum(d.sale) as sale,
                    sum(d.opening) as opening,
                    sum(d.adjustment) as adjustment,
                    sum(d.internal) as internal,
                    sum(d.sale_return) as sale_return,
                    sum(d.purchase_return) as purchase_return,
                    sum(d.scrap) as scrap,
                    sum(d.opening) + sum(d.purchase) - sum(d.purchase_return) - sum(d.sale) + sum(d.sale_return) + sum(d.internal) - sum(d.adjustment) -sum(scrap)  as closing
                    FROM data d
                    join stock_warehouse sw on sw.company_id=d.company
                    join stock_location sl on sl.id=d.location
                    where d.product is not null
                '''
            group_by = '''group by d.product, d.location'''
            query = 'CREATE OR REPLACE VIEW stock_report_db_view AS(%s %s %s %s)' % (with_query, select_query, where_query, group_by)
            self._cr.execute(query)
        else:
            query = '''CREATE OR REPLACE VIEW stock_report_db_view AS(  %s 
                        SELECT row_number() OVER() as id,
                            d.location as location_id,
                            d.product as product_id,
                            sum(d.purchase) as purchase,
                            sum(d.sale) as sale,
                            sum(d.opening) as opening,
                            sum(d.adjustment) as adjustment,
                            sum(d.internal) as internal,
                            sum(d.sale_return) as sale_return,
                            sum(d.purchase_return) as purchase_return,
                            sum(d.scrap) as scrap,
                            sum(d.opening) + sum(d.purchase) - sum(d.purchase_return) - sum(d.sale) + sum(d.sale_return) + sum(d.internal) - sum(d.adjustment) - sum(scrap) as closing
                            FROM data d
                            join stock_warehouse sw on sw.company_id=d.company
                            join stock_location sl on sl.id=d.location
                            group by d.product, d.location
                        )''' % with_query
            self._cr.execute(query)
