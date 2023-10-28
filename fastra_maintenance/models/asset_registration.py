from odoo import fields, models, api, _


class AssetRegistration(models.Model):
    _name = 'fastra.asset.registration'
    _description = 'Fastra Asset Registration'
    _rec_name = "code"

    code = fields.Char('Code')
    name = fields.Char('Asset')
    asset_code = fields.Char('Asset Code')
    purchase_date = fields.Date('Purchase Date')
    purchase_code = fields.Float('Purchase Cost')
    useful_life = fields.Float('Useful Life')
    hire_cost = fields.Float('Hire Cost/Day')
