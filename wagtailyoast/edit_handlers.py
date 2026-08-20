from django import forms
from wagtail.admin.panels import ObjectList, FieldPanel

from . import context as ctx


class YoastPanel(ObjectList):
    TITLE_FIELD = 'seo_title'
    SEARCH_DESCRIPTION_FIELD = 'search_description'
    SLUG_FIELD = 'slug'

    def __init__(self, keywords='keywords', heading='Yoast', **kwargs):
        """
        Panel used by a wagtail Page

        :param keywords: Name of the page's keywords field.
        :param heading: Heading of panel
        """
        kwargs.pop('children', None)  # always rebuilt from `keywords` below
        self.keywords = keywords
        children = [
            FieldPanel(
                keywords,
                widget=forms.TextInput(attrs={'id': 'yoast_keywords'})
            ),
        ]
        super().__init__(children=children, heading=heading, **kwargs)

    def clone_kwargs(self):
        kwargs = super().clone_kwargs()
        kwargs.pop('children', None)
        kwargs['keywords'] = self.keywords
        return kwargs

    class BoundPanel(ObjectList.BoundPanel):
        template_name = "wagtailyoast/edit_handlers/yoast_panel.html"

        def get_context_data(self, parent_context=None):
            context = super().get_context_data(parent_context)
            instance = self.instance
            page_locale = instance.locale.language_code or 'en'
            context.update({
                'page_locale': page_locale,
                'version': ctx.VERSION,
                'static_url': ctx.STATIC_URL,
                'title_field': YoastPanel.TITLE_FIELD,
                'title_value': getattr(instance, YoastPanel.TITLE_FIELD, ""),
                'search_description_field': YoastPanel.SEARCH_DESCRIPTION_FIELD,
                'search_description_value': getattr(
                    instance, YoastPanel.SEARCH_DESCRIPTION_FIELD, ""
                ),
                'slug_field': YoastPanel.SLUG_FIELD,
                'slug_value': getattr(instance, YoastPanel.SLUG_FIELD, ""),
            })
            return context
