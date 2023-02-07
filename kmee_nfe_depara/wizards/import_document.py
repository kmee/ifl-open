# Copyright (C) 2022  Renan Hiroki Bastos - Kmee
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

import base64

from odoo import _, api, fields, models
from odoo.exceptions import UserError, MissingError


class NfeImport(models.TransientModel):
    """Importar XML Nota Fiscal Eletrônica"""

    _inherit = "l10n_br_nfe.import_xml"

    nat_op = fields.Char(string="Natureza da Operação")

    def _search_supplierinfo(self, partner_id, product_name, product_code):
        return self.env["product.supplierinfo"].search(
            [
                ("name", "=", partner_id.id),
                "|",
                ("product_name", "=", product_name),
                ("product_code", "=", product_code),
            ],
            limit=1,
        )

    def _get_product_supplierinfo(self):
        for product_line in self.imported_products_ids:
            product_supplierinfo = self._search_supplierinfo(self.partner_id, product_line.product_name, product_line.product_code)
            if product_supplierinfo:
                product_line.product_id = product_supplierinfo.product_id
                product_line.uom_internal = product_supplierinfo.partner_uom

    def _set_product_supplierinfo(self, edoc):
        for product_line in self.imported_products_ids:
            product_supplierinfo = self._search_supplierinfo(edoc.partner_id, product_line.product_name, product_line.product_code)
            values = {
                "product_id": product_line.product_id.id,
                "product_name": product_line.product_name,
                "product_code": product_line.product_code,
                "price": self.env["uom.uom"]
                .browse(product_line.uom_internal.id)
                ._compute_price(
                    product_line.price_unit_com, product_line.product_id.uom_id
                ),
                "partner_uom": product_line.uom_internal.id,
            }
            if product_supplierinfo and product_supplierinfo.product_id == product_line.product_id:
                product_supplierinfo.update(values)
            else:
                if product_supplierinfo:
                    product_supplierinfo.unlink()
                values["name"] = edoc.partner_id.id
                supplier_info = self.env["product.supplierinfo"].create(values)
                supplier_info.product_id.write({"seller_ids": [(4, supplier_info.id)]})

    def _set_partner_product_name(self, edoc):
        for document_line in edoc.line_ids:
            product_line = self.imported_products_ids.filtered(lambda l: l.product_id == document_line.product_id)[0]
            document_line.partner_product_name = product_line.product_name
            document_line.partner_product_code = product_line.product_code

    @api.onchange("nfe_xml")
    def _onchange_partner_id(self):
        super(NfeImport, self)._onchange_partner_id()
        if self.nfe_xml:
            parsed_xml, document = self._parse_xml_import_wizard(
                base64.b64decode(self.nfe_xml)
            )
            self.nat_op = parsed_xml.infNFe.ide.natOp
            if self.partner_id:
                self._get_product_supplierinfo()
        for line in self.imported_products_ids:
            line.onchange_product_id()
        return

    def _parse_xml_import_wizard(self, xml):
        parsed_xml, document = super(NfeImport, self)._parse_xml_import_wizard(xml)
        parsed_xml = self._edit_parsed_xml(parsed_xml)
        return parsed_xml, document

    def _check_product_data(self):
        for product_line in self.imported_products_ids:
            err_msg = ""
            if not product_line.product_id:
                err_msg += "referência interna"
            if not product_line.uom_internal:
                if err_msg:
                    err_msg += " e "
                err_msg += "unidade de medida"
            if err_msg:
                raise UserError(
                    _(
                        """Há pelo menos uma linha sem {}.
                         Selecione uma {} para cada linha
                         para continuar.""".format(
                            err_msg, err_msg
                        )
                    )
                )

    def _check_ncm(self, xml_product, wizard_product):
        if (
            wizard_product.ncm_id
            and hasattr(xml_product, "NCM")
            and xml_product.NCM
            and xml_product.NCM != wizard_product.ncm_id.code.replace(".", "")
        ):
            raise UserError(
                _(
                    """O NCM do produto {} no cadastro interno é diferente do NCM
                     na nota. Selecione qual NCM deve ser utilizado.\nNCM interno: {}\nNCM na nota: {}""".format(
                        wizard_product.display_name,
                        wizard_product.ncm_id.code,
                        xml_product.NCM,
                    )
                )
            )

    def _edit_parsed_xml(self, parsed_xml):
        for product_line in self.imported_products_ids:
            internal_product = product_line.product_id
            if not internal_product:
                continue
            for xml_product in parsed_xml.infNFe.det:
                if xml_product.prod.cProd == product_line.product_code and xml_product.prod.xProd == product_line.product_name:
                    product_line.choose_ncm(xml_product)
                    self._check_ncm(xml_product.prod, product_line.product_id)
                    xml_product.prod.xProd = internal_product.name
                    xml_product.prod.cProd = internal_product.default_code
                    xml_product.prod.cEAN = internal_product.barcode
                    xml_product.prod.cEANTrib = internal_product.barcode
                    xml_product.prod.uCom = product_line.uom_internal.code
                    if product_line.new_cfop_id:
                        xml_product.prod.CFOP = product_line.new_cfop_id.code
        return parsed_xml

    @api.multi
    def import_nfe_xml(self):
        self._check_product_data()
        res = super(NfeImport, self).import_nfe_xml()
        edoc = self.env["l10n_br_fiscal.document"].browse(res.get("res_id"))
        self._set_product_supplierinfo(edoc)
        self._set_partner_product_name(edoc)
        return res

    def _check_nfe_xml_products(self, parsed_xml):
        product_ids = []
        for product in parsed_xml.infNFe.det:
            vICMS = 0
            pICMS = 0
            pIPI = 0
            vIPI = 0
            icms_tags = [tag for tag in dir(product.imposto.ICMS) if tag.startswith("ICMS")]
            ipi_trib = None
            for tag in icms_tags:
                if getattr(product.imposto.ICMS, tag) is not None:
                    icms_choice = getattr(product.imposto.ICMS, tag)
            if hasattr(icms_choice, "pICMS"):
                pICMS = icms_choice.pICMS
            if hasattr(icms_choice, "vICMS"):
                vICMS = icms_choice.vICMS
            if hasattr(product.imposto, 'IPI') and hasattr(product.imposto.IPI, 'IPITrib'):
                ipi_trib = product.imposto.IPI.IPITrib
            if ipi_trib is not None:
                if hasattr(ipi_trib, "pIPI"):
                    pIPI = ipi_trib.pIPI
                if hasattr(ipi_trib, "vIPI"):
                    vIPI = ipi_trib.vIPI
            product_ids.append(
                self.env["l10n_br_nfe.import_xml.products"]
                .create(
                    {
                        "product_name": product.prod.xProd,
                        "product_code": product.prod.cProd,
                        "ncm_xml": product.prod.NCM,
                        "cfop_xml": product.prod.CFOP,
                        "icms_percent": pICMS,
                        "icms_value": vICMS,
                        "ipi_percent": pIPI,
                        "ipi_value": vIPI,
                        "uom_internal": self.env['uom.uom'].search([("code", "=", product.prod.uCom)], limit=1).id,
                        "uom_com": product.prod.uCom,
                        "quantity_com": product.prod.qCom,
                        "price_unit_com": product.prod.vUnCom,
                        "uom_trib": product.prod.uTrib,
                        "quantity_trib": product.prod.qTrib,
                        "price_unit_trib": product.prod.vUnTrib,
                        "total": product.prod.vProd,
                        "import_xml_id": self.id,
                    }
                )
                .id
            )
        if product_ids:
            self.imported_products_ids = [(6, 0, product_ids)]


class NfeImportProducts(models.TransientModel):
    _inherit = "l10n_br_nfe.import_xml.products"

    product_code = fields.Char(string="Código do Produto do Parceiro")

    product_id = fields.Many2one(
        comodel_name="product.product",
        string="Referencia Interna do Produto",
    )

    uom_internal = fields.Many2one(
        "uom.uom",
        "UOM Interna",
        help="Internal UoM, equivalent to the comercial one in the document",
    )

    ncm_xml = fields.Char(string="Código NCM no XML")

    ncm_internal = fields.Char(string="Código NCM Interno", related='product_id.ncm_id.code')

    ncm_match = fields.Boolean(string="NCMs iguais", default=False)

    ncm_choice = fields.Selection(
        string='Escolha de NCM',
        selection=[('xml', 'NCM do XML'),
                   ('internal', 'NCM Interno'), ],
        required=False,
    )

    cfop_xml = fields.Char(string="CFOP no XML")

    new_cfop_id = fields.Many2one(comodel_name="l10n_br_fiscal.cfop", string="Alterar CFOP", default=False, required=False)

    icms_percent = fields.Char(string="Alíquota ICMS")

    icms_value = fields.Char(string="Valor ICMS")

    ipi_percent = fields.Char(string="Alíquota IPI")

    ipi_value = fields.Char(string="Valor IPI")

    @api.onchange("product_id")
    def onchange_product_id(self):
        self.ncm_match = False
        ncm_internal = ''
        ncm_xml = ''
        if self.product_id:
            ncm_internal = self.product_id.ncm_id.code.replace(".", "")
        if self.ncm_xml:
            ncm_xml = self.ncm_xml.replace(".", "")
        if ncm_internal and ncm_xml and ncm_internal == ncm_xml:
            self.ncm_choice = False
            self.ncm_match = True

    def choose_ncm(self, xml_product):
        if self.ncm_match is False:
            if self.ncm_choice == 'xml':
                ncm_id = self.env['l10n_br_fiscal.ncm'].search([('code_unmasked', '=', xml_product.prod.NCM)])
                if len(ncm_id) > 1:
                    ncm_id = ncm_id.filtered(lambda n: not n.name.startswith(".Ex ")
                                             and not n.name.startswith("Ex "))
                if ncm_id:
                    self.product_id.ncm_id = ncm_id
                else:
                    raise MissingError("Ncm do XML não foi encontrado.")
            elif self.ncm_choice == 'internal':
                xml_product.prod.NCM = self.product_id.ncm_id.code.replace(".", "")
