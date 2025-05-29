import httpx
from bot.auth_services.auth_services import get_tokens, get_refresh_tokens
from bot.token_utils.session_manager import save_tokens
from bot.config_data.config import API_URL


class APIClient:
    def __init__(self, chat_id):
        self.chat_id = chat_id

    async def _refresh(self, refresh_token):
        data = await get_refresh_tokens(refresh_token)

        if not data:
            return None

        access_token, refresh_token, _ = data
        await save_tokens(self.chat_id, access_token, refresh_token)

        return access_token

    async def request(self, method, path, **kwargs) -> httpx.Response:
        tokens = await get_tokens(self.chat_id)
        if not tokens:
            raise httpx.HTTPError(
                f"Unauthorized: no tokens found for chat_id={self.chat_id}"
            )

        headers = kwargs.pop("headers", {})
        headers["Authorization"] = f"Bearer {tokens['access_token']}"

        async with httpx.AsyncClient() as client:
            resp = await client.request(
                method, API_URL + path, **kwargs, headers=headers
            )

            if resp.status_code == 401:
                new_access = await self._refresh(tokens["refresh_token"])
                if not new_access:
                    return resp

                headers["Authorization"] = f"Bearer {new_access}"
                resp = await client.request(
                    method, API_URL + path, **kwargs, headers=headers
                )

        return resp

    async def post(self, path: str, **kwargs) -> httpx.Response:
        return await self.request("POST", path, **kwargs)

    async def get(self, path: str, **kwargs) -> httpx.Response:
        return await self.request("GET", path, **kwargs)
