import httpx
from bot.config_data.config import API_URL
from bot.token_utils.session_manager import get_tokens, save_tokens


async def get_refresh_tokens(refresh_token: str):

    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{API_URL}/token/refresh",
                json={"refresh_token": refresh_token}
            )
            if response.status_code == 200:
                data = response.json()

                return data["access_token"], data["refresh_token"], data["token_type"]
            else:
                return None
    except httpx.HTTPError:
        return None


async def ensure_access(chat_id: int):

    local_token =  await get_tokens(chat_id)
    if not local_token:
        return False

    access_token = local_token["access_token"]
    refresh_token = local_token["refresh_token"]
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{API_URL}/user/me",
                                        headers={"Authorization": f"Bear {access_token}"}
                                        )
            if response.status_code == 200:
                return True
            else:
                return None

    except httpx.HTTPError:
        data = await get_refresh_tokens(refresh_token)
        if data:
            access_token, refresh_token, chat_id = data
        else:
            return None

        await save_tokens(chat_id, access_token, refresh_token)
        return True
