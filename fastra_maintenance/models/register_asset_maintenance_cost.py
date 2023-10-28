from odoo import fields, models, api


class RegisterAssetMaintenanceCost(models.Model):
    _name = 'register.asset.maintenance.cost'
    _description = 'Register Asset Maintenance Cost'

    asset_registration_id = fields.Many2one('fastra.asset.registration', 'Code')
    name = fields.Char('Asset')
    asset_code = fields.Char('Asset Code')
    maintenance_cost = fields.Float('Maintenance Cost', compute='get_maintenance_cost')
    replacement_of_parts = fields.Float('Replacement of Parts', compute='get_replacement_of_parts')
    operator = fields.Float('Operator', compute='get_operator')
    fuel = fields.Float('Fuel', compute='get_fuel')
    total_dep_cost = fields.Float('Total Dep Cost', compute='get_total_dep_cost')
    hire_cost_month = fields.Float('Hire Cost/Month', compute='get_hire_cost_month')
    hire_cost = fields.Float('Hire Cost/Day', compute='get_hire_cost')
    purchase_date = fields.Date('Purchase Date')
    purchase_code = fields.Float('Purchase Cost')
    useful_life = fields.Float('Useful Life')
    tax = fields.Float('Tax', compute='get_tax_amount')

    @api.multi
    @api.depends('total_dep_cost', 'useful_life')
    def get_hire_cost(self):
        for rec in self:
            rec.hire_cost = rec.hire_cost_month / 30

    @api.multi
    @api.depends('total_dep_cost', 'useful_life')
    def get_hire_cost_month(self):
        for rec in self:
            rec.hire_cost_month = 0
            if rec.useful_life > 0:
                rec.hire_cost_month = rec.total_dep_cost / rec.useful_life

    @api.multi
    @api.depends('purchase_code', 'maintenance_cost', 'tax', 'replacement_of_parts', 'operator', 'fuel')
    def get_total_dep_cost(self):
        for rec in self:
            rec.total_dep_cost = rec.purchase_code + rec.maintenance_cost + rec.tax + rec.replacement_of_parts + rec.operator + rec.fuel

    @api.multi
    @api.depends('purchase_code')
    def get_fuel(self):
        for rec in self:
            if rec.purchase_code:
                rec.fuel = (rec.purchase_code * 2) / 100

    @api.multi
    @api.depends('purchase_code')
    def get_operator(self):
        for rec in self:
            if rec.purchase_code:
                rec.operator = (rec.purchase_code * 34) / 100

    @api.multi
    @api.depends('purchase_code')
    def get_replacement_of_parts(self):
        for rec in self:
            if rec.purchase_code:
                rec.replacement_of_parts = (rec.purchase_code * 3) / 100

    @api.multi
    @api.depends('purchase_code')
    def get_tax_amount(self):
        for rec in self:
            if rec.purchase_code:
                rec.tax = (rec.purchase_code * 7.5) / 100

    @api.multi
    @api.depends('purchase_code')
    def get_maintenance_cost(self):
        for rec in self:
            if rec.purchase_code:
                rec.maintenance_cost = (rec.purchase_code * 10) / 100

    @api.multi
    @api.onchange('asset_registration_id')
    def onchange_code_asset(self):
        if self.asset_registration_id:
            self.name = self.asset_registration_id.name
            self.asset_code = self.asset_registration_id.asset_code
            self.hire_cost = self.asset_registration_id.hire_cost
            self.purchase_date = self.asset_registration_id.purchase_date
            self.purchase_code = self.asset_registration_id.purchase_code
            self.useful_life = self.asset_registration_id.useful_life
