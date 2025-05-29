import httpx
from bot.config_data.config import API_URL
from bot.token_utils.session_manager import get_tokens, save_tokens


async def get_refresh_tokens(refresh_token: str):
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{API_URL}/auth/token/refresh",
                headers={"Authorization": f"Bearer {refresh_token}"},
            )
            if response.status_code == 200:
                data = response.json()

                return data["access_token"], data["refresh_token"], data["chat_id"]
            else:
                return None
    except httpx.HTTPError:
        return None


async def ensure_access(chat_id: int):
    tokens = await get_tokens(chat_id)
    if not tokens:
        return False
    async with httpx.AsyncClient() as client:
        resp = await client.get(
            f"{API_URL}/auth/user/me",
            headers={"Authorization": f"Bearer {tokens['access_token']}"},
        )

    if resp.status_code == 200:
        return True
    elif resp.status_code == 401:
        # access просрочен, пытаемся обновить
        data = await get_refresh_tokens(tokens["refresh_token"])
        if not data:
            return False
        access, refresh, chat_id = data
        await save_tokens(chat_id, access, refresh)
        return True
    else:
        return False
