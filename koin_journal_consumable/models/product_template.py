# -*- coding: utf-8 -*-

from odoo import models, fields, api


class ProductTemplate(models.Model):
    _inherit = "product.template"

    journal_on_move = fields.Boolean("Generate Journal on Product Move")
