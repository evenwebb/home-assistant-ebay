"""API for ebay bound to Home Assistant OAuth."""
from typing import Any, cast
from aiohttp import ClientSession
import base64
from datetime import timedelta
from yarl import URL

from homeassistant.core import HomeAssistant
from homeassistant.helpers import config_entry_oauth2_flow
from homeassistant.helpers.aiohttp_client import async_get_clientsession
import homeassistant.util.dt as dt
from .const import (
    SCOPES,
    UNFULFILLED_ORDERS_URL,
    SELLER_FUNDS_SUMMARY_URL,
    TRANSACTION_SUMMARY_URL,
)


async def get_ebay_data(access_token):

    today = 0
    total = 0
    available_funds = 0
    funds_on_hold = 0
    processing_funds = 0
    total_funds = 0
    sales_today = 0
    sales_week = 0
    sales_month = 0
    refunds_today = 0
    refunds_week = 0
    refunds_month = 0

    async with ClientSession() as session:

        order_response = await session.get(
            UNFULFILLED_ORDERS_URL,
            headers={"Authorization": "Bearer " + access_token},
        )
        if order_response.status == 200:
            data = await order_response.json()
            for order in data["orders"]:
                for lineItem in order["lineItems"]:
                    ship_by_date = dt.parse_datetime(
                        lineItem["lineItemFulfillmentInstructions"]["shipByDate"]
                    )
                    # ship_by_date = ship_by_date.day - 1
                    # This may be needed/easier depending on how ebay saves shipByDate based on timezone.
                    # e.i. If it's saved 11:59pm central always it would show 1:59am next morning for someone in pacific.
                    # ["lineItemFulfillmentInstructions"]["sourceTimeZone"] might start being returned and we can use that. however currently it's not.
                    ship_by_date = dt.as_local(ship_by_date).day
                    date_now = dt.now().day
                    if ship_by_date == date_now:
                        today = today + 1
                        break
            total = data["total"]
        funds_reponse = await session.get(
            SELLER_FUNDS_SUMMARY_URL,
            headers={"Authorization": "Bearer " + access_token},
        )
        if funds_reponse.status == 200:
            data = await funds_reponse.json()
            if "availableFunds" in data:
                available_funds = data["availableFunds"]["value"]
            if "fundsOnHold" in data:
                funds_on_hold = data["fundsOnHold"]["value"]
            if "processingFunds" in data:
                processing_funds = data["processingFunds"]["value"]
            if "totalFunds" in data:
                total_funds = data["totalFunds"]["value"]

        async def _fetch_summary(start, end):
            url = (
                f"{TRANSACTION_SUMMARY_URL}?filter="
                f"transactionDate:[{start}..{end}]"
            )
            resp = await session.get(
                url, headers={"Authorization": "Bearer " + access_token}
            )
            sale_total = 0
            refund_total = 0
            if resp.status == 200:
                summary = await resp.json()
                for item in summary.get("transactionSummaries", []):
                    amount = float(item.get("totalAmount", {}).get("value", 0))
                    t_type = item.get("transactionType")
                    if t_type == "SALE":
                        sale_total = amount
                    elif t_type == "REFUND":
                        refund_total = abs(amount)
            return sale_total, refund_total

        now = dt.utcnow()
        today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        week_start = today_start - timedelta(days=now.weekday())
        month_start = today_start.replace(day=1)

        def _fmt(dtime):
            return dtime.isoformat().replace("+00:00", "Z")

        sales_today, refunds_today = await _fetch_summary(
            _fmt(today_start), _fmt(now)
        )
        sales_week, refunds_week = await _fetch_summary(
            _fmt(week_start), _fmt(now)
        )
        sales_month, refunds_month = await _fetch_summary(
            _fmt(month_start), _fmt(now)
        )

        await session.close()
    return {
        "ebay_orders_due_today": today,
        "ebay_total_unfulfilled_orders": total,
        "ebay_available_funds": available_funds,
        "ebay_funds_on_hold": funds_on_hold,
        "ebay_processing_funds": processing_funds,
        "ebay_total_funds": total_funds,
        "ebay_sales_today": sales_today,
        "ebay_sales_this_week": sales_week,
        "ebay_sales_this_month": sales_month,
        "ebay_refunds_today": refunds_today,
        "ebay_refunds_this_week": refunds_week,
        "ebay_refunds_this_month": refunds_month,
    }


class ConfigEntryAuth:
    """Provide ebay authentication tied to an OAuth2 based config entry."""

    def __init__(
        self,
        hass: HomeAssistant,
        oauth_session: config_entry_oauth2_flow.OAuth2Session,
    ) -> None:
        """Initialize ebay Auth."""
        self.hass = hass
        self.session = oauth_session


class EbayImplementation(config_entry_oauth2_flow.LocalOAuth2Implementation):
    """Ebay implementation of LocalOAuth2Implementation.

    We need this because we have to add headers and modify the redirect URI
    """

    def __init__(
        self,
        hass: HomeAssistant,
        domain: str,
        client_id: str,
        client_secret: str,
        authorize_url: str,
        token_url: str,
        redirect_uri: str,
    ) -> None:
        """Initialize local auth implementation."""
        self.hass = hass
        self._domain = domain
        self.client_id = client_id
        self.client_secret = client_secret
        self.authorize_url = authorize_url
        self.token_url = token_url
        self._redirect_uri = redirect_uri
        auth = self.client_id + ":" + self.client_secret
        self._authEncoded = base64.b64encode(str.encode(auth)).decode()

    async def async_generate_authorize_url(self, flow_id: str) -> str:
        """Overidge default generate authorize url"""
        """Needed to change the redirect URI"""
        """Generate a url for the user to authorize."""
        redirect_uri = self._redirect_uri
        qry = str(
            URL(self.authorize_url)
            .with_query(
                {
                    "response_type": "code",
                    "client_id": self.client_id,
                    "redirect_uri": redirect_uri,
                    "state": config_entry_oauth2_flow._encode_jwt(
                        self.hass, {"flow_id": flow_id, "redirect_uri": redirect_uri}
                    ),
                }
            )
            .update_query(self.extra_authorize_data)
        )
        # Need to add scopes query, however YARL will not encode spaces correctly.
        scope_param = "%20".join(SCOPES)
        qry = f"{qry}&scope={scope_param}"
        return qry

    async def _token_request(self, data: dict) -> dict:
        """Override a token request."""
        """Needed to change the headers of the request"""
        session = async_get_clientsession(self.hass)

        headers = {
            "Content-Type": "application/x-www-form-urlencoded",
            "Authorization": "Basic " + self._authEncoded,
        }

        resp = await session.post(self.token_url, data=data, headers=headers)
        resp.raise_for_status()
        resp_json = cast(dict, await resp.json())
        return resp_json

    async def async_resolve_external_data(self, external_data: Any) -> dict:
        """Overide"""
        """Needed to update the redirect URI"""
        """Resolve the authorization code to tokens."""
        return await self._token_request(
            {
                "grant_type": "authorization_code",
                "code": external_data["code"],
                "redirect_uri": self._redirect_uri,
            }
        )

    async def _async_refresh_token(self, token: dict) -> dict:
        """Refresh tokens."""
        data = {
            "grant_type": "refresh_token",
            "client_id": self.client_id,
            "refresh_token": token["refresh_token"],
        }

        data["scope"] = " ".join(SCOPES)

        new_token = await self._token_request(data)
        return {**token, **new_token}
