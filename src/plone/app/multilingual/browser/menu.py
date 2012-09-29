from zope.interface import implements
from zope.component import getMultiAdapter
from zope.component import getUtility
from Products.CMFCore.utils import getToolByName
from Products.CMFCore.interfaces import ISiteRoot
from Products.CMFCore.permissions import ManagePortal
from zope.app.publisher.browser.menu import BrowserMenu
from zope.app.publisher.browser.menu import BrowserSubMenuItem
from plone.memoize.instance import memoize
from plone.app.multilingual.browser.interfaces import (
    ITranslateMenu,
    ITranslateSubMenuItem,
)
from plone.app.multilingual.browser.vocabularies import (
    untranslated_languages, translated_languages, translated_urls)
from plone.app.multilingual import _
from plone.uuid.interfaces import IUUID
from plone.multilingual.interfaces import LANGUAGE_INDEPENDENT, ILanguage


class TranslateMenu(BrowserMenu):
    implements(ITranslateMenu)

    def getMenuItems(self, context, request):
        """Return menu item entries in a TAL-friendly form."""
        menu = []
        url = context.absolute_url()
        lt = getToolByName(context, "portal_languages")
        portal_state = getMultiAdapter((context, request), name=u'plone_portal_state')
        portal_url = portal_state.portal_url()
        showflags = lt.showFlags()
        # In case is neutral language show set language menu only
        if LANGUAGE_INDEPENDENT != ILanguage(context).get_language():
            context_id = IUUID(context)
            langs = untranslated_languages(context)
            for lang in langs:
                lang_name = lang.title
                lang_id = lang.value
                icon = showflags and lt.getFlagForLanguageCode(lang_id) or None
                item = {
                    "title": _(u"Create") + " " + lang_name,
                    "description": _(u"description_translate_into",
                                    default=u"Translate into ${lang_name}",
                                    mapping={"lang_name": lang_name}),
                    "action": url + "/@@create_translation?form.widgets.language"\
                            "=%s&form.buttons.create=1" % lang_id,
                    "selected": False,
                    "icon": icon,
                    "extra": {"id": "translate_into_%s" % lang_id,
                           "separator": None,
                           "class": ""},
                    "submenu": None,
                    }

                menu.append(item)

            langs = translated_languages(context)
            urls = translated_urls(context)
            for lang in langs:
                lang_name = lang.title
                lang_id = lang.value
                icon = showflags and lt.getFlagForLanguageCode(lang_id) or None
                item = {
                    "title": _(u"Edit") + " " + lang_name,
                    "description": _(u"description_babeledit_menu",
                                    default=u"Babel edit ${lang_name}",
                                    mapping={"lang_name": lang_name}),
                    "action": urls.getTerm(lang_id).title + "/babel_edit",
                    "selected": False,
                    "icon": icon,
                    "extra": {"id": "babel_edit_%s" % lang_id,
                           "separator": None,
                           "class": ""},
                    "submenu": None,
                    }

                menu.append(item)

            menu.append({
                "title": _(u"title_add_translations",
                       default=u"Add translations..."),
                "description": _(u"description_add_translations",
                                default=u"Add existing content as translation"),
                "action": url + "/add_translations",
                "selected": False,
                "icon": None,
                "extra": {"id": "_add_translations",
                       "separator": langs and "actionSeparator" or None,
                       "class": ""},
                "submenu": None,
                })

            menu.append({
                "title": _(u"title_remove_translations",
                       default=u"Remove translations..."),
                "description": _(
                    u"description_remove_translations",
                    default=u"Delete translations or remove the relations"),
                "action": url + "/remove_translations",
                "selected": False,
                "icon": None,
                "extra": {"id": "_remove_translations",
                       "separator": langs and "actionSeparator" or None,
                       "class": ""},
                "submenu": None,
                })

            menu.append({
                "title": _(u"universal_link",
                       default=u"Universal Link"),
                "description": _(
                    u"description_universal_link",
                    default=u"Universal Language content link"),
                "action": portal_url + "/multilingual-universal-link?uid=" + context_id,
                "selected": False,
                "icon": None,
                "extra": {"id": "_universal_link",
                       "separator": langs and "actionSeparator" or None,
                       "class": ""},
                "submenu": None,
                })

        menu.append({
            "title": _(u"title_set_language",
                   default=u"Set language"),
            "description": _(u"description_add_translations",
                   default=u"Set/change context language"),
            "action": url + "/update_language",
            "selected": False,
            "icon": None,
            "extra": {"id": "_set_language",
               "separator": langs and "actionSeparator" or None,
                   "class": ""},
                 "submenu": None,
            })

        return menu


class TranslateSubMenuItem(BrowserSubMenuItem):
    implements(ITranslateSubMenuItem)

    title = _(u"label_translate_menu", default=u"Translate into...")
    description = _(u"title_translate_menu",
                    default="Manage translations for your content.")
    submenuId = "plone_contentmenu_multilingual"
    order = 5
    extra = {"id": "plone-contentmenu-multilingual"}

    @property
    def action(self):
        return self.context.absolute_url() + "/add_translations"

    @memoize
    def available(self):
        # this menu is only for ITranslatable,
        # IPloneAppMultilingualInstalled available
        return True

    def selected(self):
        return False
