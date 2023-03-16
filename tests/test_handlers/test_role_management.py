from uuid import uuid4

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
    promoted_user_from_db = await get_user_from_database(
        data_from_resp["promoted_user_id"]
    )
    assert len(promoted_user_from_db) == 1
    promoted_user_from_db = dict(promoted_user_from_db[0])
    assert promoted_user_from_db["user_id"] == user_data_for_promotion["user_id"]
