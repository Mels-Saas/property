from odoo import http
from odoo.http import request
from datetime import datetime, timedelta

class PropertyDashboardController(http.Controller):

    @http.route('/property_dashboard/data', auth='user', type='json')
    def get_dashboard_data(self, site_id=None, block_id=None, floor_id=None, period=30):
        env = request.env
        today = datetime.today()
        start_date = today - timedelta(days=int(period))
        domain = [('create_date', '>=', start_date.strftime('%Y-%m-%d'))]

        # Apply filters
        if site_id:
            domain.append(('site_id', '=', int(site_id)))
        if block_id:
            domain.append(('block_id', '=', int(block_id)))
        if floor_id:
            domain.append(('floor_id', '=', int(floor_id)))

        # Property Data
        property_obj = env['property.property']
        total_properties = property_obj.search_count(domain)
        available_properties = property_obj.search_count(domain + [('status', '=', 'available')])
        reserved_properties = property_obj.search_count(domain + [('status', '=', 'reserved')])
        sold_properties = property_obj.search_count(domain + [('status', '=', 'sold')])

        property_data = {
            'labels': ['Available', 'Reserved', 'Sold'],
            'datasets': [{
                'label': 'Properties',
                'data': [available_properties, reserved_properties, sold_properties],
                'backgroundColor': ['#36A2EB', '#FFCE56', '#FF6384'],
            }],
            'total': total_properties,
        }

        # Revenue Data
        payment_line_obj = env['property.payment.line']
        payment_domain = [('sale_id.create_date', '>=', start_date.strftime('%Y-%m-%d'))]
        if site_id or block_id or floor_id:
            payment_domain.append(('sale_id.property_id', 'in', property_obj.search(domain).ids))
        
        total_revenue = sum(payment_line_obj.search(payment_domain).mapped('expected_amount'))
        paid_revenue = sum(payment_line_obj.search(payment_domain).mapped('paid_amount'))
        remaining_revenue = sum(payment_line_obj.search(payment_domain).mapped('remaining'))

        revenue_data = {
            'labels': ['Total', 'Paid', 'Remaining'],
            'datasets': [{
                'label': 'Revenue',
                'data': [total_revenue, paid_revenue, remaining_revenue],
                'backgroundColor': '#36A2EB',
                'barThickness': 40,
            }],
        }

        # Commission Data
        commission_line_obj = env['property.commission.line']
        commission_domain = [('sale_id.create_date', '>=', start_date.strftime('%Y-%m-%d'))]
        if site_id or block_id or floor_id:
            commission_domain.append(('sale_id.property_id', 'in', property_obj.search(domain).ids))

        total_commission = sum(commission_line_obj.search(commission_domain).mapped('expected_amount'))
        paid_commission = sum(commission_line_obj.search(commission_domain).mapped('paid_amount'))
        remaining_commission = sum(commission_line_obj.search(commission_domain).mapped('remaining'))

        commission_data = {
            'labels': ['Total', 'Paid', 'Remaining'],
            'datasets': [{
                'label': 'Commission',
                'data': [total_commission, paid_commission, remaining_commission],
                'backgroundColor': '#FF6384',
                'barThickness': 40,
            }],
        }

        # Filter Options
        sites = env['property.site'].search([]).read(['id', 'name'])
        blocks = env['property.block'].search([]).read(['id', 'name'])
        floors = env['property.floor'].search([]).read(['id', 'name'])

        return {
            'property_data': property_data,
            'revenue_data': revenue_data,
            'commission_data': commission_data,
            'sites': sites,
            'blocks': blocks,
            'floors': floors,
        }