import os
from unittest.mock import AsyncMock, MagicMock

from supabase import AClient, ASupabaseException, create_async_client


async def test_incorrect_values_dont_instantiate_client() -> None:
    """Ensure we can't instantiate client with invalid values."""
    try:
        client: AClient = await create_async_client(None, None)
    except ASupabaseException:
        pass


async def test_supabase_exception() -> None:
    try:
        raise ASupabaseException("err")
    except ASupabaseException:
        pass


async def test_postgrest_client() -> None:
    url = os.environ.get("SUPABASE_TEST_URL")
    key = os.environ.get("SUPABASE_TEST_KEY")

    client = await create_async_client(url, key)
    assert client.table("sample")


async def test_rpc_client() -> None:
    url = os.environ.get("SUPABASE_TEST_URL")
    key = os.environ.get("SUPABASE_TEST_KEY")

    client = await create_async_client(url, key)
    assert client.rpc("test_fn")


async def test_function_initialization() -> None:
    url = os.environ.get("SUPABASE_TEST_URL")
    key = os.environ.get("SUPABASE_TEST_KEY")

    client = await create_async_client(url, key)
    assert client.functions


async def test_schema_update() -> None:
    url = os.environ.get("SUPABASE_TEST_URL")
    key = os.environ.get("SUPABASE_TEST_KEY")

    client = await create_async_client(url, key)
    assert client.postgrest
    assert client.schema("new_schema")


async def test_updates_the_authorization_header_on_auth_events() -> None:
    url = os.environ.get("SUPABASE_TEST_URL")
    key = os.environ.get("SUPABASE_TEST_KEY")

    client = await create_async_client(url, key)

    assert client.options.headers.get("apiKey") == key
    assert client.options.headers.get("Authorization") == f"Bearer {key}"

    mock_session = MagicMock(access_token="secretuserjwt")
    realtime_mock = AsyncMock()
    client.realtime = realtime_mock

    client._listen_to_auth_events("SIGNED_IN", mock_session)

    updated_authorization = f"Bearer {mock_session.access_token}"

    assert client.options.headers.get("apiKey") == key
    assert client.options.headers.get("Authorization") == updated_authorization

    assert client.postgrest.session.headers.get("apiKey") == key
    assert (
        client.postgrest.session.headers.get("Authorization") == updated_authorization
    )

    assert client.auth._headers.get("apiKey") == key
    assert client.auth._headers.get("Authorization") == updated_authorization

    assert client.storage.session.headers.get("apiKey") == key
    assert client.storage.session.headers.get("Authorization") == updated_authorization

    realtime_mock.set_auth.assert_called_once_with(mock_session.access_token)
