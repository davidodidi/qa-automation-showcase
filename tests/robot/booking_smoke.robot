*** Settings ***
Documentation     Restful-Booker Regression Suite
...               Covers edge cases, negative paths, and data integrity checks
...               that run nightly or before major releases.

Library           RequestsLibrary
Library           Collections
Library           String
Resource          resources/keywords.robot
Resource          resources/variables.robot

Suite Setup       Create API Session
Suite Teardown    Delete All Sessions


*** Test Cases ***

Booking List — Every Item Has A bookingid
    [Documentation]    Every item in GET /booking must include a bookingid key.
    [Tags]    regression    api
    ${resp}=    GET On Session    booking_api    /booking
    ${items}=   Set Variable      ${resp.json()}
    FOR    ${item}    IN    @{items}
        Dictionary Should Contain Key    ${item}    bookingid
    END

Auth — Empty Username Rejected
    [Documentation]    Auth with an empty username should not return a valid token.
    [Tags]    regression    api    auth    negative
    ${body}=    Create Dictionary    username=${EMPTY}    password=${ADMIN_PASSWORD}
    ${resp}=    POST On Session    booking_api    /auth    json=${body}
    ${data}=    Set Variable    ${resp.json()}
    Run Keyword If    'token' in $data
    ...    Should Be Equal    ${data}[reason]    Bad credentials

Auth — Empty Password Rejected
    [Documentation]    Auth with an empty password should not return a valid token.
    [Tags]    regression    api    auth    negative
    ${body}=    Create Dictionary    username=${ADMIN_USER}    password=${EMPTY}
    ${resp}=    POST On Session    booking_api    /auth    json=${body}
    ${data}=    Set Variable    ${resp.json()}
    Run Keyword If    'token' in $data
    ...    Should Be Equal    ${data}[reason]    Bad credentials

Booking — Non-existent ID Returns 404
    [Documentation]    Requesting a booking with an impossible ID must return 404.
    [Tags]    regression    api    negative
    ${resp}=    GET On Session    booking_api    /booking/999999999
    ...         expected_status=any
    Should Be Equal As Integers    ${resp.status_code}    404

Update Without Token — Returns 403
    [Documentation]    A PUT request without a valid cookie must return 403.
    [Tags]    regression    api    security
    ${payload}=    Build Booking Payload
    ${booking_id}=    Create Booking And Get ID    ${payload}
    ${update}=        Build Booking Payload    firstname=Unauthorised
    ${resp}=          PUT On Session    booking_api    /booking/${booking_id}
    ...               json=${update}    expected_status=any
    Should Be Equal As Integers    ${resp.status_code}    403
    # Cleanup
    ${token}=    Get Auth Token
    Delete Booking    ${booking_id}    ${token}

Booking Dates — Checkin Before Checkout
    [Documentation]    A booking with checkin after checkout is an invalid scenario.
    [Tags]    regression    api    data-integrity
    ${payload}=    Build Booking Payload
    ...            checkin=2025-12-31
    ...            checkout=2025-01-01
    ${resp}=       POST On Session    booking_api    /booking
    ...            json=${payload}    expected_status=any
    # The API may accept or reject — we log and document behaviour
    Log    Status for reversed dates: ${resp.status_code}
    Log    Body: ${resp.text}

Response Time — Create Booking Under 5s
    [Documentation]    Creating a booking must respond within 5 seconds.
    [Tags]    regression    api    performance
    ${payload}=       Build Booking Payload
    ${resp}=          POST On Session    booking_api    /booking    json=${payload}
    Response Time Should Be Acceptable    ${resp}    5
    ${token}=         Get Auth Token
    ${booking_id}=    Get From Dictionary    ${resp.json()}    bookingid
    Delete Booking    ${booking_id}    ${token}

Data Integrity — depositpaid Field Is Boolean
    [Documentation]    The depositpaid field returned by the API must be a boolean.
    [Tags]    regression    api    data-integrity
    ${payload}=       Build Booking Payload    deposit=${True}
    ${booking_id}=    Create Booking And Get ID    ${payload}
    ${resp}=          Get Booking By ID    ${booking_id}
    ${deposit}=       Get From Dictionary    ${resp.json()}    depositpaid
    Should Be True    isinstance($deposit, bool)
    ...    msg=depositpaid should be boolean, got: ${deposit}
    ${token}=    Get Auth Token
    Delete Booking    ${booking_id}    ${token}
