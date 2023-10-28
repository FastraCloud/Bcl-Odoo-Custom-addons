from odoo import models, api, _
from odoo.exceptions import UserError


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    @api.model
    def create(self, vals):
        if vals.get('journal_id', False) and vals.get('date_invoice', False):
            lock_date_id = self.env['lock.date'].search([('to_date', '>', vals['date_invoice']),
                                                         ('from_date', '<', vals['date_invoice']),
                                                         ('journal_ids', '=', vals['journal_id']),
                                                         ('state', '=', 'locked')], limit=1)
            if lock_date_id:
                raise UserError(_("Accounting Journal can't be posted from %s to %s" % (lock_date_id.from_date, lock_date_id.to_date)))
        return super(AccountInvoice, self).create(vals)

    @api.multi
    def write(self, vals):
        if vals.get('journal_id', False) or vals.get('date_invoice', False):
            lock_date_id = self.env['lock.date'].search([('to_date', '>', vals.get('date_invoice', self.date_invoice)),
                                                         ('from_date', '<', vals.get('date_invoice', self.date_invoice)),
                                                         ('journal_ids', '=', vals.get('journal_id', self.journal_id.id)),
                                                         ('state', '=', 'locked')], limit=1)
            if lock_date_id:
                raise UserError(_("Accounting Journal can't be posted from %s to %s" % (lock_date_id.from_date, lock_date_id.to_date)))
        return super(AccountInvoice, self).write(vals)