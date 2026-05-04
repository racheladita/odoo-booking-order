from odoo import api, fields, tools, models, _
from odoo.exceptions import UserError, ValidationError


class SaleOrder(models.Model):
    _inherit = "sale.order"

    is_booking_order = fields.Boolean(string="Is Booking Order?", default=False)
    service_team_id = fields.Many2one(comodel_name='service.team', string="Team")
    team_leader_id = fields.Many2one('res.users', string='Team Leader', index=True, related='service_team_id.team_leader_id')
    team_member_ids = fields.Many2many('res.users', string='Team Members', index=True, related='service_team_id.team_member_ids')
    booking_start = fields.Datetime(string='Booking Start', copy=False)
    booking_end = fields.Datetime(string='Booking End', copy=False)
    work_order_ids = fields.Many2many('work.order', compute='_get_work_order', string='Work Order associated to this sale')
    work_order_count = fields.Integer(string='# of Work Orders', compute='_get_work_order', readonly=True)

    @api.model
    def create(self, values):
        booking = super(SaleOrder, self).create(values)
        if booking.service_team_id:
            booking.is_booking_order = True

        return booking
    
    def check_overlap(self, order):
        overlapping_wo = self.env['work.order'].search([
            ('team_id', '=', order.service_team_id.id),
            ('team_leader_id', '=', order.team_leader_id.id),
            ('planned_start', '<=', order.booking_end),
            ('planned_end', '>=', order.booking_start),
        ]).filtered(lambda r: r.state != 'cancel')
        
        return overlapping_wo

    @api.multi
    def action_check(self):
        for order in self:
            overlapping_wo = order.check_overlap(order)
            
            if overlapping_wo:
                raise UserError(_('Team already has work order during that period on %s') % (overlapping_wo.origin))
            else:
                raise UserError(_('Team is available for booking'))

    @api.multi
    def action_confirm(self):
        for order in self:
            overlapping_wo = order.check_overlap(order)

            if overlapping_wo:
                raise UserError(_('Team is not available during this period, already booked on %s. Please book on another date.') % (overlapping_wo.origin))
            else:
                sales = super(SaleOrder, self).action_confirm()
                self.env['work.order'].create({
                    'booking_order_id': order.id,
                    'origin': order.name,
                    'team_id': order.service_team_id.id,
                    'team_leader_id': order.team_leader_id.id,
                    'team_member_ids': order.team_member_ids.ids,
                    'planned_start': order.booking_start,
                    'planned_end': order.booking_end,
                    # 'date_start': order.booking_start,
                    # 'date_end': order.booking_end,
                    'state': 'pending',
                    'company_id': order.company_id.id,
                })
        return True
    
    @api.multi
    def action_view_work_order(self):
        wos = self.env['work.order'].search([('booking_order_id', '=', self.id)])
        action = self.env.ref('booking_order_adita_putri_puspaningrum_16012024.work_order_tree_action').read()[0]
        if len(wos) > 1:
            action['domain'] = [('id', 'in', wos.ids)]
        elif len(wos) == 1:
            action['views'] = [(self.env.ref('booking_order_adita_putri_puspaningrum_16012024.view_work_order_form').id, 'form')]
            action['res_id'] = wos.ids[0]
        else:
            action = {'type': 'ir.actions.act_window_close'}
        return action
    
    @api.multi
    def _get_work_order(self):
        for order in self:
            order.work_order_ids = self.env['work.order'].search([('booking_order_id', '=', order.id)])
            order.work_order_count = len(order.work_order_ids)