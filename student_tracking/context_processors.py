from django.contrib.sites.models import Site
from django.conf import settings as django_settings


def settings(request):
    ctx = {
        "ADMIN_URL": django_settings.ADMIN_URL,
        "CONTACT_EMAIL": django_settings.CONTACT_EMAIL,

        "pinax_notifications_installed": "pinax.notifications" in django_settings.INSTALLED_APPS,
        "pinax_stripe_installed": "pinax.stripe" in django_settings.INSTALLED_APPS,

        "COURSE_URL": django_settings.COURSE_URL,
        "LESSON1_URL": django_settings.LESSON1_URL,
        "GITHUB_REPO": django_settings.GITHUB_REPO,
        "SLACK_INVITE": django_settings.SLACK_INVITE,
    }

    if Site._meta.installed:
        site = Site.objects.get_current(request)
        ctx.update({
            "SITE_NAME": site.name,
            "SITE_DOMAIN": site.domain
        })

    return ctx
