
from odoo import api, fields, models

from odoo.addons import decimal_precision as dp

PRINTER = [
    ("epson-tm-t20", "Epson TM-T20"),
    ("bematech-mp4200th", "Bematech MP4200TH"),
    ("daruma-dr700", "Daruma DR700"),
    ("elgin-i9", "Elgin I9"),
    ("GenericESCPOS", "GenericESCPOS")
]

class PosConfig(models.Model):
    _inherit = "pos.config"

    impressora = fields.Selection(
        selection=PRINTER,
        string="Impressora",
    )


    fiscal_printer_type = fields.Selection(
        selection=[
            ("BluetoothConnection", "Bluetooth"),
            ("DummyConnection", "Dummy"),
            ("FileConnection", "File"),
            ("NetworkConnection", "Network"),
            ("SerialConnection", "Serial"),
            ("USBConnection", "USB"),
            ("CupsConnection", "Cups"),
            ("Windows", "Windows")
        ],


    )