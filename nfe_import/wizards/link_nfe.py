# Copyright 2022 KMEE (Renan Hiroki Bastos <renan.hiroki@kmee.com.br>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models
from odoo.exceptions import UserError

from datetime import datetime

class LinkNFePO(models.TransientModel):
    _name = "nfe_import.link_nfe"
    _inherit = "l10n_br_fiscal.base.wizard.mixin"

    # WIZARD FIELDS

    origin_model = fields.Selection(
        string='Origin Model',
        selection=[('picking', 'picking'),
                   ('purchase', 'purchase'),
                   ('document', 'document'),
                   ],
        required=False,
    )

    link_with = fields.Selection(
        string='Conciliar Com',
        selection=[('purchase', 'Ordem de Compra')],
        default='purchase',
        required=True,
    )

    link_or_create = fields.Selection(
        string='Tipo de Conciliação',
        selection=[('link', 'Conciliar com Documento existente'),
                   ('create', 'Criar novo Documento'), ],
        required=False,
    )

    new_scheduled_date = fields.Datetime(
        string='Data Programada',
        required=False
    )

    new_date_order = fields.Datetime(
        string='Data do Pedido',
        required=False
    )

    new_date_planned = fields.Datetime(
        string='Data de Entrega',
        required=False
    )

    # PURCHASE ORDER FIELDS

    purchase_id = fields.Many2one(
        comodel_name='purchase.order',
        string='Ordem de Compra',
        domain="[('state','=', 'purchase'), ('partner_id', '=', partner_id)]",
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

    # INDUSTRIALIZATION FIELDS

    sale_id = fields.Many2one(
        comodel_name='sale.order',
        string='Ordem de Venda (opcional)',
        domain="[('state','=', 'sale'), ('partner_id', '=', partner_id)]",
    )

    picking_id = fields.Many2one(
        comodel_name='stock.picking',
        string='Documento de Transferência',
        required=False,
        default=False,
    )

    picking_partner_id = fields.Many2one(
        related='picking_id.partner_id',
    )

    picking_scheduled_date = fields.Datetime(
        related='picking_id.scheduled_date',
    )

    picking_date_created = fields.Datetime(
        related='picking_id.date',
    )

    picking_new_fiscal_operation_id = fields.Many2one(
        comodel_name='l10n_br_fiscal.operation',
        string='Operação',
        domain="[('fiscal_operation_type', '=','in')]",
        default=False,
    )

    picking_fiscal_operation_id = fields.Many2one(
        related='picking_id.fiscal_operation_id',
    )

    picking_move_ids_without_package = fields.One2many(
        related='picking_id.move_ids_without_package',
    )

    # L10N_BR_FISCAL.DOCUMENT FIELDS
    nfe_id = fields.Many2one(
        comodel_name='l10n_br_fiscal.document',
        string='Documento Fiscal',
        domain="[('imported_document','=', True), ('partner_id', '=', partner_id)]",
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

    # TODO: Find better way to filter domain
    # Can't use stock.picking sale_id field because it's related to group_id.sale and
    # and group_id.sale_id is related to stock_moves.sale_id
    # Therefore sale_id might be empty
    @api.onchange('sale_id')
    def onchange_sale_id(self):

        domain = {'picking_id': []}
        return {'domain': domain}

    def _get_objects(self):
        # Get industrialization and fiscal.document depending on where wizard was opened from
        if self.origin_model == 'document':
            doc, nfe = self._get_objects_from_nfe()
        elif self.origin_model == 'picking':
            doc, nfe = self._get_objects_from_picking()
        elif self.origin_model == 'purchase':
            doc, nfe = self._get_objects_from_purchase()
        return doc, nfe

    def _get_objects_from_nfe(self):
        if not self.link_or_create:
            raise UserError(_("Selecione um tipo de conciliação."))
        doc = None
        if self.link_with == 'purchase':
            if self.purchase_id:
                doc = self.purchase_id
            elif self.link_or_create == 'link':
                raise UserError(_("Selecione uma Ordem de Compra."))
        else:
            if self.picking_id:
                doc = self.picking_id
            elif self.link_or_create == 'link' and self.link_with == 'industrialization':
                raise UserError(_("Selecione uma Transferência de Industrialização."))
            elif self.link_or_create == 'link' and self.link_with == 'other':
                raise UserError(_("Selecione um Documento de Entrada."))

        return doc, self.document_id

    def _get_objects_from_picking(self):
        if not self.nfe_id:
            raise UserError(_("Selecione um documento."))
        return self.picking_id, self.nfe_id

    def _get_objects_from_purchase(self):
        if not self.nfe_id:
            raise UserError(_("Selecione um documento."))
        return self.purchase_id, self.nfe_id

    def link_nfe(self):
        if self.link_with == 'purchase':
            return self.link_nfe_po()
        else:
            return self.link_nfe_picking()

    def link_nfe_po(self):
        # Get fiscal document and purchase order
        purchase, nfe = self._get_objects()
        if self.origin_model == 'document' and self.link_or_create == 'create':
            # If create new PO opition was chosen, do it here
            purchase = self.create_purchase_order(nfe)
            self.purchase_id = purchase
        # Create link between records
        nfe.write({'linked_purchase_ids': [(4, purchase.id)],})
        self._process_entry()
        # Open purchase order form view
        result = self.env.ref('nfe_import.action_purchase').read()[0]
        result['context'] = {}
        res = self.env.ref('purchase.purchase_order_form', False)
        result['views'] = [(res and res.id or False, 'form')]
        result['res_id'] = purchase.id
        return result

    def link_nfe_picking(self):
        # Get fiscal document and industrialization picking
        picking, nfe = self._get_objects()
        if self.origin_model == 'document' and self.link_or_create == 'create':
            # If create new picking option was chosen, do it here
            if self.link_with == 'industrialization':
                picking = self.create_industrialization(nfe)
            else:
                picking = self.create_picking(nfe)
            self.picking_id = picking
            # Set owner_id to picking if industrialization
            if picking.partner_id and not picking.owner_id:
                picking.owner_id = picking.partner_id
        # Create link between records
        nfe.write({'industrialization_picking_ids': [(4, picking.id)],})
        # Set picking done quantities
        self._process_entry()
        # Open picking form view
        result = self.env.ref('nfe_import.action_picking').read()[0]
        result['context'] = {}
        res = self.env.ref('stock.view_picking_form', False)
        result['views'] = [(res and res.id or False, 'form')]
        result['res_id'] = picking.id
        return result

    def create_purchase_order(self, document):
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
                'origin_nfe_id': document.id,
                'origin_nfe_line_id': document_line.id,
                'name': document_line.product_id.seller_ids.filtered(lambda n: n.name == document_line.partner_id)[
                    0].product_name or document_line.product_id.name,
                'date_planned': self.new_date_planned or datetime.now(),
                'product_qty': document_line.quantity,
                'product_uom': product_uom[0].id,
                'price_unit': document_line.price_unit,
                'price_subtotal': document_line.amount_total,
                'order_id': purchase.id,
            }
            new_purchase_line = self.env['purchase.order.line'].create(new_line_dict)
            new_purchase_lines.append(new_purchase_line.id)
        purchase.write({'order_line': [(6, 0, new_purchase_lines)]})
        purchase.button_confirm()
        return purchase

    def create_picking(self, document):
        StockPicking = self.env['stock.picking']
        company = self.env.user.company_id
        vals = {
            'partner_id': document.partner_id.id,
            'company_id': company.id,
            'currency_id': company.currency_id.id,
            'picking_type_id': self.env.ref('stock.picking_type_in').id,
            'fiscal_operation_id': self.picking_new_fiscal_operation_id.id,
            'date': datetime.now(),
            'scheduled_date': self.new_scheduled_date or datetime.now(),
            'location_dest_id': self.env.ref('stock.picking_type_in').default_location_dest_id.id,
            'location_id': self.env.ref('stock.stock_location_suppliers').id,
            'origin': self.nfe_id.name or self.document_id.name,
        }
        picking_id = StockPicking.create(vals)
        new_stock_moves = []
        for document_line in document.line_ids:
            product_uom = self.env['uom.uom'].browse(document_line.uom_id).id or document_line.product_id.uom_id,
            new_line_dict = {
                'name': document_line.product_id.name,
                'origin_nfe_id': document.id,
                'origin_nfe_line_id': document_line.id,
                'product_id': document_line.product_id.id,
                'date_expected': self.new_scheduled_date or datetime.now(),
                'product_uom_qty': document_line.quantity,
                'fiscal_quantity': document_line.quantity,
                'product_uom': product_uom[0].id,
                'price_unit': document_line.price_unit,
                'invoice_state': 'none',
                'picking_type_id': self.env.ref('stock.picking_type_in').id,
                'location_dest_id': self.env.ref('stock.picking_type_in').default_location_dest_id.id,
                'location_id': self.env.ref('stock.stock_location_suppliers').id,
                'origin': self.nfe_id.name or self.document_id.name,
                'picking_id': picking_id.id,
            }
            new_stock_move = self.env['stock.move'].create(new_line_dict)
            new_stock_moves.append(new_stock_move.id)
        picking_id.write({'move_ids_without_package': [(6, 0, new_stock_moves)]})
        return picking_id

    def create_industrialization(self, document):
        StockPicking = self.env['stock.picking']
        company = self.env.user.company_id
        vals = {
            'partner_id': document.partner_id.id,
            'company_id': company.id,
            'currency_id': company.currency_id.id,
            'picking_type_id': self.env.ref('stock.picking_type_in').id,
            'fiscal_operation_id': self.env.ref('l10n_br_fiscal.fo_entrada_industrializacao').id,
            'date': datetime.now(),
            'scheduled_date': self.new_scheduled_date or datetime.now(),
            'origin': self.sale_id and self.sale_id.name or False,
            'location_dest_id': self.env.ref('stock.picking_type_in').default_location_dest_id.id,
            'location_id': self.env.ref('stock.stock_location_suppliers').id,
        }
        industrialization_id = StockPicking.create(vals)
        if self.sale_id:
            self.sale_id.industrialization_ids += industrialization_id
        new_stock_moves = []
        for document_line in document.line_ids:
            product_uom = self.env['uom.uom'].browse(document_line.uom_id).id or document_line.product_id.uom_id,
            new_line_dict = {
                'name': document_line.product_id.name,
                'origin_nfe_id': document.id,
                'origin_nfe_line_id': document_line.id,
                'product_id': document_line.product_id.id,
                'date_expected': self.new_scheduled_date or datetime.now(),
                'product_uom_qty': document_line.quantity,
                'fiscal_quantity': document_line.quantity,
                'product_uom': product_uom[0].id,
                'price_unit': document_line.price_unit,
                'invoice_state': 'none',
                'picking_type_id': self.env.ref('stock.picking_type_in').id,
                'location_dest_id': self.env.ref('stock.picking_type_in').default_location_dest_id.id,
                'location_id': self.env.ref('stock.stock_location_suppliers').id,
                'origin': self.sale_id and self.sale_id.name or False,
                'picking_id': industrialization_id.id,
            }
            new_stock_move = self.env['stock.move'].create(new_line_dict)
            new_stock_moves.append(new_stock_move.id)
        industrialization_id.write({'move_ids_without_package': [(6, 0, new_stock_moves)]})
        return industrialization_id

    def _process_entry(self):
        doc, nfe = self._get_objects()
        if self.link_with == 'purchase':
            if len(doc.picking_ids) > 1:
                raise UserError(
                    _('A Ordem de Compra possuí mais de uma entrega. Recebimentos automáticos não são possíveis. Realize o recebimento manual.'))
            picking = doc.picking_ids
        else:
            picking = doc
        for nfe_line in nfe.line_ids:
            picking_lines = picking.move_ids_without_package.filtered(lambda pl: pl.origin_nfe_line_id and pl.origin_nfe_line_id.id == nfe_line.id)
            if picking_lines:
                picking_lines[0].quantity_done = nfe_line.uom_id._compute_quantity(nfe_line.quantity, picking_lines[0].product_uom)

    @api.model
    def default_get(self, fields):
        res = super(LinkNFePO, self).default_get(fields)
        if 'origin_model' in res:
            if res['origin_model'] == 'purchase':
                purchase_id = self.env.context.get('active_id')
                purchase_id = self.env['purchase.order'].browse(purchase_id)
                res.update({
                    'purchase_id': purchase_id.id,
                    'partner_id': purchase_id.partner_id.id,
                })
            elif res['origin_model'] == 'picking':
                picking_id = self.env.context.get('active_id')
                picking_id = self.env['stock.picking'].browse(picking_id)
                res.update({
                    'picking_id': picking_id.id,
                    'partner_id': picking_id.partner_id.id,
                })
        return res
