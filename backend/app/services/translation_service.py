import httpx

from app.core.config import settings


class TranslationService:
    """Translate listing text using DeepL or Google Translate."""

    async def translate(self, text: str, target_lang: str = "EN") -> str | None:
        if settings.DEEPL_API_KEY:
            return await self._translate_deepl(text, target_lang)
        if settings.GOOGLE_TRANSLATE_API_KEY:
            return await self._translate_google(text, target_lang)
        return None

    async def _translate_deepl(self, text: str, target_lang: str) -> str:
        async with httpx.AsyncClient() as client:
            resp = await client.post(
                "https://api-free.deepl.com/v2/translate",
                data={
                    "auth_key": settings.DEEPL_API_KEY,
                    "text": text,
                    "target_lang": target_lang,
                },
            )
            resp.raise_for_status()
            return resp.json()["translations"][0]["text"]

    async def _translate_google(self, text: str, target_lang: str) -> str:
        async with httpx.AsyncClient() as client:
            resp = await client.post(
                "https://translation.googleapis.com/language/translate/v2",
                params={"key": settings.GOOGLE_TRANSLATE_API_KEY},
                json={
                    "q": text,
                    "target": target_lang.lower(),
                    "format": "text",
                },
            )
            resp.raise_for_status()
            return resp.json()["data"]["translations"][0]["translatedText"]
