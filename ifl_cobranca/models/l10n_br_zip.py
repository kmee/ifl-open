import logging
from odoo import api, models

_logger = logging.getLogger(__name__)

try:
    from erpbrasil.base import misc
except ImportError:
    _logger.error("Biblioteca erpbrasil.base não instalada")

_logger = logging.getLogger(__name__)


class L10nBrZip(models.Model):
    _inherit = "l10n_br.zip"

    @api.multi
    def set_result(self):
        self.ensure_one()
        self._zip_update()
        return {
            "country_id": self.country_id.id,
            "state_id": self.state_id.id,
            "city_id": self.city_id.id,
            "city": self.city_id.name,
            "district": self.district,
            "street_name": (
                ((self.street_type or "") + " " + (self.street or ""))
                if self.street_type
                else (self.street or "")
            ),
            "zip": misc.format_zipcode(self.zip_code, self.country_id.code),
        }
