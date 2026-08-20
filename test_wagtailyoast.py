"""Smoke tests for the wagtailyoast package.

These cover the import chain Wagtail exercises at startup
(``wagtail_hooks`` -> ``context``) and the two editor hooks. VERSION is
interpolated into the static asset filenames, so a wrong value does not
just mislabel the package - it 404s the editor's JS and CSS.

Run with:

    python -m django test --settings=test_settings
"""
import importlib
import json
import os
from importlib.metadata import version as installed_version
from unittest import mock

from django.conf import settings
from django.contrib.auth.models import AnonymousUser
from django.db import models
from django.test import RequestFactory, SimpleTestCase, TestCase

from wagtail.models import Page

from wagtailyoast import context, wagtail_hooks
from wagtailyoast.edit_handlers import YoastPanel


class ProbeModel(models.Model):
    """Minimal model exposing the `keywords` field YoastPanel expects.

    Test-only; never migrated or saved. A plain model (not a Page
    subclass) keeps the migration-less test app out of Django's
    migration state, and the panel machinery is model-agnostic.
    """

    keywords = models.CharField(max_length=255, blank=True, default="")

    class Meta:
        app_label = "wagtailyoast"


class ContextTests(SimpleTestCase):

    def test_version_matches_installed_distribution(self):
        self.assertEqual(context.VERSION, installed_version("wagtailyoast"))

    def test_static_url_comes_from_settings(self):
        self.assertEqual(context.STATIC_URL, settings.STATIC_URL)

    def test_package_json_fallback_when_distribution_is_missing(self):
        """The develop-mode path: no installed distribution -> package.json."""
        from importlib.metadata import PackageNotFoundError

        with mock.patch(
            "importlib.metadata.version",
            side_effect=PackageNotFoundError("wagtailyoast"),
        ):
            reloaded = importlib.reload(context)
            with open(os.path.join(settings.BASE_DIR, "package.json")) as f:
                expected = json.load(f)["version"]
            self.assertEqual(reloaded.VERSION, expected)

        # Restore the real module state for the other tests.
        importlib.reload(context)


class EditorHookTests(SimpleTestCase):

    def test_css_hook_includes_versioned_stylesheet(self):
        html = wagtail_hooks.yoast_panel_css()
        self.assertIn("styles%s.css" % context.VERSION, html)

    def test_hooks_are_registered_on_hooks_wagtail_still_renders(self):
        """`insert_editor_css` is no longer rendered by any Wagtail
        template, so registering the stylesheet there loaded nothing."""
        from wagtail import hooks

        css_hooks = hooks.get_hooks("insert_global_admin_css")
        self.assertIn(wagtail_hooks.yoast_panel_css, css_hooks)


class YoastPanelTests(SimpleTestCase):

    def test_panel_instantiates_with_defaults(self):
        panel = YoastPanel()
        self.assertEqual(panel.heading, "Yoast")

    def test_clone_kwargs_round_trips_custom_fields(self):
        panel = YoastPanel(
            keywords="kw"
        )
        kwargs = panel.clone_kwargs()
        self.assertEqual(kwargs["keywords"], "kw")


class YoastPanelRenderTests(SimpleTestCase):
    """
    Test that YoastPanel renders the expected HTML and uses the correct template.
    """

    def _bound_panel(self):
        panel_def = YoastPanel().bind_to_model(ProbeModel)
        form_class = panel_def.get_form_class()
        instance = ProbeModel()
        instance.locale = mock.Mock(language_code="en")
        form = form_class(instance=instance)
        request = RequestFactory().get("/")
        request.user = AnonymousUser()
        return panel_def.get_bound_panel(
            instance=instance, request=request, form=form, prefix="panel"
        )

    def test_bound_panel_uses_the_yoast_template(self):
        bound = self._bound_panel()
        self.assertEqual(
            bound.template_name,
            "wagtailyoast/edit_handlers/yoast_panel.html",
        )

    def test_rendered_panel_contains_the_yoast_markup(self):
        html = str(self._bound_panel().render_html({}))
        self.assertIn('id="yoast_panel"', html)
        self.assertIn('id="yoast_title" data-field="seo_title"', html)
        self.assertIn(
            'id="yoast_search_description"'
            ' data-field="search_description"',
            html,
        )
        self.assertIn('id="yoast_slug" data-field="slug"', html)
        self.assertIn('id="yoast_results_seo"', html)
        self.assertIn('id="yoast_results_readability"', html)

    def test_rendered_panel_contains_the_keywords_form_field(self):
        html = str(self._bound_panel().render_html({}))
        self.assertIn('id="yoast_keywords"', html)

    def test_clone_preserves_a_custom_keywords_field(self):
        """clone_kwargs dropped `keywords`, so binding rebuilt the
        panel against the default field name and crashed on any model
        without a literal `keywords` field."""
        panel_def = YoastPanel(keywords="seo_title").bind_to_model(Page)
        form_class = panel_def.get_form_class()
        self.assertIn("seo_title", form_class.base_fields)


class AdminEditViewTests(TestCase):
    """End-to-end checks against a real Wagtail admin edit view.

    The unit tests above assert on the panel rendered in isolation and
    on hook registration. Both are proxies: they encode today's
    answers (which template attribute, which hook name) rather than
    the requirement. These tests assert the requirement itself - that
    an editor opening a page actually gets the Yoast panel, its
    stylesheet and its scripts - so they keep holding whatever Wagtail
    renames next.

    Two bugs that shipped for years would have been caught here:
    the panel not rendering at all on the post-4.0 panels API, and the
    stylesheet registered on a hook Wagtail no longer renders.
    """

    def setUp(self):
        from django.contrib.auth import get_user_model
        from wagtail.models import Page

        from test_app.models import YoastTestPage

        User = get_user_model()
        self.user = User.objects.create_superuser(
            "editor", "editor@example.com", "password",
        )
        home = Page.objects.filter(depth=2).first()
        self.page = YoastTestPage(
            title="SEO test page", slug="seo-test-page", keywords="wagtail",
        )
        home.add_child(instance=self.page)
        self.client.force_login(self.user)

    def _edit_html(self):
        response = self.client.get(
            "/admin/pages/%d/edit/" % self.page.pk,
        )
        self.assertEqual(response.status_code, 200)
        return response.content.decode()

    def test_panel_markup_is_present_in_the_edit_view(self):
        html = self._edit_html()
        self.assertIn('id="yoast_panel"', html)
        self.assertIn('id="yoast_title"', html)
        self.assertIn('id="yoast_results_seo"', html)
        self.assertIn('id="yoast_results_readability"', html)
        self.assertIn('id="yoast_keywords"', html)

    def test_stylesheet_is_included_in_the_edit_view(self):
        """Regression: registered on `insert_editor_css`, which Wagtail
        no longer renders, so the panel loaded unstyled."""
        html = self._edit_html()
        self.assertIn("styles%s.css" % context.VERSION, html)
