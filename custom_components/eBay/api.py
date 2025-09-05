"""API for ebay bound to Home Assistant OAuth."""
from typing import Any, cast
from aiohttp import ClientSession
import base64
from yarl import URL

from homeassistant.core import HomeAssistant
from homeassistant.helpers import config_entry_oauth2_flow
from homeassistant.helpers.aiohttp_client import async_get_clientsession
import homeassistant.util.dt as dt
from .const import (
    SCOPES,
    UNFULFILLED_ORDERS_URL,
    FULFILLED_ORDERS_URL,
    CANCELLED_ORDERS_URL,
    RETURN_REQUESTS_URL,
    CANCELLATION_REQUESTS_URL,
    ACTIVE_LISTINGS_URL,
    TRAFFIC_REPORT_URL,
)


async def get_ebay_data(access_token):

    today = 0
    total = 0
    awaiting_payment = 0
    fulfilled_total = 0
    cancelled_total = 0
    return_requests = 0
    cancellation_requests = 0
    active_listings = 0
    listing_impressions = 0
    listing_page_views = 0
    click_through_rate = 0

    async with ClientSession() as session:

        order_response = await session.get(
            UNFULFILLED_ORDERS_URL,
            headers={"Authorization": "Bearer " + access_token},
        )
        if order_response.status == 200:
            data = await order_response.json()
            for order in data["orders"]:
                if order.get("orderPaymentStatus") != "PAID":
                    awaiting_payment += 1
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

        fulfilled_response = await session.get(
            FULFILLED_ORDERS_URL,
            headers={"Authorization": "Bearer " + access_token},
        )
        if fulfilled_response.status == 200:
            data = await fulfilled_response.json()
            fulfilled_total = data.get("total", 0)

        cancelled_response = await session.get(
            CANCELLED_ORDERS_URL,
            headers={"Authorization": "Bearer " + access_token},
        )
        if cancelled_response.status == 200:
            data = await cancelled_response.json()
            cancelled_total = data.get("total", 0)

        return_response = await session.get(
            RETURN_REQUESTS_URL,
            headers={"Authorization": "Bearer " + access_token},
        )
        if return_response.status == 200:
            data = await return_response.json()
            return_requests = data.get("total", 0)

        cancellation_req_response = await session.get(
            CANCELLATION_REQUESTS_URL,
            headers={"Authorization": "Bearer " + access_token},
        )
        if cancellation_req_response.status == 200:
            data = await cancellation_req_response.json()
            cancellation_requests = data.get("total", 0)

        listings_response = await session.get(
            ACTIVE_LISTINGS_URL,
            headers={"Authorization": "Bearer " + access_token},
        )
        if listings_response.status == 200:
            data = await listings_response.json()
            active_listings = data.get("total", 0)

        traffic_response = await session.get(
            TRAFFIC_REPORT_URL,
            headers={"Authorization": "Bearer " + access_token},
        )
        if traffic_response.status == 200:
            data = await traffic_response.json()
            for record in data.get("records", []):
                metrics = {
                    m.get("metricName"): float(m.get("value", 0))
                    for m in record.get("metricValues", [])
                }
                listing_impressions += int(metrics.get("LISTING_IMPRESSION", 0))
                listing_page_views += int(
                    metrics.get("LISTING_PAGE_VIEWS", metrics.get("LISTING_VIEWS", 0))
                )
            if listing_impressions:
                click_through_rate = round(
                    (listing_page_views / listing_impressions) * 100, 2
                )
        await session.close()
    return {
        "ebay_orders_due_today": today,
        "ebay_total_unfulfilled_orders": total,
        "ebay_orders_awaiting_payment": awaiting_payment,
        "ebay_fulfilled_orders": fulfilled_total,
        "ebay_cancelled_orders": cancelled_total,
        "ebay_return_requests": return_requests,
        "ebay_cancellation_requests": cancellation_requests,
        "ebay_active_listings": active_listings,
        "ebay_listing_impressions": listing_impressions,
        "ebay_listing_page_views": listing_page_views,
        "ebay_click_through_rate": click_through_rate,
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
