# Copyright 2020 KMEE
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import http
from odoo.http import request

from odoo.addons.portal.controllers.portal import CustomerPortal
from odoo.addons.payment_cielo.controllers.main import CieloController


class CieloPreProcessPayment(CieloController):

    @http.route(['/payment/cielo/s2s/create_json_3ds'], type='json',
                auth='public', csrf=False, website=True)
    def cielo_s2s_create_json_3ds(self, verify_validity=False, **kwargs):
        charge_pricelist = request.env['ir.config_parameter'].sudo().get_param(
            'theme_clarico.default_website_pricelist_charge')
        request.website.sudo().pricelist_id = int(charge_pricelist)

        order = request.website.sale_get_order()
        order.pricelist_id = request.env['product.pricelist'].browse(
            int(charge_pricelist))

        for line in order.order_line:
            line.with_context({'pricelist': int(charge_pricelist)})._onchange_product_id_fiscal()

        order_line = request.env['sale.order.line'].sudo()
        donation_product_id = request.env['product.product'].sudo().search(
            [('donation', '=', True)], limit=1)

        donation_lines = order.order_line.filtered(
            lambda l: l.product_id.donation == True)

        order.order_line = order.order_line - donation_lines

        operation_line = request.env['l10n_br_fiscal.operation.line'].search([
            ('name', '=', 'Doação')
        ])
        uot_id = request.env['l10n_br_fiscal.operation.line'].search([
            ('name', '=', 'Unidade(s)')
        ])

        donation_order_line_id = order_line.create({
            'product_id': donation_product_id.id,
            'product_uom_qty': order.amount_price_gross,
            # 'price_total': order.amount_gross * 0.35,
            'price_unit': 0.35,
            'order_id': order.id,
            'fiscal_operation_line_id': operation_line.id,
            'uot_id': uot_id.id
        })

        donation_order_line_id._onchange_commercial_quantity()

        # donation_order_line_id._onchange_fiscal_operation_line_id()

        return super(CieloPreProcessPayment, self).cielo_s2s_create_json_3ds(
            verify_validity=verify_validity, **kwargs)
