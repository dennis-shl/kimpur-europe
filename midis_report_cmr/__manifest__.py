{
    'name': 'Print Picking CMR',
    'summary': 'CMR Report from Picking',
    'version': '17.0.1.5',
    'category': 'Warehouse Management',
    'website': "https://midis.eu",
    'author': 'Midis (www.midis.eu)',
    'license': 'AGPL-3',
    'depends': [
        'stock',
        'sale_stock',
        'web',
    ],
    'data': [
        'report/report_cmr.xml',
        'report/stock_report_views.xml',
        'data/report_paperformat.xml',
        'views/stock_picking_views.xml',
        'views/product_template_views.xml',
    ],
}