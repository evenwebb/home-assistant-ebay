"""Constants for the ebay integration."""
from homeassistant.components.sensor import SensorEntityDescription

DOMAIN = "ebay"
OAUTH2_AUTHORIZE = "https://auth.ebay.com/oauth2/authorize"
OAUTH2_TOKEN = "https://api.ebay.com/identity/v1/oauth2/token"
# Request fulfillment and finances scopes so financial endpoints work
SCOPES = (
    "https://api.ebay.com/oauth/api_scope/sell.fulfillment.readonly",
    "https://api.ebay.com/oauth/api_scope/sell.finances",
    "https://api.ebay.com/oauth/api_scope/sell.analytics.readonly",
    "https://api.ebay.com/oauth/api_scope/sell.inventory.readonly",
    "https://api.ebay.com/oauth/api_scope/sell.postorder.readonly",
)
UNFULFILLED_ORDERS_URL = "https://api.ebay.com/sell/fulfillment/v1/order?filter=orderfulfillmentstatus:%7BNOT_STARTED%7CIN_PROGRESS%7D"
FULFILLED_ORDERS_URL = "https://api.ebay.com/sell/fulfillment/v1/order?filter=orderfulfillmentstatus:%7BFULFILLED%7D"
CANCELLED_ORDERS_URL = "https://api.ebay.com/sell/fulfillment/v1/order?filter=orderfulfillmentstatus:%7BCANCELLED%7D"
SELLER_FUNDS_SUMMARY_URL = "https://apiz.ebay.com/sell/finances/v1/seller_funds_summary"
TRANSACTION_SUMMARY_URL = "https://apiz.ebay.com/sell/finances/v1/transaction_summary"
RETURN_REQUESTS_URL = "https://api.ebay.com/post-order/v2/return/search"
CANCELLATION_REQUESTS_URL = "https://api.ebay.com/post-order/v2/cancellation/search"
ACTIVE_LISTINGS_URL = "https://api.ebay.com/sell/inventory/v1/inventory_item?status=ACTIVE&limit=1"
TRAFFIC_REPORT_URL = (
    "https://api.ebay.com/sell/analytics/v1/traffic_report?dimension=LISTING"
    "&metric=LISTING_IMPRESSION,LISTING_VIEWS"
)


EBAY_QUERIES_SENSOR: tuple[SensorEntityDescription, ...] = (
    SensorEntityDescription(
        key="ebay_total_unfulfilled_orders",
        name="eBay Total Unfulfilled Orders",
        icon="mdi:package-variant-closed",
    ),
    SensorEntityDescription(
        key="ebay_orders_due_today",
        name="eBay Orders Due Today",
        icon="mdi:package-variant-closed",
    ),
    SensorEntityDescription(
        key="ebay_available_funds",
        name="eBay Available Funds",
        icon="mdi:currency-usd",
        native_unit_of_measurement="USD",
    ),
    SensorEntityDescription(
        key="ebay_funds_on_hold",
        name="eBay Funds on Hold",
        icon="mdi:currency-usd",
        native_unit_of_measurement="USD",
    ),
    SensorEntityDescription(
        key="ebay_processing_funds",
        name="eBay Funds Processing",
        icon="mdi:currency-usd",
        native_unit_of_measurement="USD",
    ),
    SensorEntityDescription(
        key="ebay_total_funds",
        name="eBay Total Funds",
        icon="mdi:currency-usd",
        native_unit_of_measurement="USD",
    ),
    SensorEntityDescription(
        key="ebay_sales_today",
        name="eBay Sales Today",
        icon="mdi:currency-usd",
        native_unit_of_measurement="USD",
    ),
    SensorEntityDescription(
        key="ebay_sales_this_week",
        name="eBay Sales This Week",
        icon="mdi:currency-usd",
        native_unit_of_measurement="USD",
    ),
    SensorEntityDescription(
        key="ebay_sales_this_month",
        name="eBay Sales This Month",
        icon="mdi:currency-usd",
        native_unit_of_measurement="USD",
    ),
    SensorEntityDescription(
        key="ebay_refunds_today",
        name="eBay Refunds Today",
        icon="mdi:cash-refund",
        native_unit_of_measurement="USD",
    ),
    SensorEntityDescription(
        key="ebay_refunds_this_week",
        name="eBay Refunds This Week",
        icon="mdi:cash-refund",
        native_unit_of_measurement="USD",
    ),
    SensorEntityDescription(
        key="ebay_refunds_this_month",
        name="eBay Refunds This Month",
        icon="mdi:cash-refund",
        native_unit_of_measurement="USD",
    ),
    SensorEntityDescription(
        key="ebay_orders_awaiting_payment",
        name="eBay Orders Awaiting Payment",
        icon="mdi:cash-clock",
    ),
    SensorEntityDescription(
        key="ebay_fulfilled_orders",
        name="eBay Fulfilled Orders",
        icon="mdi:package-variant-closed-check",
    ),
    SensorEntityDescription(
        key="ebay_cancelled_orders",
        name="eBay Cancelled Orders",
        icon="mdi:package-variant-closed-remove",
    ),
    SensorEntityDescription(
        key="ebay_return_requests",
        name="eBay Return Requests",
        icon="mdi:clipboard-list",
    ),
    SensorEntityDescription(
        key="ebay_cancellation_requests",
        name="eBay Cancellation Requests",
        icon="mdi:cancel",
    ),
    SensorEntityDescription(
        key="ebay_active_listings",
        name="eBay Active Listings",
        icon="mdi:storefront-outline",
    ),
    SensorEntityDescription(
        key="ebay_listing_impressions",
        name="eBay Listing Impressions",
        icon="mdi:eye-outline",
    ),
    SensorEntityDescription(
        key="ebay_listing_page_views",
        name="eBay Listing Page Views",
        icon="mdi:eye",
    ),
    SensorEntityDescription(
        key="ebay_click_through_rate",
        name="eBay Click Through Rate",
        icon="mdi:cursor-pointer",
        native_unit_of_measurement="%",
    ),
)
