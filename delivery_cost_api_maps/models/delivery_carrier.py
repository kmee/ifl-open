# Copyright 2020 KMEE INFORMATICA LTDA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models, _

from odoo.exceptions import UserError


class DeliveryCarrier(models.Model):
    _inherit = 'delivery.carrier'

    def available_carriers(self, partner):
        googlemaps_api = self.env['googlemaps.api.config'].search([])
        company = self.env.user.company_id
        company_address = company.partner_id._display_address(
            without_company=True
        ).replace('\n', ', ')
        partner_adress = partner._display_address(
            without_company=True
        ).replace('\n', ', ')

        return googlemaps_api.get_distance_cost(
            company_address, partner_adress
        )
