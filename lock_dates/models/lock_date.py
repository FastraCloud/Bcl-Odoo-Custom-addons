from odoo import models, fields, api, _
from odoo.exceptions import UserError


class LockDates(models.Model):
    _name = 'lock.date'
    _description = "Lock Dates"

    name = fields.Char("Name")
    company_id = fields.Many2one('res.company', string="Company", default=lambda self: self.env.user.company_id)
    journal_ids = fields.Many2many('account.journal', 'lock_date_journal_rel', 'lock_date_id', 'journal_id', string="Journal")
    from_date = fields.Date('From Date')
    to_date = fields.Date('To Date')
    state = fields.Selection([('draft', 'Draft'), ('locked', 'Locked')], string="State", default='draft')

    @api.multi
    def lock(self):
        self.write({'state': 'locked'})

    @api.multi
    def reset_to_draft(self):
        self.write({'state': 'draft'})


    @api.model
    def create(self, vals):
        if vals.get('from_date', False) and vals.get('to_date', False):
            lock_date_id = self.search([('to_date', '>', vals['from_date']),
                                        ('from_date', '<', vals['to_date']),
                                        ('state', '=', 'locked')])
            if lock_date_id:
                raise UserError(_("There is already period lock date is available. Can't create other with same period"))
            else:
                res = super(LockDates, self).create(vals)
        else:
            res = super(LockDates, self).create(vals)
        return res

    # @api.multi
    # @api.onchange('from_date', 'to_date')
    # def onchange_dates(self):
    #     if self.to_date and self.from_date and self.to_date < self.from_date:
    #         raise UserError(_("You can't set To date less than From date"))