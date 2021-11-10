# Copyright 2020 KMEE INFORMATICA LTDA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import googlemaps

from odoo import api, fields, models, _
from odoo.exceptions import UserError

class GooglemapsApiConfig(models.Model):

    _name = 'googlemaps.api.config'
    _description = 'Googlemaps Api Config'

    name = fields.Char()
    api_key = fields.Char()
    distance_line_ids = fields.One2many(
        comodel_name='googlemaps.api.distance.lines',
        inverse_name='googlemaps_api_id',
        string='Distances'
    )

    default_delivery_method_id = fields.Many2one(
        comodel_name='delivery.carrier',
        string='Default delivery carrier'
    )

    @staticmethod
    def get_min_distance(matrix):
        result = False
        distances = []
        if matrix and matrix.get('rows'):
            for row in matrix['rows']:
                for element in row.get('elements'):
                    if 'distance' in element and element.get('distance').get('value'):
                        distances.append(element['distance']['value'])
        for distance in distances:
            if distance > result:
                result = distance
        return result

    @api.multi
    def get_distance_cost(self, origin, destination):
        if not origin or not destination:
            raise UserError(_(
                'Origin or destination not provided!'
            ))
        for record in self:
            client = googlemaps.Client(record.api_key)
            matrix = client.distance_matrix(origin, destination)
            distance = self.get_min_distance(matrix)
            for line in self.distance_line_ids.sorted('distance_limit'):
                if distance < line.distance_limit:
                    return line.delivery_method_id + self.default_delivery_method_id
            return self.default_delivery_method_id

    def button_teste(self):
        print(
            self.get_distance_cost(
                'itajuba',
                'shopping vale sul sjc'
            )
        )


class GooglemapsApiDistanceLines(models.Model):

    _name = 'googlemaps.api.distance.lines'

    googlemaps_api_id = fields.Many2one(
        comodel_name='googlemaps.api.config',
        string='Googlemaps API'
    )
    distance_limit = fields.Integer(
        string='Distance(m)',
    )
    # delivery_cost = fields.Monetary(
    #     string='Delivery Cost'
    # )
    delivery_method_id = fields.Many2one(
        comodel_name='delivery.carrier',
        string='Delivery Method'
    )
    currency_id = fields.Many2one(
        comodel_name='res.currency',
        string='Currency',
        readonly=True,
        default=lambda self: self.env.user.company_id.currency_id
    )

    @api.depends('googlemaps_api_id.name', 'distance_limit', 'delivery_method_id')
    def _compute_display_name(self):
        for record in self:
            record.display_name = record.googlemaps_api_id.name + ' - ' +\
                str(record.distance_limit) + '/' +\
                str(record.delivery_method_id.name)
