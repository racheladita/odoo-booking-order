{
    'name': 'Booking Order',
    'version': '1.0',
    'category': 'Sales',
    'author': 'Adita Putri Puspaningrum',
    'depends': [
        'base',
        'sale',
        'sales_team',
    ],
    'description': """
        This is a custom module for managing Booking Order.
        ====================================================
    """,
    'data': [
        'security/ir.model.access.csv',
        'data/ir_sequence_data.xml',
        'report/work_order_report.xml',
        'report/work_order_report_template.xml',
        'wizard/work_order_cancel_confirmation_view.xml',
        'views/service_team_views.xml',
        'views/booking_order_views.xml',
        'views/work_order_views.xml',
        'views/booking_menuitem.xml',
    ],
    'installable': True,
    'application': True,
    'license': 'LGPL-3',
}
