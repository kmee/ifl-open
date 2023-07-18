from odoo import models, fields, api


class SaleAdvancePaymentInv(models.TransientModel):
    _inherit = "sale.advance.payment.inv"

    @api.multi
    def create_invoices(self):
        res = super().create_invoices()
        self.recompute_freight_distribution(res)

        return res

    @api.multi
    def recompute_freight_distribution(self, res):
        invoice_id = self.env["account.invoice"].browse(res.get("res_id", False))

        order_total = 0
        parcial_freight_applied = 0
        last_line = 0

        if not invoice_id.carrier_id:
            return

        amount_freight = invoice_id.carrier_id.rate_shipment(invoice_id)["price"]

        valid_lines = invoice_id.invoice_line_ids.filtered(
            lambda l: l.product_id.donation != True
        )

        for line in valid_lines:
            order_total += line.quantity * line.price_unit

        for line in valid_lines:
            if line != valid_lines[-1]:
                line_freight = (
                    amount_freight * line.quantity * line.price_unit / order_total
                )
                line.freight_value = line_freight
                parcial_freight_applied += line_freight
            else:
                # use subtraction for last line
                line.freight_value = amount_freight - parcial_freight_applied
                last_line = line
            line._onchange_fiscal_operation_line_id()

        invoice_id._onchange_invoice_line_ids()
