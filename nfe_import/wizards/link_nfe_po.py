# Copyright 2022 KMEE (Renan Hiroki Bastos <renan.hiroki@kmee.com.br>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models
from odoo.exceptions import UserError

from datetime import datetime

# TODO: Reformatar variáveis deste modelo, estão totalmente inconsistentes entre os métodos
class LinkNFePO(models.TransientModel):
    _name = "nfe_import.link_nfe_po"
    _inherit = "l10n_br_fiscal.base.wizard.mixin"

    entry_type = fields.Selection(
        string='Tipo de Recebimento',
        selection=[('automatico', 'Automático'),
                   ('manual', 'Manual'),
                   ],
        required=True,
        help="Tipo de Recebimento:"
             "\nAutomático - As quantidades a serem recebidas serão preenchidas automaticamente"
             "\ncom os valores do Documento Fiscal e conversão unidade de medida."
             "\nManual - As quantidades a serem recebidas devem preenchidas manualmente."
    )

    origin_model = fields.Selection(
        string='Origin Model',
        selection=[('purchase', 'purchase'),
                   ('document', 'document'),
                   ],
        required=False,
    )

    linked = fields.Boolean(
        string='Linked',
        required=False,
        default=False,
    )

    link_or_create_po = fields.Selection(
        string='Tipo de Conciliação',
        selection=[('link', 'Conciliar com OC existente'),
                   ('create', 'Criar nova OC'), ],
        required=False,
    )

    purchase_id = fields.Many2one(
        comodel_name='purchase.order',
        string='Purchase Order',
        domain="[('state','=', 'purchase'), ('imported_nfe_id', '=', False), ('partner_id', '=', partner_id)]",
        required=False,
        default=False,
    )

    purchase_partner_id = fields.Many2one(
        related='purchase_id.partner_id',
    )

    purchase_partner_ref = fields.Char(
        related='purchase_id.partner_ref',
    )

    purchase_date_order = fields.Datetime(
        related='purchase_id.date_order',
    )

    purchase_fiscal_operation_id = fields.Many2one(
        related='purchase_id.fiscal_operation_id',
    )

    purchase_order_line = fields.One2many(
        related='purchase_id.order_line',
    )

    nfe_id = fields.Many2one(
        comodel_name='l10n_br_fiscal.document',
        string='Documento Fiscal',
        domain="[('imported_document','=', True), ('purchase_id', '=', False), ('partner_id', '=', partner_id)]",
        required=False,
        default=False,
    )

    nfe_partner_id = fields.Many2one(
        related='nfe_id.partner_id',
    )

    nfe_document_date = fields.Datetime(
        related='nfe_id.document_date',
    )

    nfe_document_type = fields.Many2one(
        comodel_name='l10n_br_fiscal.document.type',
        related='nfe_id.document_type_id'
    )
    nfe_document_number = fields.Char(
        related='nfe_id.document_number'
    )
    nfe_document_key = fields.Char(
        related='nfe_id.document_key'
    )

    nfe_line_ids = fields.One2many(
        related='nfe_id.line_ids'
    )

    new_date_order = fields.Datetime(
        string='Data do Pedido',
        required=False
    )

    new_date_planned = fields.Datetime(
        string='Data de Entrega',
        required=False
    )

    def link_nfe_po(self):
        # Get pruchase.order and fiscal.document depending on where wizard was openned from
        if self.origin_model == 'document':
            if not self.link_or_create_po:
                raise UserError(_("Selecione um tipo de conciliação."))
            if self.link_or_create_po == 'link' and not self.purchase_id:
                raise UserError(_("Selecione uma Ordem de Compra."))
            document = self.document_id
            purchase = self.purchase_id
        elif self.origin_model == 'purchase':
            if not self.nfe_id:
                raise UserError(_("Selecione um documento."))
            document = self.nfe_id
            purchase = self.env['purchase.order'].browse(self.env.context.get('active_id'))
            self.purchase_id = purchase

        if self.origin_model == 'document' and self.link_or_create_po == 'create':
            # If create new PO opition was chosen, do it here
            company = self.env.user.company_id
            vals = {
                'partner_id': document.partner_id.id,
                'currency_id': company.currency_id.id,
                'fiscal_operation_id': company.purchase_fiscal_operation_id.id,
                'date_order': self.new_date_order or datetime.now(),
            }
            purchase = self.env['purchase.order'].create(vals)
            new_purchase_lines = []
            for document_line in document.line_ids:
                product_uom = self.env['uom.uom'].browse(document_line.uom_id).id or document_line.product_id.uom_id,
                new_line_dict = {
                    'product_id': document_line.product_id.id,
                    'name': document_line.product_id.seller_ids.filtered(lambda n: n.name == document_line.partner_id)[
                        0].product_name,
                    'date_planned': self.new_date_planned or datetime.now(),
                    'product_qty': document_line.quantity,
                    'product_uom': product_uom[0].id,
                    'price_unit': document_line.price_unit,
                    'price_subtotal': document_line.amount_total,
                    'order_id': purchase.id,
                }
                new_line_dict.update(self.fill_tax_fields(document_line))
                new_purchase_line = self.env['purchase.order.line'].create(new_line_dict)
                new_purchase_lines.append(new_purchase_line.id)
            purchase.write({'order_line': [(6, 0, new_purchase_lines)]})
            purchase.button_confirm()
            self.purchase_id = purchase
        else:
            # Otherwise check if products from purchase.order and fiscal.document match
            for document_line in document.line_ids:
                flag = False
                for purchase_line in purchase.order_line:
                    if document_line.product_id == purchase_line.product_id:
                        purchase_line.update(self.fill_tax_fields(document_line))
                        flag = True
                        continue
                if not flag:
                    raise UserError(_("Os produtos do Documento Fiscal e da Ordem de Compra não podem ser diferentes."))

        # Create link between records
        document.purchase_id = purchase

        self._process_entry()

        # Open purchase order form view
        result = self.env.ref('nfe_import.action_purchase').read()[0]
        result['context'] = {}
        res = self.env.ref('purchase.purchase_order_form', False)
        result['views'] = [(res and res.id or False, 'form')]
        result['res_id'] = purchase.id
        return result

    def choose_entry_type(self):
        self._process_entry()
        result = self.env.ref('nfe_import.action_purchase').read()[0]
        result['context'] = {}
        res = self.env.ref('purchase.purchase_order_form', False)
        result['views'] = [(res and res.id or False, 'form')]
        result['res_id'] = self.purchase_id.id
        return result

    def fill_tax_fields(self, document_line):
        new_vals = {}
        new_vals.update(self.fill_icms_fields(document_line))
        new_vals.update(self.fill_ipi_fields(document_line))
        new_vals.update(self.fill_pis_fields(document_line))
        new_vals.update(self.fill_cofins_fields(document_line))
        return new_vals

    def fill_icms_fields(self, document_line):
        new_vals = {
            'icms_tax_id': document_line.icms_tax_id.id,
            'icms_cst_id': document_line.icms_cst_id.id,
            'icms_origin': document_line.icms_origin,
            'icms_base_type': document_line.icms_base_type,
            'icms_base': document_line.icms_base,
            'icms_percent': document_line.icms_percent,  # Talvez não exista
            'icms_value': document_line.icms_value,  # Talvez não exista
            'icms_relief_id': document_line.icms_relief_id.id,
            'icms_relief_value': document_line.icms_relief_value,
            'icms_substitute': document_line.icms_substitute,
            'icmsfcp_tax_id': document_line.icmsfcp_tax_id.id,
            'icmsfcp_base': document_line.icmsfcp_base,
            'icmsfcp_percent': document_line.icmsfcp_percent,
            'icmsfcp_value': document_line.icmsfcp_value,
            'icms_destination_base': document_line.icms_destination_base,
            'icms_origin_percent': document_line.icms_origin_percent,
            'icms_destination_percent': document_line.icms_destination_percent,
            'icms_sharing_percent': document_line.icms_sharing_percent,
            'icms_origin_value': document_line.icms_origin_value,
            'icms_destination_value': document_line.icms_destination_value,
        }
        return new_vals

    def fill_ipi_fields(self, document_line):
        new_vals = {
            'ipi_tax_id': document_line.ipi_tax_id.id,
            'ipi_cst_id': document_line.ipi_cst_id.id,
            'ipi_guideline_id': document_line.ipi_guideline_id.id,
            'ipi_base_type': document_line.ipi_base_type,
            'ipi_percent': document_line.ipi_percent,
            'ipi_reduction': document_line.ipi_reduction,
            'ipi_base': document_line.ipi_base,
            'ipi_value': document_line.ipi_value
        }
        return new_vals

    def fill_pis_fields(self, document_line):
        new_vals = {
            'pis_tax_id': document_line.pis_tax_id.id,
            'pis_cst_id': document_line.pis_cst_id.id,
            'pis_credit_id': document_line.pis_credit_id.id,
            'pis_base_id': document_line.pis_base_id.id,
            'pis_base_type': document_line.pis_base_type,
            'pis_percent': document_line.pis_percent,
            'pis_reduction': document_line.pis_reduction,
            'pisst_base': document_line.pisst_base,
            'pisst_value': document_line.pisst_value,
            'pis_wh_tax_id': document_line.pis_wh_tax_id.id,
            'pis_wh_base': document_line.pis_wh_base,
            'pis_wh_percent': document_line.pis_wh_percent,
            'pis_wh_reduction': document_line.pis_wh_reduction,
            'pis_wh_value': document_line.pis_wh_value,
        }
        return new_vals

    def fill_cofins_fields(self, document_line):
        new_vals = {
            'cofins_tax_id': document_line.cofins_tax_id.id,
            'cofins_cst_id': document_line.cofins_cst_id.id,
            'cofins_credit_id': document_line.cofins_credit_id.id,
            'cofins_base_id': document_line.cofins_base_id.id,
            'cofins_base_type': document_line.cofins_base_type,
            'cofins_percent': document_line.cofins_percent,
            'cofins_reduction': document_line.cofins_reduction,
            'cofins_base': document_line.cofins_base,
            'cofins_value': document_line.cofins_value,
            'cofinsst_tax_id': document_line.cofinsst_tax_id.id,
            'cofinsst_cst_id': document_line.cofinsst_cst_id.id,
            'cofinsst_base_type': document_line.cofinsst_base_type,
            'cofinsst_percent': document_line.cofinsst_percent,
            'cofinsst_reduction': document_line.cofinsst_reduction,
            'cofinsst_base': document_line.cofinsst_base,
            'cofinsst_value': document_line.cofinsst_value,
            'cofins_wh_tax_id': document_line.cofins_wh_tax_id.id,
            'cofins_wh_base': document_line.cofins_wh_base,
            'cofins_wh_percent': document_line.cofins_wh_percent,
            'cofins_wh_reduction': document_line.cofins_wh_reduction,
            'cofins_wh_value': document_line.cofins_wh_value,
        }
        return new_vals

    def _process_entry(self):
        # Adjusts done quantities on purchase order's picking with quantities from fiscal document
        # TODO: In the future an option to automate validating the picking and creating an invoice should be implemented
        purchase = self.purchase_id
        document = self.nfe_id or self.document_id
        purchase.entry_type = self.entry_type
        if self.entry_type == 'automatico':
            if len(purchase.picking_ids) > 1:
                raise UserError(
                    _('A Ordem de Compra possuí mais de uma entrega. Recebimentos automáticos não são possíveis. Utilize o recebimento manual.'))
            picking = purchase.picking_ids
            for picking_line in picking.move_ids_without_package:
                flag = False
                for document_line in document.line_ids:
                    if picking_line.product_id == document_line.product_id:
                        flag = True
                        picking_line.quantity_done = self.env['uom.uom'].browse(document_line.uom_id.id)._compute_quantity(document_line.quantity, picking_line.product_uom)
                        continue
                if not flag:
                    raise UserError(_("Os produtos do Documento Fiscal e da Entrega não podem ser diferentes."))

    @api.model
    def default_get(self, fields):
        res = super(LinkNFePO, self).default_get(fields)
        if 'origin_model' in res and res['origin_model'] == 'purchase':
            purchase_id = self.env.context.get('active_id')
            purchase = self.env['purchase.order'].browse(purchase_id)
            res.update({
                'partner_id': purchase.partner_id.id,
            })
        return res
