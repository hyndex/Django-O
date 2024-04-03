# ocpp_app/message_handlers/handle_start_transaction.py
from asgiref.sync import sync_to_async
from ocpp_app.models import Connector, IdTag, ChargingSession, Charger
from users.models import PlanUser, Wallet, SessionBilling, Order, User
import json
import aioredis
from django.conf import settings
from django.utils import timezone
from django.db.models import Sum


# Initialize Redis connection
redis = aioredis.from_url(f"redis://{settings.REDIS_HOST}:{settings.REDIS_PORT}", encoding="utf-8", decode_responses=True)

async def get_price_per_kwh(user, charger):
    """
    Fetch the price per kWh either from the user's plan or the charger's default.
    """
    try:
        user_plan = await sync_to_async(PlanUser.objects.filter(
            user=user,
            expiry__gte=timezone.now(),
            active=True
        ).select_related('plan').latest, thread_sensitive=True)('expiry')
        return user_plan.plan.price_per_kwh
    except PlanUser.DoesNotExist:
        return charger.price_per_kwh


async def kwh_to_amount(kwh, user, charger):
    """
    Convert kWh to amount using the price per kWh for a given user and charger.
    """
    price_per_kwh = await get_price_per_kwh(user, charger)
    amount = kwh * price_per_kwh
    return amount

async def amount_to_kwh(amount, user, charger):
    """
    Convert amount to kWh based on the price per kWh for a given user and charger.
    """
    price_per_kwh = await get_price_per_kwh(user, charger)
    kwh = amount / price_per_kwh
    return kwh


async def calculate_default_limit(user, charger):
    # Fetch wallet balance
    wallet_balance_aggregate = await sync_to_async(Wallet.objects.filter(user=user).aggregate, thread_sensitive=True)(Sum('amount'))
    wallet_balance = wallet_balance_aggregate['amount__sum'] or 0

    # Attempt to use plan pricing if available
    price_per_kwh = None
    try:
        user_plan = await sync_to_async(PlanUser.objects.filter(
            user=user, expiry__gte=timezone.now(), active=True
        ).select_related('plan').latest, thread_sensitive=True)('expiry')
        price_per_kwh = user_plan.plan.price_per_kwh
    except PlanUser.DoesNotExist:
        pass

    # Fallback to a default price if no valid plan is found
    if price_per_kwh is None:
        price_per_kwh = charger.price_per_kwh

    # Calculate how much kWh can be afforded
    kwh_affordable = wallet_balance / price_per_kwh

    return kwh_affordable, "KWH"

async def handle_start_transaction(payload):
    connector_id = payload.get("connectorId")
    id_tag = payload.get("idTag")
    meter_start = payload.get("meterStart")
    timestamp = payload.get("timestamp")

    connector = await sync_to_async(Connector.objects.get)(id=connector_id)
    id_tag_obj = await sync_to_async(IdTag.objects.get)(idtag=id_tag)

    charger = await sync_to_async(Charger.objects.get)(id=connector.charger_id)
    user = await sync_to_async(User.objects.get)(id=id_tag_obj.user_id)

    # Retrieve or calculate limit and limit type
    redis_key = f"charging:{charger.charger_id}:{connector_id}:{id_tag}"
    limit_info = await redis.get(redis_key)
    limit, limit_type = 0, 'KWH'
    if limit_info:
        limit_info = json.loads(limit_info)
        limit, limit_type = limit_info['limit'], limit_info['limit_type']
        await redis.delete(redis_key)
    else:
        limit, limit_type = await calculate_default_limit(user, charger)

    # Create the ChargingSession
    session = await sync_to_async(ChargingSession.objects.create)(
        connector=connector,
        id_tag=id_tag_obj,
        start_time=timestamp,
        meter_start=meter_start,
        limit=limit,
        limit_type=limit_type,
    )

    # Calculate amount and kWh based on limit and limit type
    if limit_type == 'KWH':
        amount_added = await kwh_to_amount(limit, user, charger)
        kwh_added = limit
    else:  # limit_type == 'AMOUNT'
        amount_added = limit
        kwh_added = await amount_to_kwh(limit, user, charger)

    # Create SessionBilling
    session_billing = await sync_to_async(SessionBilling.objects.create)(
        session=session,
        amount_added=amount_added,
        kwh_added=kwh_added,
    )

    # Create Order with appropriate amount
    order = await sync_to_async(Order.objects.create)(
        user=user,
        session_billing=session_billing,
        amount=amount_added,  # This presumes that order amount directly relates to billing amount
        status='Pending',
    )

    return {
        "transactionId": session.formatted_transaction_id,
        "idTagInfo": {"status": "Accepted"}
    }
