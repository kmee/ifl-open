{
    # Theme information

    'name': 'Theme Clarico',
    'category': 'Theme/eCommerce',
    'summary': 'Fully Responsive Odoo Theme suitable for eCommerce Businesses',
    'version': '12.0.0.59',
    'license': 'OPL-1',
    'depends': [
        'emipro_theme_base',
        'website_sale_delivery',
        'website_sale_secondary_unit',
        'website_sale_product_minimal_price',
        'website_sale_require_login',
        'l10n_br_portal',
        'l10n_br_website_sale',
        ],
    'data': [
        'security/ir.model.access.csv',
        
        'templates/assets.xml',
        'templates/emipro_custom_snippets.xml',
        'templates/odoo_default_snippets.xml',
        'templates/blog.xml',
        'templates/shop.xml',
        'templates/portal.xml',
        'templates/product.xml',
        'templates/product_ept_inherit.xml',
        'templates/cart.xml',
        'templates/login.xml',
        'templates/theme_customise_option.xml',
        'templates/404.xml',
        'templates/category.xml',
        'templates/compare.xml',
        'templates/header.xml',
        'templates/footer.xml',
        'templates/customize.xml',
        'templates/menu_config.xml',
        'templates/slider.xml',
        'templates/wishlist.xml',
        'templates/product_label.xml',
        'templates/contactus.xml',
        'templates/recently_viewed.xml',
        'templates/website_price_filter.xml',
        'templates/quickview.xml',
        'templates/cart_line.xml',
        'views/res_config_settings.xml',
        'views/product_footer.xml',
        'views/minimal_price.xml',
        # 'views/product_attribute_views.xml',
        'data/slider_styles_data.xml',
        'views/website_sale_portal.xml',
        'templates/cart_total.xml',
        'templates/cart_fix_qty_table.xml',
        'templates/auth_signup_login_templates.xml',
        'views/address_management_inherit.xml',
        'views/sale_order_product_replace.xml',
        'security/product_replace_strategy.xml',
        'data/sale_order_product_replace_data.xml',

        'templates/payment_replace_strategy_template.xml',
        'templates/delivery_methods.xml',
        ],

    # Odoo Store Specific
    'live_test_url': 'http://clarico12ee.theme12demo.emiprotechnologies.com',
    'images': [
        'static/description/main_poster.jpg',
        'static/description/main_screenshot.gif',
        ],

    # Author
    'author': 'Emipro Technologies Pvt. Ltd.',
    'website': 'https://www.emiprotechnologies.com',
    'maintainer': 'Emipro Technologies Pvt. Ltd.',

    # Technical
    'installable': True,
    'auto_install': False,
    'price': 240.00,
    'currency': 'EUR',
    }
