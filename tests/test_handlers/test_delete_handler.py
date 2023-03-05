from uuid import uuid4

import pytest

from tests.conftest import create_test_auth_headers_for_user


async def test_delete_user(client, create_user_in_database, get_user_from_database):
    user_data = {
        "user_id": uuid4(),
        "name": "Nikolai",
        "surname": "Sviridov",
        "email": "lol@kek.com",
        "is_active": True,
        "hashed_password": "SampleHashedPass",
        "roles": ["ROLE_PORTAL_USER"],
    }
    await create_user_in_database(**user_data)
    resp = client.delete(
        f"/user/?user_id={user_data['user_id']}",
        headers=create_test_auth_headers_for_user(user_data["email"]),
    )
    assert resp.status_code == 200
    assert resp.json() == {"deleted_user_id": str(user_data["user_id"])}
    users_from_db = await get_user_from_database(user_data["user_id"])
    user_from_db = dict(users_from_db[0])
    assert user_from_db["name"] == user_data["name"]
    assert user_from_db["surname"] == user_data["surname"]
    assert user_from_db["email"] == user_data["email"]
    assert user_from_db["is_active"] is False
    assert user_from_db["user_id"] == user_data["user_id"]


async def test_delete_user_not_found(client, create_user_in_database):
    user_data_for_database = {
        "user_id": uuid4(),
        "name": "Nikolai",
        "surname": "Sviridov",
        "email": "lol@kek.com",
        "is_active": True,
        "hashed_password": "SampleHashedPass",
        "roles": ["ROLE_PORTAL_USER"],
    }
    user_data = {
        "user_id": uuid4(),
        "name": "Admin",
        "surname": "Adminov",
        "email": "admin@kek.com",
        "is_active": True,
        "hashed_password": "SampleHashedPass",
        "roles": ["ROLE_PORTAL_USER", "ROLE_PORTAL_SUPERADMIN"],
    }
    await create_user_in_database(**user_data_for_database)
    await create_user_in_database(**user_data)
    user_id_not_exists_user = uuid4()
    resp = client.delete(
        f"/user/?user_id={user_id_not_exists_user}",
        headers=create_test_auth_headers_for_user(user_data["email"]),
    )
    assert resp.status_code == 404
    assert resp.json() == {
        "detail": f"User with id {user_id_not_exists_user} not found."
    }


async def test_delete_user_user_id_validation_error(client, create_user_in_database):
    user_data = {
        "user_id": uuid4(),
        "name": "Nikolai",
        "surname": "Sviridov",
        "email": "lol@kek.com",
        "is_active": True,
        "hashed_password": "SampleHashedPass",
        "roles": ["ROLE_PORTAL_USER"],
    }
    await create_user_in_database(**user_data)
    resp = client.delete(
        "/user/?user_id=123",
        headers=create_test_auth_headers_for_user(user_data["email"]),
    )
    assert resp.status_code == 422
    data_from_response = resp.json()
    assert data_from_response == {
        "detail": [
            {
                "loc": ["query", "user_id"],
                "msg": "value is not a valid uuid",
                "type": "type_error.uuid",
            }
        ]
    }


async def test_delete_user_bad_cred(client, create_user_in_database):
    user_data = {
        "user_id": uuid4(),
        "name": "Nikolai",
        "surname": "Sviridov",
        "email": "lol@kek.com",
        "is_active": True,
        "hashed_password": "SampleHashedPass",
        "roles": ["ROLE_PORTAL_USER"],
    }
    await create_user_in_database(**user_data)
    user_id = uuid4()
    resp = client.delete(
        f"/user/?user_id={user_id}",
        headers=create_test_auth_headers_for_user(user_data["email"] + "a"),
    )
    assert resp.status_code == 401
    assert resp.json() == {"detail": "Could not validate credentials"}


async def test_delete_user_unauth(client, create_user_in_database):
    user_data = {
        "user_id": uuid4(),
        "name": "Nikolai",
        "surname": "Sviridov",
        "email": "lol@kek.com",
        "is_active": True,
        "hashed_password": "SampleHashedPass",
        "roles": ["ROLE_PORTAL_USER"],
    }
    await create_user_in_database(**user_data)
    user_id = uuid4()
    bad_auth_headers = create_test_auth_headers_for_user(user_data["email"])
    bad_auth_headers["Authorization"] += "a"
    resp = client.delete(
        f"/user/?user_id={user_id}",
        headers=bad_auth_headers,
    )
    assert resp.status_code == 401
    assert resp.json() == {"detail": "Could not validate credentials"}


async def test_delete_user_no_jwt(client, create_user_in_database):
    user_data = {
        "user_id": uuid4(),
        "name": "Nikolai",
        "surname": "Sviridov",
        "email": "lol@kek.com",
        "is_active": True,
        "hashed_password": "SampleHashedPass",
        "roles": ["ROLE_PORTAL_USER"],
    }
    await create_user_in_database(**user_data)
    user_id = uuid4()
    resp = client.delete(
        f"/user/?user_id={user_id}",
    )
    assert resp.status_code == 401
    assert resp.json() == {"detail": "Not authenticated"}


@pytest.mark.parametrize(
    "user_role_list",
    [
        ["ROLE_PORTAL_USER", "ROLE_PORTAL_ADMIN"],
        ["ROLE_PORTAL_USER", "ROLE_PORTAL_SUPERADMIN"],
    ],
)
async def test_delete_user_by_privilege_roles(
    client, create_user_in_database, get_user_from_database, user_role_list
):
    user_data_for_deletion = {
        "user_id": uuid4(),
        "name": "Nikolai",
        "surname": "Sviridov",
        "email": "lol@kek.com",
        "is_active": True,
        "hashed_password": "SampleHashedPass",
        "roles": ["ROLE_PORTAL_USER"],
    }
    user_data = {
        "user_id": uuid4(),
        "name": "Admin",
        "surname": "Adminov",
        "email": "admin@kek.com",
        "is_active": True,
        "hashed_password": "SampleHashedPass",
        "roles": user_role_list,
    }
    await create_user_in_database(**user_data_for_deletion)
    await create_user_in_database(**user_data)
    resp = client.delete(
        f"/user/?user_id={user_data_for_deletion['user_id']}",
        headers=create_test_auth_headers_for_user(user_data["email"]),
    )
    assert resp.status_code == 200
    assert resp.json() == {"deleted_user_id": str(user_data_for_deletion["user_id"])}
    users_from_db = await get_user_from_database(user_data_for_deletion["user_id"])
    user_from_db = dict(users_from_db[0])
    assert user_from_db["name"] == user_data_for_deletion["name"]
    assert user_from_db["surname"] == user_data_for_deletion["surname"]
    assert user_from_db["email"] == user_data_for_deletion["email"]
    assert user_from_db["is_active"] is False
    assert user_from_db["user_id"] == user_data_for_deletion["user_id"]


@pytest.mark.parametrize(
    "user_for_deletion, user_who_delete",
    [
        (
            {
                "user_id": uuid4(),
                "name": "Nikolai",
                "surname": "Sviridov",
                "email": "lol@kek.com",
                "is_active": True,
                "hashed_password": "SampleHashedPass",
                "roles": ["ROLE_PORTAL_USER"],
            },
            {
                "user_id": uuid4(),
                "name": "Admin",
                "surname": "Adminov",
                "email": "admin@kek.com",
                "is_active": True,
                "hashed_password": "SampleHashedPass",
                "roles": ["ROLE_PORTAL_USER"],
            },
        ),
        (
            {
                "user_id": uuid4(),
                "name": "Nikolai",
                "surname": "Sviridov",
                "email": "lol@kek.com",
                "is_active": True,
                "hashed_password": "SampleHashedPass",
                "roles": ["ROLE_PORTAL_USER", "ROLE_PORTAL_SUPERADMIN"],
            },
            {
                "user_id": uuid4(),
                "name": "Admin",
                "surname": "Adminov",
                "email": "admin@kek.com",
                "is_active": True,
                "hashed_password": "SampleHashedPass",
                "roles": ["ROLE_PORTAL_USER", "ROLE_PORTAL_ADMIN"],
            },
        ),
        (
            {
                "user_id": uuid4(),
                "name": "Nikolai",
                "surname": "Sviridov",
                "email": "lol@kek.com",
                "is_active": True,
                "hashed_password": "SampleHashedPass",
                "roles": ["ROLE_PORTAL_USER", "ROLE_PORTAL_ADMIN"],
            },
            {
                "user_id": uuid4(),
                "name": "Admin",
                "surname": "Adminov",
                "email": "admin@kek.com",
                "is_active": True,
                "hashed_password": "SampleHashedPass",
                "roles": ["ROLE_PORTAL_USER", "ROLE_PORTAL_ADMIN"],
            },
        ),
    ],
)
async def test_delete_another_user_error(
    client,
    create_user_in_database,
    get_user_from_database,
    user_for_deletion,
    user_who_delete,
):
    await create_user_in_database(**user_for_deletion)
    await create_user_in_database(**user_who_delete)
    resp = client.delete(
        f"/user/?user_id={user_for_deletion['user_id']}",
        headers=create_test_auth_headers_for_user(user_who_delete["email"]),
    )
    assert resp.status_code == 403
