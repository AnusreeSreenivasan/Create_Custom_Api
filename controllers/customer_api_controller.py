from odoo import http
from odoo.http import request,Response
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
        
class CustomerAPIController(http.Controller):

    @http.route('/api/customers', type='json', auth='public', methods=['POST'], csrf=False)
    def create_customer(self, **kwargs):
        """Creates a new customer"""
        try:
            # Get data from the request body (sent as JSON)
            data = request.jsonrequest

            # Ensure required fields are provided
            if not data.get('name'):
                return Response(
                    json.dumps({'status': 'error', 'message': 'Name is required'}),
                    content_type='application/json',
                    status=400
                )

            # Create customer using the provided data
            new_customer = request.env['res.partner'].sudo().create({
                'name': data.get('name'),
                'email': data.get('email', False),
                'phone': data.get('phone', False),
                'company_name': data.get('company_name', False),
                'is_company': data.get('is_company', False),
                'customer_rank': 1,  # Mark as a customer
            })

            # Return success response
            return Response(
                json.dumps({'status': 'success', 'customer_id': new_customer.id}),
                content_type='application/json',
                status=201
            )
        except Exception as e:
            # Handle any exception and return error response
            return Response(
                json.dumps({'status': 'error', 'message': str(e)}),
                content_type='application/json',
                status=500
            )