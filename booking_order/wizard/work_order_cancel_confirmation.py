from odoo import api, fields, models, _


class WorkOrderCancelConfirmation(models.TransientModel):
    _name = 'work.order.cancel.confirmation'
    _description = 'Work Order Cancel Confirmation'

    work_order_id = fields.Many2one('work.order')
    reason = fields.Text('Reason')

    @api.model
    def default_get(self, fields):
        res = super(WorkOrderCancelConfirmation, self).default_get(fields)
        if 'work_order_id' in fields and self._context.get('active_id') and not res.get('work_order_id'):
            res = {'work_order_id': self._context['active_id']}
        return res

    @api.one
    def _process(self):
        wo = self.env['work.order'].search([('id', '=', self.work_order_id.id)])
        wo.action_cancel_wo()
        wo.write({
            'notes': self.reason,
        })

    @api.multi
    def process(self):
        self._process()
