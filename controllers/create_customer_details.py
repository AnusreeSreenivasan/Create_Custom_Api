import json
from odoo import http
from odoo.http import request, Response

class CustomerAPIController(http.Controller):

    @http.route('/api/customer_create', type='json', auth='public', methods=['POST'], csrf=False)
    def create_customer(self):
        try:
            data = request.get_json_data()

            # Check if required fields are provided
            if not data.get('name') or not data.get('email'):
                return {
                    'success': False,
                    'error': 'Name and Email are required.'
                }

            # Check for existing customers with the same name or email
            existing_customer = request.env['res.partner'].sudo().search([
                '|',  # Search for either condition
                ('email', '=', data['email']),
                ('name', '=', data['name']),
            ], limit=1)

            if existing_customer:
                return {
                    'success': False,
                    'error': 'Customer with this name or email already exists.'
                }

            # Create a new company customer (res.partner)
            company = request.env['res.partner'].sudo().create({
                'name': data['name'],
                'email': data['email'],
                'phone': data.get('phone', ''),
                'street': data.get('street', ''),
                'city': data.get('city', ''),
                'state_id': data.get('state_id'),
                'country_id': data.get('country_id'),
                'zip': data.get('zip', ''),
                'website': data.get('website', ''),
                'vat': data.get('vat', ''),
                'is_company': True,  # Marks it as a company
                'customer_rank': 1,  # Marks it as a customer
            })

            # If there are child contacts, create them under the company
            contacts_data = data.get('contacts', [])
            for contact in contacts_data:
                request.env['res.partner'].sudo().create({
                    'name': contact['name'],
                    'email': contact['email'],
                    'phone': contact.get('phone', ''),
                    'parent_id': company.id,  # Link to the company
                })

            # Return the response with the created company ID
            return {
                'success': True,
                'customer_id': company.id
            }

        except Exception as e:
            # Handle exceptions and return an error message
            return {
                'success': False,
                'error': str(e)
            }
