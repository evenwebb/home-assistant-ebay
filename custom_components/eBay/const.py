"""Constants for the ebay integration."""
from homeassistant.components.sensor import SensorEntityDescription

DOMAIN = "ebay"
OAUTH2_AUTHORIZE = "https://auth.ebay.com/oauth2/authorize"
OAUTH2_TOKEN = "https://api.ebay.com/identity/v1/oauth2/token"
# Request fulfillment and finances scopes so financial endpoints work
SCOPES = (
    "https://api.ebay.com/oauth/api_scope/sell.fulfillment.readonly%20"
    "https://api.ebay.com/oauth/api_scope/sell.finances"
)
UNFULFILLED_ORDERS_URL = "https://api.ebay.com/sell/fulfillment/v1/order?filter=orderfulfillmentstatus:%7BNOT_STARTED%7CIN_PROGRESS%7D"
SELLER_FUNDS_SUMMARY_URL = "https://apiz.ebay.com/sell/finances/v1/seller_funds_summary"
TRANSACTION_SUMMARY_URL = "https://apiz.ebay.com/sell/finances/v1/transaction_summary"


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
)
