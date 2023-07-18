from odoo import models, api


class SpecMixin(models.AbstractModel):
    _inherit = "spec.mixin"

    @api.model
    def _build_attr(self, node, fields, vals, path, attr):
        """
        Builds an Odoo field from a binding attribute.
        """
        value = getattr(node, attr.get_name())
        if value is None or value == []:
            return False
        key = "%s%s" % (
            self._field_prefix,
            attr.get_name(),
        )
        if key == "nfe40_autXML":
            return
        return super(SpecMixin, self)._build_attr(node, fields, vals, path, attr)
