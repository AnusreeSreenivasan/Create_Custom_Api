from odoo import http
from odoo.http import request
import json


class CustomerAPIController(http.Controller):

    @http.route('/get_customer', type='http', auth='public', methods=['POST'], csrf=False)
    def get_customer_details(self, **data_passed):
        kwargs = request.get_json_data()
        phone = kwargs.get('phone')
        if not phone:
            return {'error': 'Phone number is required'}

        customer = request.env['res.partner'].sudo().search([('phone', '=', phone)], limit=1)

        if not customer:
            return {'error': 'Customer not found'}
        data = {
            'name': customer.name,
            'address': customer.city,
            'street': customer.street,
            'city': customer.city,
            'country_id': customer.country_id.name,
        }
        return request.make_response(http.json.dumps(data),
            headers={'Content-Type': 'application/json'})
        
