from odoo.http import Controller, request, route
import json
from odoo import http
from odoo.http import request

class PropertyController(Controller):

    @http.route('/web/session/authenticate', type='json', auth="none")
    def authenticate(self, db, login, password, base_location=None):
        request.session.authenticate(db, login, password)
        response=request.env['ir.http'].session_info()
        allowed_no_site = int(request.env['ir.config_parameter'].sudo().get_param('ahadubit_property_base.allows_site_no', default=0))

        response['site'] = {
            'allowed_no_site': allowed_no_site
        }
        return response

    @route('/api/lookup', type='http', auth='none', csrf=False, methods=['GET'])
    def get_lookup(self,name=None, **kwargs):
        try:
            session_id = request.httprequest.cookies.get('session_id')
            if not session_id:
                return request.make_response(
                    json.dumps({"status": 401, "error": "Unauthorized: No session found"}),
                    headers={'Content-Type': 'application/json'}
                )
            request.session.rotate = False
            user_id = request.session.uid
            if not user_id:
                return request.make_response(
                    json.dumps({"status": 401, "error": "Unauthorized: Invalid session"}),
                    headers={'Content-Type': 'application/json'}
                )

            # Get the user record
            user = request.env['res.users'].sudo().browse(user_id)

            if not user.exists():
                return request.make_response(
                    json.dumps({"status": 401, "error": "Unauthorized: User not found"}),
                    headers={'Content-Type': 'application/json'}
                )
            if name and name == "site":
                sites = request.env['property.site'].sudo().search([])
                data = []
                for prop in sites:
                    data.append({
                        "id": prop.id,
                        "name": prop.name,

                    })
            elif name and name == "country":
                countries = request.env['res.country'].sudo().search([])
                data = []
                for prop in countries:
                    data.append({
                        "id": prop.id,
                        "phone_code": prop.phone_code,
                        "name": prop.name,

                    })
            elif name and name == "source":
                sources = request.env['utm.source'].sudo().search([])
                data = []
                for prop in sources:
                    data.append({
                        "id": prop.id,
                        "name": prop.name,

                    })
            else:
                return request.make_response(
                    json.dumps({"status": 500, "error": "Please request with valid name => site/country/source"}),
                    headers={'Content-Type': 'application/json'}
                )
            return request.make_response(
                json.dumps({"status": 200, "data": data}),
                headers={'Content-Type': 'application/json'}
            )

        except Exception as e:
            return request.make_response(
                json.dumps({"status": 500, "error": str(e)}),
                headers={'Content-Type': 'application/json'}
            )

    @route('/api/myPipeline', type='http', auth='none', csrf=False, methods=['GET'])
    def get_my_activity(self, **kwargs):
        try:
            session_id = request.httprequest.cookies.get('session_id')
            if not session_id:
                return request.make_response(
                    json.dumps({"status": 401, "error": "Unauthorized: No session found"}),
                    headers={'Content-Type': 'application/json'}
                )
            request.session.rotate = False
            user_id = request.session.uid
            if not user_id:
                return request.make_response(
                    json.dumps({"status": 401, "error": "Unauthorized: Invalid session"}),
                    headers={'Content-Type': 'application/json'}
                )

            # Get the user record
            user = request.env['res.users'].sudo().browse(user_id)

            if not user.exists():
                return request.make_response(
                    json.dumps({"status": 401, "error": "Unauthorized: User not found"}),
                    headers={'Content-Type': 'application/json'}
                )

            leads = request.env['crm.lead'].sudo().search([('user_id','=',user_id)])

            # Prepare property data for response
            data = []
            for prop in leads:
                data.append({
                    "id": prop.id,
                    "name": prop.name,
                    "customer": prop.customer_name,
                    "reservation_count": prop.reservation_count,
                    "stage": {"id": prop.stage_id.id, "name": prop.stage_id.name} if prop.stage_id else None,
                })
            return request.make_response(
                json.dumps({"status": 200, "data": data}),
                headers={'Content-Type': 'application/json'}
            )

        except Exception as e:
            return request.make_response(
                json.dumps({"status": 500, "error": str(e)}),
                headers={'Content-Type': 'application/json'}
            )

    @route('/api/myPipelineDetail', type='http', auth='none', csrf=False, methods=['GET'])
    def get_my_activity_detail(self,id=None, **kwargs):
        try:
            session_id = request.httprequest.cookies.get('session_id')
            if not session_id:
                return request.make_response(
                    json.dumps({"status": 401, "error": "Unauthorized: No session found"}),
                    headers={'Content-Type': 'application/json'}
                )
            request.session.rotate = False
            user_id = request.session.uid
            if not user_id:
                return request.make_response(
                    json.dumps({"status": 401, "error": "Unauthorized: Invalid session"}),
                    headers={'Content-Type': 'application/json'}
                )

            # Get the user record
            user = request.env['res.users'].sudo().browse(user_id)

            if not user.exists():
                return request.make_response(
                    json.dumps({"status": 401, "error": "Unauthorized: User not found"}),
                    headers={'Content-Type': 'application/json'}
                )
            if id:
                lead = request.env['crm.lead'].sudo().search([('id', '=', int(id)),('user_id', '=', user_id)])
                if lead:
                    data = {
                        "id": lead.id,
                        "name": lead.name,
                        "customer": lead.customer_name,
                        "source_id": lead.source_id.name if lead.source_id else None,
                        "user_id": lead.user_id.name if lead.user_id else None,
                        "site_ids": [{"id": site.id, "name": site.name} for site in lead.site_ids],
                        "phone": [{"id": phone.id, "phone": phone.phone} for phone in lead.phone_ids],
                        "stage": {"id": lead.stage_id.id, "name": lead.stage_id.name} if lead.stage_id else None,
                        "reservation_count": lead.reservation_count,
                    }
                    return request.make_response(
                        json.dumps({"status": 200, "data": data}),
                        headers={'Content-Type': 'application/json'}
                    )
                else:
                    return request.make_response(
                        json.dumps({"status": 404, "error": "Activity with the given id not found"}),
                        headers={'Content-Type': 'application/json'})

            else:
                return request.make_response(
                    json.dumps({"status": 500, "error":"Pleas request by id"}),
                    headers={'Content-Type': 'application/json'}
                )

        except Exception as e:
            return request.make_response(
                json.dumps({"status": 500, "error": str(e)}),
                headers={'Content-Type': 'application/json'}
            )

    @route('/api/properties', type='http', auth='none', csrf=False, methods=['GET'])
    def get_propertieslist(self, **kwargs):
        try:
            session_id = request.httprequest.cookies.get('session_id')
            if not session_id:
                return request.make_response(
                    json.dumps({"status": 401, "error": "Unauthorized: No session found"}),
                    headers={'Content-Type': 'application/json'}
                )
            request.session.rotate = False
            user_id = request.session.uid
            if not user_id:
                return request.make_response(
                    json.dumps({"status": 401, "error": "Unauthorized: Invalid session"}),
                    headers={'Content-Type': 'application/json'}
                )

            # Get the user record
            user = request.env['res.users'].sudo().browse(user_id)

            if not user.exists():
                return request.make_response(
                    json.dumps({"status": 401, "error": "Unauthorized: User not found"}),
                    headers={'Content-Type': 'application/json'}
                )
            properties = request.env['property.property'].sudo().search([])

            # Prepare property data for response
            data = []
            for prop in properties:
                data.append({
                    "id": prop.id,
                    "name": prop.name,
                    "property_type": prop.property_type,
                    "site": prop.site.name if prop.site else None,
                    "site_property_type_id": prop.site_property_type_id.property_type_id.code if prop.site_property_type_id else None,
                    "block": prop.block.name if prop.site else None,
                    "floor_id": prop.floor_id.name if prop.floor_id else None,
                    "gross_area": prop.gross_area,
                    "net_area": prop.net_area,
                    "bedroom": prop.bedroom,
                    "bathroom": prop.bathroom,
                    "price": prop.price,
                    "unit_price": prop.unit_price,
                    "state": prop.state,
                    "reservation_end_date": prop.reservation_end_date.strftime('%Y-%m-%d %H:%M:%S') if prop.reservation_end_date else None,
                    "furnishing": prop.furnishing,
                    "finishing": prop.finishing,
                    "country_id": prop.country_id.name if prop.country_id else None,
                    "city": prop.city_id.name if prop.city_id else None,
                    "sub_city_id": prop.sub_city_id.name if prop.sub_city_id else None,
                    "wereda": prop.wereda,
                    "area": prop.area,
                    "street": prop.street,
                    "payment_structure_id": prop.payment_structure_id.name if prop.payment_structure_id else None,
                })

            # Return a successful JSON response
            return request.make_response(
                json.dumps({"status": 200, "data": data}),
                headers={'Content-Type': 'application/json'}
            )

        except Exception as e:
            # Handle exceptions and return an error response
            return request.make_response(
                json.dumps({"status": 500, "error": str(e)}),
                headers={'Content-Type': 'application/json'}
            )
