# Copyright 2020 KMEE
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models, _
from urllib.parse import quote
import decimal


class SaleOrder(models.Model):

    _inherit = 'sale.order'

    donation_price = fields.Float(
        string="Contribuição",
        required=False,
        )

    def descriptive_link(self):
        picking_id = self.picking_ids
        if len(picking_id) > 1:
            # todo user error
            pass

        # MESSAGE HEADER
        header = 'Olá, %s,\n\n' \
                 'Agradecemos por sua compra no Instituto Feira Livre!\n\n' \
                 'Em função de indisponibilidades em estoque ou de ' \
                 'variações de valor de produtos comercializados por peso, ' \
                 'seu pedido %s sofreu alterações.\n\n' % (
                    self.partner_invoice_id.name, self.name)

        # QTY CHANGED PRODUCTS
        altered_products = []
        altered_message = ''
        for line in picking_id.move_line_ids_without_package:
            if line.product_uom_qty != line.qty_done:
                altered_products.append(line)
        if altered_products:
            altered_message = 'Os seguintes itens são vendidos por quilo, e ' \
                              'as quantidades sofreram ligeiras alterações ' \
                              'no momento da pesagem dos produtos:\n\n'
            for line in altered_products:
                msg_line = '- %s. Solicitado: %.3f (R$ %.2f), quantidade ' \
                           'selecionada: %.3f (R$ %.2f)\n' % \
                           (line.product_id.display_name,
                            line.product_uom_qty,
                            line.product_uom_qty *
                            line.product_id.standard_price,
                            line.qty_done,
                            line.qty_done *
                            line.product_id.standard_price)
                altered_message += msg_line

        # MISSING PRODUCTS
        missing_message = ''
        missing_product_lines = picking_id.move_ids_without_package.filtered(
            lambda move: not move.move_line_ids)
        if missing_product_lines:
            missing_message = '\nOs seguintes itens não estão mais ' \
                              'disponíveis em estoque:\n\n'
            for line in missing_product_lines:
                msg_line = '- %s. Solicitado: %.3f (R$ %.2f)\n' % \
                           (line.product_id.display_name,
                            line.product_uom_qty,
                            line.product_uom_qty *
                            line.product_id.standard_price)
                missing_message += msg_line

        # REPLACEMENT PRODUCTS
        replacement_message = ''
        replacement_product_lines = picking_id.move_ids_without_package\
            .filtered(lambda move: move.sale_line_id.is_replacement == 1)\
            .mapped('move_line_ids')
        if replacement_product_lines:
            replacement_message = '\nComo alternativa sugerimos os ' \
                                  'seguintes itens em substituição, para ' \
                                  'os quais precisamos de sua aprovação:\n\n'
            for line in replacement_product_lines:
                msg_line = '- %s. Quantidade: %.3f (R$ %.2f)\n' % \
                           (line.product_id.display_name,
                            line.qty_done,
                            line.qty_done *
                            line.product_id.standard_price)
                replacement_message += msg_line

        # FINAL PRODUCTS
        order_total = 0
        final_order_message = '\nOs demais itens solicitados serão faturados' \
                              ' e entregues normalmente.\n\nIMPORTANTE: ' \
                              'Devido a estas alterações e conforme os ' \
                              'termos de uso de nosso site, aguardamos sua ' \
                              'autorização para a realização das ' \
                              'substituições sugeridas.\n\nApós sua ' \
                              'autorização, estornaremos o valor pago ' \
                              'originalmente, e efetuaremos uma nova ' \
                              'cobrança no valor correspondente à nova ' \
                              'composição de sua compra.\n\nCaso você ' \
                              'autorize todas as substituições acima, ' \
                              'esta será a composição de sua compra:\n'
        for line in picking_id.move_line_ids_without_package:
            msg_line = '- %s. (%.3f): R$ %.2f\n' % \
                       (line.product_id.display_name,
                        line.qty_done,
                        line.qty_done *
                        line.product_id.standard_price)
            final_order_message += msg_line
            order_total += line.qty_done * line.product_id.standard_price
        # DONATION
        donation_price = self.get_donation_price()
        final_order_message += '- Contribuição IFL (35): R$ %.2f\n' % \
            donation_price
        order_total += donation_price
        # FREIGHT
        final_order_message += '- Frete: R$ %.2f\n' % \
                               self.carrier_id.rate_shipment(self)['price']
        order_total += self.carrier_id.rate_shipment(self)['price']
        # TOTAL
        final_order_message += '- Total: R$ %.2f\n' % (order_total)

        final_order_message += '\nCaso você não autorize alguma das ' \
                               'substituições sugeridas, o valor ' \
                               'correspondente será subtraído deste total.'

        # SEND MESSAGE
        if not self.partner_invoice_id.phone:
            # todo validation error
            pass
        number_str = '55' + self.partner_invoice_id.phone

        text_str = header + altered_message + missing_message + \
            replacement_message + final_order_message
        address = 'https://web.whatsapp.com/send?phone=%s&text=%s' % \
                  (number_str, quote(text_str))

        # print(text_str)
        self.whatsapp_descriptive_link = address

        return {
            'name': 'Go to whatsapp',
            'res_model': 'ir.actions.act_url',
            'type': 'ir.actions.act_url',
            'target': 'new',
            'url': address
            }

    def simple_link(self):
        text_str = 'Olá %s' % self.partner_invoice_id.name
        number_str = '55' + self.partner_invoice_id.phone
        address = 'https://web.whatsapp.com/send?phone=%s&text=%s' % \
                  (number_str, quote(text_str))

        return {
            'name': 'Go to whatsapp',
            'res_model': 'ir.actions.act_url',
            'type': 'ir.actions.act_url',
            'target': 'new',
            'url': address
            }

    # def update_order(self):
    #     # keep freight
    #     freight = self.amount_freight
    #
    #     charge_pricelist = self.env['ir.config_parameter'].sudo().get_param(
    #         'theme_clarico.default_website_pricelist_charge')
    #
    #     order_line = self.env['sale.order.line'].sudo()
    #
    #     #TODO: melhorar obtenção de donation (talvez buscar pela flag is donation)
    #     donation_product_id = self.env['product.product'].sudo().search(
    #         [('name', '=', 'Donation')])
    #
    #     donation_order_line_id = self.order_line.file('donation')
    #     if not donation_order_line_id:
    #         donation_order_line_id = order_line.create({
    #             'product_id': donation_product_id.id,
    #             'price_total': self.amount_gross * 0.35,
    #             'price_unit': self.amount_gross * 0.35,
    #             'order_id': self.id,
    #             })
    #     else:
    #         donation_order_line_id.write({
    #             'price_total': self.amount_gross * 0.35,
    #             'price_unit': self.amount_gross * 0.35,
    #         })
    #
    #     # donation_order_line_id._onchange_product_id_fiscal()
    #     donation_order_line_id._onchange_commercial_quantity()
    #     donation_order_line_id._onchange_ncm_id()
    #     donation_order_line_id._onchange_fiscal_operation_id()
    #     donation_order_line_id._onchange_fiscal_operation_line_id()
    #     donation_order_line_id._onchange_fiscal_taxes()
    #     donation_order_line_id._onchange_fiscal_tax_ids()
    #
    #     # restore freight
    #     self.amount_freight = freight

    def enable_payment_token(self):
        # enable payment_token
        transaction_id = self.env['payment.transaction'].search(
            [('sale_order_ids', '=', self.id)])
        transaction_id.payment_token_id.active = True

    def request_customer_approval(self):
        new_line = '%0A'

        number_str = '55' + self.partner_invoice_id.phone

        products = []
        quantities = []
        # add requested products (exclude donation)
        for order_line in self.order_line:
            if order_line.product_id.default_code != 'DON':
                products.append(order_line.product_id)
                quantities.append(order_line.product_uom_qty)

        # get product names
        product_ref = self.env['product.product']
        product_names = ''
        for p in products:
            if product_names == '':
                product_names = p.display_name
            else:
                product_names += ', %s ' % p.display_name

        if len(products) > 1:
            text_str = 'Olá %s! Infelizmente os produtos %s não estão ' \
                       'disponíveis para o seu pedido %s. ' % (
                           self.partner_invoice_id.name, product_names,
                           self.name)
        else:
            text_str = 'Olá %s! Infelizmente o produto %s não está ' \
                       'disponível para o seu pedido %s. ' % (
                           self.partner_invoice_id.name, product_names,
                           self.name)

        address = 'https://web.whatsapp.com/send?phone=%s&text=%s' % \
                  (number_str, quote(text_str))

    def update_donation(self):
        for order in self:
            valid_lines = order.order_line.filtered(
                lambda l: l.product_id.donation != True)
            order_subtotal = sum(
                line.price_unit * line.qty_delivered for line in valid_lines)

            donation_line = order.order_line - valid_lines
            if donation_line:
                donation_line.qty_delivered = order_subtotal
                donation_line.price_unit = 0.35
                # TODO setar qty_delivery OU qty_delivered_manual
                # donation_line.qty_delivered_manual =
                #   order_subtotal * donation_line.price_unit

    def get_donation_price(self):
        valid_lines = self.order_line.filtered(
            lambda l: l.product_id.default_code != 'DON')
        order_subtotal = sum(
            line.price_unit * line.move_ids.move_line_ids.qty_done for line in
            valid_lines)
        decimal.getcontext().rounding = decimal.ROUND_CEILING
        return float(
            round(decimal.Decimal(str(order_subtotal * 0.35)), ndigits=2))

    @api.multi
    def recompute_freight_distribution(self):
        order_total = 0
        parcial_freight_applied = 0
        last_line = 0

        amount_freight = self.carrier_id.rate_shipment(self)['price']

        valid_lines = self.order_line.filtered(
            lambda l: l.product_id.donation != True)

        for line in valid_lines:
            order_total += line.qty_delivered * line.price_unit

        for line in valid_lines:
            if line != valid_lines[-1]:
                line_freight = amount_freight * \
                               line.qty_delivered * \
                               line.price_unit / \
                               order_total
                line.freight_value = line_freight
                parcial_freight_applied += line_freight
            else:
                # use subtraction for last line
                line.freight_value = amount_freight - parcial_freight_applied
                last_line = line

        # fix 1 cent divergence
        if last_line and amount_freight != self.amount_freight_value:
            last_line.freight_value += amount_freight - self.amount_freight_value


class Picking(models.Model):
    _inherit = 'stock.picking'

    @api.multi
    def action_done(self):
        result = super(Picking, self).action_done()

        for record in self.filtered(
                lambda ot: ot.picking_type_id.code == 'outgoing'
        ):
            record.sale_id.update_donation()
            record.sale_id.recompute_freight_distribution()

        return result

    # def prepare_sale_make_invoice(self):
    #     if self.picking_type_code == 'outgoing':
    #         ctx = {
    #             'active_model': 'sale.order',
    #             'active_id': self.sale_id.id,
    #             'active_ids': self.sale_id.ids,
    #             }
    #
    #         return {
    #             'type': 'ir.actions.act_window',
    #             'res_model': "sale.advance.payment.inv",
    #             'view_type': 'form',
    #             'view_mode': 'form',
    #             'target': 'new',
    #             'context': ctx,
    #             }
    #     else:
    #         return {
    #             'type': 'ir.actions.act_window',
    #             'res_model': "stock.invoice.onshipping",
    #             'view_type': 'form',
    #             'view_mode': 'form',
    #             'target': 'new',
    #             }

    def action_descriptive_link(self):
        return self.sale_id.descriptive_link()

    def cancel_move(self):
        self._action_cancel()

    def replace_move(self):
        self._action_cancel()


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    is_replacement = fields.Boolean(
        string="Substituição?",
        required=False,
        )


class StockMove(models.Model):
    _inherit = "stock.move"

    def cancel_move(self):
        self._action_cancel()
