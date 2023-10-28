from datetime import datetime

from odoo import fields, models, api, _
from odoo.exceptions import UserError


class AssetMovement(models.Model):
    _name = 'asset.movement'
    _description = 'Asset Movement'

    name = fields.Char('Asset')
    asset_registration_id = fields.Many2one('fastra.asset.registration', 'Code')
    hire_cost = fields.Float('Hire Cost/Day')
    project_id = fields.Many2one('account.analytic.account', 'Project')
    collection_date = fields.Date('Collection Date')
    return_date = fields.Date('Return Date')
    no_of_days = fields.Float('No of Days', compute='get_no_of_days')
    amount_charged = fields.Float('Amount Charged', compute='get_amount_charged')
    request_by = fields.Char('Request By')
    state = fields.Selection([('draft', 'Draft'),
                              ('open', 'Open'),
                              ('completed', 'Completed')], string="State", default='draft')
    cost_to_date = fields.Float('Cost to Date', compute='get_cost_to_date')

    @api.multi
    @api.depends('collection_date', 'hire_cost', 'return_date')
    def get_cost_to_date(self):
        for rec in self:
            rec.cost_to_date = 0.0
            if rec.collection_date:
                return_date = datetime.today().date()
                if rec.return_date:
                    return_date = rec.return_date
                delta = return_date - rec.collection_date
                rec.cost_to_date = int(delta.days) * rec.hire_cost

    @api.multi
    @api.onchange('asset_registration_id')
    def onchange_code_asset(self):
        if self.asset_registration_id:
            self.name = self.asset_registration_id.name
            self.hire_cost = self.asset_registration_id.hire_cost

    @api.multi
    @api.depends('collection_date', 'return_date')
    def get_no_of_days(self):
        for rec in self:
            rec.no_of_days = 0.0
            if rec.return_date and rec.collection_date:
                delta = rec.return_date - rec.collection_date
                rec.no_of_days = delta.days

    @api.multi
    @api.depends('no_of_days', 'hire_cost')
    def get_amount_charged(self):
        for rec in self:
            rec.amount_charged = rec.no_of_days * rec.hire_cost

    def set_to_open(self):
        self.write({'state': 'open'})

    def set_completed(self):
        self.write({'state': 'completed'})

    @api.model
    def create(self, vals):
        if vals.get('asset_registration_id', False):
            asset_movement_ids = self.search([('asset_registration_id', '=', vals['asset_registration_id']),
                                              ('state', '=', 'open')])
            if asset_movement_ids:
                raise UserError(_('Current Asset is already connected with other Project'))
        return super(AssetMovement, self).create(vals)
