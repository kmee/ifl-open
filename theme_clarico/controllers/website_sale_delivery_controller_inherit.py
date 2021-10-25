from odoo import http, _
from odoo.http import request
from odoo.addons.website_sale_delivery.controllers.main import WebsiteSaleDelivery


class WebsiteSaleDeliveryInherit(WebsiteSaleDelivery):

    def _get_shop_payment_values(self, order, **kwargs):
        values = super(WebsiteSaleDeliveryInherit, self)._get_shop_payment_values(order, **kwargs)

        replace_strategies = request.env['product.replace.strategy'].sudo().search([])
        values['replace_strategies'] = replace_strategies

        return values

    @http.route(['/shop/update_strategy'], type='json', auth='public', methods=['POST'], website=True, csrf=False)
    def update_shop_strategy(self, **post):
        if 'strategy_id' in post and post['strategy_id']:
            order = request.website.sale_get_order()
            if order:
                order._strategy_update(post['strategy_id'])
        if 'strategy_obs' in post and post['strategy_obs']:
            order = request.website.sale_get_order()
            if order:
                order._strategy_obs_update(post['strategy_obs'])
        if 'contribution' in post and post['contribution']:
            order = request.website.sale_get_order()
            if order:
                order._donation_percentage_update(post['contribution'])
