from uuid import uuid4

import pytest

from db.models import PortalRole
from tests.conftest import create_test_auth_headers_for_user


async def test_add_admin_role_to_user_by_superadmin(
    client, create_user_in_database, get_user_from_database
):
    user_data_for_promotion = {
        "user_id": uuid4(),
        "name": "Nikolai",
        "surname": "Sviridov",
        "email": "lol@kek.com",
        "is_active": True,
        "hashed_password": "SampleHashedPass",
        "roles": [PortalRole.ROLE_PORTAL_USER],
    }
    user_data_who_promoted = {
        "user_id": uuid4(),
        "name": "Ivan",
        "surname": "Ivanov",
        "email": "ivan@kek.com",
        "is_active": True,
        "hashed_password": "SampleHashedPass",
        "roles": [PortalRole.ROLE_PORTAL_SUPERADMIN],
    }
    for user_data in [user_data_for_promotion, user_data_who_promoted]:
        await create_user_in_database(**user_data)
    resp = client.patch(
        f"/user/admin_privilege?user_id={user_data_for_promotion['user_id']}",
        headers=create_test_auth_headers_for_user(user_data_who_promoted["email"]),
    )
    data_from_resp = resp.json()
    assert resp.status_code == 200
    updated_user_from_db = await get_user_from_database(
        data_from_resp["updated_user_id"]
    )
    assert len(updated_user_from_db) == 1
    updated_user_from_db = dict(updated_user_from_db[0])
    assert updated_user_from_db["user_id"] == user_data_for_promotion["user_id"]
    assert PortalRole.ROLE_PORTAL_ADMIN in updated_user_from_db["roles"]


async def test_revoke_admin_role_from_user_by_superadmin(
    client, create_user_in_database, get_user_from_database
):
    user_data_for_revoke = {
        "user_id": uuid4(),
        "name": "Nikolai",
        "surname": "Sviridov",
        "email": "lol@kek.com",
        "is_active": True,
        "hashed_password": "SampleHashedPass",
        "roles": [PortalRole.ROLE_PORTAL_USER, PortalRole.ROLE_PORTAL_ADMIN],
    }
    user_data_who_revoke = {
        "user_id": uuid4(),
        "name": "Ivan",
        "surname": "Ivanov",
        "email": "ivan@kek.com",
        "is_active": True,
        "hashed_password": "SampleHashedPass",
        "roles": [PortalRole.ROLE_PORTAL_SUPERADMIN],
    }
    for user_data in [user_data_for_revoke, user_data_who_revoke]:
        await create_user_in_database(**user_data)
    resp = client.delete(
        f"/user/admin_privilege?user_id={user_data_for_revoke['user_id']}",
        headers=create_test_auth_headers_for_user(user_data_who_revoke["email"]),
    )
    data_from_resp = resp.json()
    assert resp.status_code == 200
    revoked_user_from_db = await get_user_from_database(
        data_from_resp["updated_user_id"]
    )
    assert len(revoked_user_from_db) == 1
    revoked_user_from_db = dict(revoked_user_from_db[0])
    assert revoked_user_from_db["user_id"] == user_data_for_revoke["user_id"]
    assert PortalRole.ROLE_PORTAL_ADMIN not in revoked_user_from_db["roles"]


@pytest.mark.parametrize(
    "roles_of_who_revoke",
    [
        [PortalRole.ROLE_PORTAL_USER, PortalRole.ROLE_PORTAL_ADMIN],
        [
            PortalRole.ROLE_PORTAL_USER,
        ],
    ],
)
async def test_revoke_admin_role_from_user_by_wrong_type_of_user(
    client, create_user_in_database, get_user_from_database, roles_of_who_revoke
):
    user_data_for_revoke = {
        "user_id": uuid4(),
        "name": "Nikolai",
        "surname": "Sviridov",
        "email": "lol@kek.com",
        "is_active": True,
        "hashed_password": "SampleHashedPass",
        "roles": [PortalRole.ROLE_PORTAL_USER, PortalRole.ROLE_PORTAL_ADMIN],
    }
    user_data_who_revoke = {
        "user_id": uuid4(),
        "name": "Ivan",
        "surname": "Ivanov",
        "email": "ivan@kek.com",
        "is_active": True,
        "hashed_password": "SampleHashedPass",
        "roles": roles_of_who_revoke,
    }
    for user_data in [user_data_for_revoke, user_data_who_revoke]:
        await create_user_in_database(**user_data)
    resp = client.delete(
        f"/user/admin_privilege?user_id={user_data_for_revoke['user_id']}",
        headers=create_test_auth_headers_for_user(user_data_who_revoke["email"]),
    )
    data_from_resp = resp.json()
    assert resp.status_code == 403
    assert data_from_resp == {"detail": "Forbidden."}
    not_revoked_user_from_db = await get_user_from_database(
        user_data_for_revoke["user_id"]
    )
    assert len(not_revoked_user_from_db) == 1
    not_revoked_user_from_db = dict(not_revoked_user_from_db[0])
    assert not_revoked_user_from_db["user_id"] == user_data_for_revoke["user_id"]
    assert PortalRole.ROLE_PORTAL_ADMIN in not_revoked_user_from_db["roles"]
