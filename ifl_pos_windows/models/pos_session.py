from odoo import _, api, models
from odoo.exceptions import ValidationError


class PosSession(models.Model):
    _inherit = "pos.session"

    @api.multi
    def action_pos_session_validate(self):
        for session in self:
            for order_id in session.order_ids:
                if len(order_id.lines) == 0:
                    raise ValidationError(
                        f"O pedido {order_id.display_name} não pode ser fechado pois"
                        " não contém linhas"
                    )
