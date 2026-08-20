from django.utils.html import format_html_join
from django.templatetags.static import static
from wagtail import hooks

from . import context


@hooks.register('insert_global_admin_css')
def yoast_panel_css():
    """
    Add Yoast styles CSS files

    :return: HTML <link>
    """
    css_files = [
        'wagtailyoast/dist/css/styles%s.css' % context.VERSION,
    ]
    css_includes = format_html_join(
        '\n',
        '<link href="{0}" rel="stylesheet" type="text/css">',
        ((static(filename),) for filename in css_files)
    )
    return css_includes
