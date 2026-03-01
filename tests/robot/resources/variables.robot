*** Variables ***
# ─── API Settings ──────────────────────────────────────────────────────────────
${BASE_URL}             https://restful-booker.herokuapp.com
${AUTH_ENDPOINT}        ${BASE_URL}/auth
${BOOKING_ENDPOINT}     ${BASE_URL}/booking
${ADMIN_USER}           admin
${ADMIN_PASSWORD}       password123

# ─── UI Settings ───────────────────────────────────────────────────────────────
${UI_BASE_URL}          https://automationintesting.online
${BROWSER}              chromium
${HEADLESS}             true

# ─── Timeouts ──────────────────────────────────────────────────────────────────
${DEFAULT_TIMEOUT}      30s
${SHORT_TIMEOUT}        10s

# ─── Test Data ─────────────────────────────────────────────────────────────────
${VALID_FIRSTNAME}      Robot
${VALID_LASTNAME}       Testington
${VALID_PRICE}          200
${VALID_CHECKIN}        2025-06-01
${VALID_CHECKOUT}       2025-06-07
