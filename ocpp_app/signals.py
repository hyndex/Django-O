from django.db.models.signals import post_save
from django.dispatch import receiver
from partners.models import PartnerCommissionMember, CommissionPayment
from users.models import SessionBilling

@receiver(post_save, sender=SessionBilling)
def create_commission_payment(sender, instance, created, **kwargs):
    if created:
        # Calculate the commission amount based on the amount consumed
        commission_amount = instance.amount_consumed * instance.session.connector.charger.charger_commission_group.commission / 100

        # Create a CommissionPayment entry for each commission member
        commission_members = PartnerCommissionMember.objects.filter(partner_commission_member_group=instance.session.connector.charger.charger_commission_group)
        for member in commission_members:
            CommissionPayment.objects.create(
                amount=commission_amount * member.commission / 100,
                session_billing=instance,
                charger_commission_member=member
            )
