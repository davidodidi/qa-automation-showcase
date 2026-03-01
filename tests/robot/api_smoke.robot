*** Settings ***
Documentation     Restful-Booker API Smoke Test Suite
...               Covers the core happy-path scenarios that prove the API is up
...               and functioning correctly. These run on every commit.
...
...               Tech: Robot Framework + RequestsLibrary
...               Target: https://restful-booker.herokuapp.com

Library           RequestsLibrary
Library           Collections
Resource          resources/keywords.robot
Resource          resources/variables.robot

Suite Setup       Create API Session
Suite Teardown    Delete All Sessions


*** Test Cases ***

Health Check — API Is Reachable
    [Documentation]    The root /booking endpoint must return a 200 status.
    [Tags]    smoke    api
    ${resp}=    GET On Session    booking_api    /booking
    Should Be Equal As Integers    ${resp.status_code}    200

Auth — Valid Credentials Return Token
    [Documentation]    Admin credentials must produce a non-empty token.
    [Tags]    smoke    api    auth
    ${body}=      Create Dictionary    username=${ADMIN_USER}    password=${ADMIN_PASSWORD}
    ${resp}=      POST On Session    booking_api    /auth    json=${body}
    Should Be Equal As Integers    ${resp.status_code}    200
    ${token}=     Get From Dictionary    ${resp.json()}    token
    Should Not Be Empty    ${token}
    Should Not Be Equal    ${token}    Bad credentials

Create Booking — Returns 200 With Booking ID
    [Documentation]    POSTing a valid payload must return a bookingid integer.
    [Tags]    smoke    api    booking
    ${payload}=      Build Booking Payload
    ${booking_id}=   Create Booking And Get ID    ${payload}
    Should Be True    ${booking_id} > 0
    # Cleanup
    ${token}=        Get Auth Token
    Delete Booking    ${booking_id}    ${token}

Get Booking — Returns Correct Data
    [Documentation]    A fetched booking must match the payload that created it.
    [Tags]    smoke    api    booking
    ${payload}=    Build Booking Payload    firstname=RobotSmoke    lastname=Test
    ${token}=      Get Auth Token
    ${booking_id}=    Create Booking And Get ID    ${payload}
    ${resp}=          Get Booking By ID    ${booking_id}
    Should Be Equal As Integers    ${resp.status_code}    200
    Booking Should Have Field    ${resp}    firstname    RobotSmoke
    Booking Should Have Field    ${resp}    lastname     Test
    Delete Booking    ${booking_id}    ${token}

Delete Booking — Returns 201
    [Documentation]    Deleting an existing booking must return status 201.
    [Tags]    smoke    api    booking
    ${payload}=       Build Booking Payload
    ${token}=         Get Auth Token
    ${booking_id}=    Create Booking And Get ID    ${payload}
    Delete Booking    ${booking_id}    ${token}    # assertion inside keyword

CRUD Lifecycle — Create Read Update Delete
    [Documentation]    Full booking lifecycle in a single test to validate end-to-end flow.
    [Tags]    smoke    api    crud
    ${token}=         Get Auth Token
    ${payload}=       Build Booking Payload    firstname=CRUDTest    lastname=Robot
    
    # CREATE
    ${booking_id}=    Create Booking And Get ID    ${payload}
    Should Be True    ${booking_id} > 0

    # READ
    ${resp}=    Get Booking By ID    ${booking_id}
    Should Be Equal As Integers    ${resp.status_code}    200
    Booking Should Have Field    ${resp}    firstname    CRUDTest

    # UPDATE (PATCH)
    ${patch}=         Create Dictionary    firstname=UpdatedByRobot
    ${headers}=       Create Dictionary    Cookie=token=${token}    Content-Type=application/json
    ${patch_resp}=    PATCH On Session    booking_api    /booking/${booking_id}
    ...               json=${patch}    headers=${headers}
    Should Be Equal As Integers    ${patch_resp.status_code}    200
    Booking Should Have Field    ${patch_resp}    firstname    UpdatedByRobot

    # DELETE
    Delete Booking    ${booking_id}    ${token}

    # VERIFY DELETED
    ${del_resp}=    GET On Session    booking_api    /booking/${booking_id}
    ...             expected_status=any
    Should Be Equal As Integers    ${del_resp.status_code}    404
