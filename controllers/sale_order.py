from odoo import http
from odoo.http import request
import json

class SaleQuotationController(http.Controller):

    @http.route('/api/sale_order/create', type='http', auth='public', methods=['POST'], csrf=False)
    def create_sale_order(self, **kwargs):
        # Parse JSON request data
        try:
            kwargs = request.get_json_data()
        except Exception as e:
            return request.make_response(
                json.dumps({"error": f"Invalid JSON: {str(e)}"}), 
                headers={'Content-Type': 'application/json'}, 
                status=400
            )

        # Extract required fields
        partner_id = kwargs.get('partner_id')
        user_id = kwargs.get('user_id')
        order_lines = kwargs.get('order_lines')
        company_id = kwargs.get('company_id')

        # Validate required fields
        if not company_id:
            return request.make_response(
                json.dumps({"error": "company_id is required."}),
                headers={'Content-Type': 'application/json'}, 
                status=400
            )

        if not partner_id:
            return request.make_response(
                json.dumps({"error": "partner_id is required."}),
                headers={'Content-Type': 'application/json'}, 
                status=400
            )

        # Check if the partner exists
        partner = request.env['res.partner'].sudo().browse(partner_id)
        if not partner.exists():
            return request.make_response(
                json.dumps({"error": f"Partner with ID {partner_id} does not exist."}),
                headers={'Content-Type': 'application/json'}, 
                status=404
            )

        # Validate order lines
        if not order_lines or not isinstance(order_lines, list):
            return request.make_response(
                json.dumps({"error": "order_lines must be a non-empty list."}),
                headers={'Content-Type': 'application/json'}, 
                status=400
            )

        sale_order_lines = []
        # Validate each order line product
        for line in order_lines:
            product_id = line.get('product_id')
            quantity = line.get('quantity', 1)
            price_unit = line.get('price_unit', 0.0)

            product = request.env['product.product'].sudo().browse(product_id)
            if not product.exists():
                return request.make_response(
                    json.dumps({"error": f"Product with ID {product_id} does not exist."}),
                    headers={'Content-Type': 'application/json'}, 
                    status=404
                )

            sale_order_lines.append((0, 0, {
                'product_id': product_id,
                'product_uom_qty': quantity,
                'price_unit': price_unit,
            }))

        # Create the Sale Order and handle errors
        try:
            sale_order = request.env['sale.order'].sudo().create({
                'company_id': company_id,
                'user_id': user_id,
                'partner_id': partner_id,
                'order_line': sale_order_lines,
            })

            # Confirm the sale order
            sale_order.action_confirm()

            # Handle the delivery (stock.picking) and reserve quantities
            for picking in sale_order.picking_ids:
                picking.action_assign()  # Reserve stock
                if picking.state == 'assigned':  # Check if quantities are reserved
                    picking.action_validate()  # Validate the transfer

            # Check if picking has been processed
            if any(picking.state != 'done' for picking in sale_order.picking_ids):
                return request.make_response(
                    json.dumps({"error": "Not all pickings have been validated."}),
                    headers={'Content-Type': 'application/json'},
                    status=400
                )

            # Create the invoice for the sale order
            invoice = sale_order._create_invoices(grouped=False)

        except Exception as e:
            return request.make_response(
                json.dumps({"error": str(e)}),
                headers={'Content-Type': 'application/json'}, 
                status=500
            )

        # Successful response with sale order and invoice details
        data = {
            "success": True,
            "message": "Sale order created and invoice generated successfully",
            "sale_order_id": sale_order.id,
            "sale_order_name": sale_order.name,
            "invoice_id": invoice.id,
            "invoice_name": invoice.name,
        }
        return request.make_response(
            json.dumps(data), 
            headers={'Content-Type': 'application/json'}
        )
 

# class SaleQuotationController(http.Controller):

#     @http.route('/api/sale_order/create', type='http', auth='public', methods=['POST'], csrf=False)
#     def create_sale_order(self, **kwargs):
#         # Parse JSON request data
#         try:
#             kwargs = request.get_json_data()
#         except Exception as e:
#             return request.make_response(
#                 json.dumps({"error": f"Invalid JSON: {str(e)}"}), 
#                 headers={'Content-Type': 'application/json'}, 
#                 status=400
#             )

#         # Extract required fields
#         partner_id = kwargs.get('partner_id')
#         user_id = kwargs.get('user_id')
#         order_lines = kwargs.get('order_lines')
#         company_id = kwargs.get('company_id')

#         # Validate required fields
#         if not company_id:
#             return request.make_response(
#                 json.dumps({"error": "company_id is required."}),
#                 headers={'Content-Type': 'application/json'}, 
#                 status=400
#             )

#         if not partner_id:
#             return request.make_response(
#                 json.dumps({"error": "partner_id is required."}),
#                 headers={'Content-Type': 'application/json'}, 
#                 status=400
#             )

#         # Check if the partner exists
#         partner = request.env['res.partner'].sudo().browse(partner_id)
#         if not partner.exists():
#             return request.make_response(
#                 json.dumps({"error": f"Partner with ID {partner_id} does not exist."}),
#                 headers={'Content-Type': 'application/json'}, 
#                 status=404
#             )

#         # Validate order lines
#         if not order_lines or not isinstance(order_lines, list):
#             return request.make_response(
#                 json.dumps({"error": "order_lines must be a non-empty list."}),
#                 headers={'Content-Type': 'application/json'}, 
#                 status=400
#             )

#         sale_order_lines = []
#         # Validate each order line product
#         for line in order_lines:
#             product_id = line.get('product_id')
#             quantity = line.get('quantity', 1)
#             price_unit = line.get('price_unit', 0.0)

#             product = request.env['product.product'].sudo().browse(product_id)
#             if not product.exists():
#                 return request.make_response(
#                     json.dumps({"error": f"Product with ID {product_id} does not exist."}),
#                     headers={'Content-Type': 'application/json'}, 
#                     status=404
#                 )

#             sale_order_lines.append((0, 0, {
#                 'product_id': product_id,
#                 'product_uom_qty': quantity,
#                 'price_unit': price_unit,
#             }))

#         # Create the Sale Order and handle errors
#         try:
#             sale_order = request.env['sale.order'].sudo().create({
#                 'company_id': company_id,
#                 'user_id': user_id,
#                 'partner_id': partner_id,
#                 'order_line': sale_order_lines,
#             })

#             # Confirm the sale order
#             sale_order.action_confirm()

#         except Exception as e:
#             return request.make_response(
#                 json.dumps({"error": str(e)}),
#                 headers={'Content-Type': 'application/json'}, 
#                 status=500
#             )

#         # Successful response with sale order details
#         data = {
#             "success": True,
#             "message": "Sale order created successfully",
#             "sale_order_id": sale_order.id,
#             "sale_order_name": sale_order.name,
#         }
#         return request.make_response(
#             json.dumps(data), 
#             headers={'Content-Type': 'application/json'}
#         )