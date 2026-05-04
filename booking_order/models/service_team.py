from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class ServiceTeam(models.Model):
    _name = "service.team"
    _description = "Service Team"
    _order = "name"

    name = fields.Char('Team Name', required=True)
    team_leader_id = fields.Many2one('res.users', string='Team Leader', index=True, required=True)
    team_member_ids = fields.Many2many('res.users', string='Team Members', index=True)
    company_id = fields.Many2one('res.company', string='Company', index=True, default=lambda self: self.env['res.company']._company_default_get('service.team'))