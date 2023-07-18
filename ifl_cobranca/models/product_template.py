from odoo.exceptions import ValidationError

from odoo import api, fields, models, _


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    @api.constrains('donation')
    def check_admin(self):
        if (self.donation == True):
            user_admin = self.env.ref('base.user_admin')
            if (user_admin != self.env.user):
                raise ValidationError(
                                _("Somente o Administrador tem permissão para alterar o campo donation")
                            )
