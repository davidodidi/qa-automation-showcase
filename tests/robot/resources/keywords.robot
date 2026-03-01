*** Settings ***
Library     RequestsLibrary
Library     Collections
Library     String
Library     OperatingSystem
Resource    variables.robot


*** Keywords ***
# ─── Session Management ────────────────────────────────────────────────────────

Create API Session
    [Documentation]    Creates a persistent HTTP session for the booking API.
    Create Session    booking_api    ${BASE_URL}    verify=True

Get Auth Token
    [Documentation]    Authenticates with admin credentials and returns a token.
    RETURN          ${token}
    ${body}=          Create Dictionary    username=${ADMIN_USER}    password=${ADMIN_PASSWORD}
    ${resp}=          POST On Session    booking_api    /auth    json=${body}
    Should Be Equal As Integers    ${resp.status_code}    200
    ${token}=         Get From Dictionary    ${resp.json()}    token
    Should Not Be Empty    ${token}
    Log    Obtained auth token: ${token}

# ─── Booking Helpers ──────────────────────────────────────────────────────────

Build Booking Payload
    [Documentation]    Returns a booking payload dictionary.
    [Arguments]    ${firstname}=${VALID_FIRSTNAME}
    ...            ${lastname}=${VALID_LASTNAME}
    ...            ${price}=${VALID_PRICE}
    ...            ${deposit}=${True}
    ...            ${checkin}=${VALID_CHECKIN}
    ...            ${checkout}=${VALID_CHECKOUT}
    ...            ${needs}=Breakfast
    ${dates}=         Create Dictionary    checkin=${checkin}    checkout=${checkout}
    ${payload}=       Create Dictionary
    ...               firstname=${firstname}
    ...               lastname=${lastname}
    ...               totalprice=${price}
    ...               depositpaid=${deposit}
    ...               bookingdates=${dates}
    ...               additionalneeds=${needs}
    RETURN    ${payload}

Create Booking And Get ID
    [Documentation]    Creates a booking and returns the booking ID.
    [Arguments]    ${payload}
    ${resp}=          POST On Session    booking_api    /booking    json=${payload}
    Should Be Equal As Integers    ${resp.status_code}    200
    ${booking_id}=    Get From Dictionary    ${resp.json()}    bookingid
    Log    Created booking with ID: ${booking_id}
    RETURN    ${booking_id}

Get Booking By ID
    [Documentation]    Fetches a single booking and returns the response.
    [Arguments]    ${booking_id}
    ${resp}=    GET On Session    booking_api    /booking/${booking_id}
    RETURN    ${resp}

Delete Booking
    [Documentation]    Deletes a booking using the auth token cookie.
    [Arguments]    ${booking_id}    ${token}
    ${headers}=    Create Dictionary    Cookie=token=${token}
    ${resp}=       DELETE On Session    booking_api    /booking/${booking_id}    headers=${headers}
    Should Be Equal As Integers    ${resp.status_code}    201
    Log    Deleted booking: ${booking_id}

# ─── Assertion Keywords ───────────────────────────────────────────────────────

Booking Should Have Field
    [Documentation]    Asserts a booking response contains a field with an expected value.
    [Arguments]    ${resp}    ${field}    ${expected}
    ${booking}=    Set Variable    ${resp.json()}
    ${actual}=     Get From Dictionary    ${booking}    ${field}
    Should Be Equal As Strings    ${actual}    ${expected}
    ...    msg=Field '${field}': expected '${expected}', got '${actual}'

Response Time Should Be Acceptable
    [Documentation]    Asserts the response elapsed time is below threshold (seconds).
    [Arguments]    ${resp}    ${max_seconds}=3
    ${elapsed}=    Set Variable    ${resp.elapsed.total_seconds()}
    Should Be True    ${elapsed} < ${max_seconds}
    ...    msg=Response too slow: ${elapsed}s > ${max_seconds}s
