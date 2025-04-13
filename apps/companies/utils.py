from django.conf import settings
from django.db.models import Q
from django.core.mail import EmailMultiAlternatives
from django.utils import timezone
from django.template.loader import render_to_string
from ..external_tables.models import Agent
from auditlog.models import LogEntry
import traceback


# Send deactivation emails when company is deactivated
def send_deactivation_emails(company, request_user):
    """
    Send notifications to affected users.
    """
    try:
        affected_agents = Agent.objects.filter(Q(company=company))
        subject = "Agent Account Status Update"
        # message = f"Your account with {company.name} has be deactivated"
        recipients = list(
            Agent.objects.filter(company=company).values_list("user__email", flat=True)
        )

        if not recipients:
            return False

        context = {"company": company, "support_email": settings.SUPPORT_EMAIL}

        email = EmailMultiAlternatives(
            subject=subject,
            body=render_to_string("companies/deactivation_email.txt", context),
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=recipients,
            reply_to=[settings.SUPPORT_EMAIL],
        )
        email.attach_alternative(
            render_to_string(
                "companies/deactivation_email.html",
                context,
            ),
            "text/html",
        )
        email.send(fail_silently=False)

        return True

    except Exception as e:
        LogEntry.objects.create(
            instance=company,
            actor=request_user,
            action="EMAIL_FAILURE",
            changes={
                "error": str(e),
                "failed_recipients": recipients,
                "attempted_at": timezone.now().isoformat(),
                "traceback": traceback.format_exc()[-1000],
            },
        )
        return False
