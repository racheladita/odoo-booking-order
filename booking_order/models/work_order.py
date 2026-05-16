from odoo import api, fields, models, _
from odoo.exceptions import ValidationError, UserError


class WorkOrder(models.Model):
    _name = "work.order"
    _description = "Work Order"

    wo_number = fields.Char(string='Work Order Number', required=True, copy=False, readonly=True, index=True, default=lambda self: _('New'))
    booking_order_id = fields.Many2one(comodel_name='sale.order', string="Booking Order Reference", readonly=True)
    origin = fields.Char('Booking Order Reference', index=True, related='booking_order_id.name',
        states={'in_progress': [('readonly', True)], 'done': [('readonly', True)], 'cancel': [('readonly', True)]},
        help="Reference of the document")
    team_id = fields.Many2one(comodel_name='service.team', string="Team", required=True)
    team_leader_id = fields.Many2one('res.users', string='Team Leader', index=True, related='team_id.team_leader_id', required=True)
    team_member_ids = fields.Many2many('res.users', string='Team Members', index=True, related='team_id.team_member_ids')
    planned_start = fields.Datetime(string='Planned Start', copy=False, required=True)
    planned_end = fields.Datetime(string='Planned End', copy=False, required=True)
    date_start = fields.Datetime(string='Date Start', copy=False, readonly=True)
    date_end = fields.Datetime(string='Date End', copy=False, readonly=True)
    state = fields.Selection([
        ('pending', 'Pending'),
        ('in_progress', 'In Progress'),
        ('done', 'Done'),
        ('cancel', 'Cancelled'),
        ], string='Status', readonly=True, copy=False, index=True, track_visibility='onchange', default='pending')
    notes = fields.Text('Notes')
    company_id = fields.Many2one('res.company', string='Company', index=True, default=lambda self: self.env['res.company']._company_default_get('work.order'))
    
    @api.model
    def create(self, vals):
        if vals.get('wo_number', _('New')) == _('New'):
            if 'company_id' in vals:
                vals['wo_number'] = self.env['ir.sequence'].with_context(force_company=vals['company_id']).next_by_code('work.order') or _('New')
            else:
                vals['wo_number'] = self.env['ir.sequence'].next_by_code('work.order') or _('New')

        result = super(WorkOrder, self).create(vals)
        return result
    
    @api.multi
    def action_start_work(self):
        return self.write({
            'state': 'in_progress',
            'date_start': fields.Datetime.now(),
        })
    
    @api.multi
    def action_end_work(self):
        return self.write({
            'state': 'done',
            'date_end': fields.Datetime.now(),
        })
    
    @api.multi
    def action_reset(self):
        orders = self.filtered(lambda s: s.state in ['in_progress'])
        return orders.write({
            'state': 'pending',
            'date_start': False,
        })

    @api.multi
    def action_cancel_wo(self):
        return self.write({'state': 'cancel'})
    
    @api.multi
    def action_cancel(self):
        view = self.env.ref('booking_order.view_work_order_cancel_confirmation')
        wiz = self.env['work.order.cancel.confirmation'].create({'work_order_id': self.id})
        return {
            'name': _('Reason for Cancellation'),
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'work.order.cancel.confirmation',
            'views': [(view.id, 'form')],
            'view_id': view.id,
            'target': 'new',
            'res_id': wiz.id,
            'context': self.env.context,
        }