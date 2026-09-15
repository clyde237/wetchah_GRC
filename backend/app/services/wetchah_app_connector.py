"""
Connecteur vers l'API de reporting de wetchah_app (le PMS d'exploitation).

Règle cardinale de ce module : **ne jamais fabriquer de donnée financière**.

Le GRC est un outil de contrôle de gestion et d'audit : un chiffre affiché ici
est lu comme un constat opposable. Si le PMS ne répond pas, la seule réponse
acceptable est de le dire. Une valeur de repli plausible — un écart de caisse
inventé, un taux d'occupation crédible — ferait auditer une réalité qui
n'existe pas, et ruinerait la valeur probante de l'ensemble du module.

Chaque méthode renvoie donc une enveloppe explicite :
    {"available": True,  "fetched_at": "...", "source": "...", **données}
    {"available": False, "fetched_at": "...", "error": "...", "reason": "..."}

`reason` est un code stable, destiné au front ; `error` est le message lisible.
"""

import logging
from datetime import datetime, timezone
from typing import Any, Dict, Optional, Tuple

import httpx

from app.core.config import settings

logger = logging.getLogger(__name__)

# Codes de `reason` — stables, destinés à l'affichage côté front.
REASON_NOT_CONFIGURED = "not_configured"
REASON_UNAUTHORIZED = "unauthorized"
REASON_UNAVAILABLE = "unavailable"
REASON_UNREACHABLE = "unreachable"
REASON_BAD_PAYLOAD = "bad_payload"


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _failure(reason: str, error: str, endpoint: str) -> Dict[str, Any]:
    return {
        "available": False,
        "fetched_at": _now(),
        "reason": reason,
        "error": error,
        "source": f"{settings.ERP_API_URL.rstrip('/')}{endpoint}",
    }


def _success(data: Dict[str, Any], endpoint: str) -> Dict[str, Any]:
    envelope = {
        "available": True,
        "fetched_at": _now(),
        "source": f"{settings.ERP_API_URL.rstrip('/')}{endpoint}",
    }
    envelope.update(data)
    return envelope


class WetchahAppConnector:
    def __init__(self):
        self.base_url = settings.ERP_API_URL.rstrip("/")

    @property
    def _headers(self) -> Dict[str, str]:
        return {
            "Authorization": f"Bearer {settings.REPORTING_SECRET}",
            "Accept": "application/json",
        }

    async def _fetch(self, endpoint: str) -> Tuple[Optional[Dict[str, Any]], Optional[Dict[str, Any]]]:
        """
        Renvoie (données, échec) : exactement l'un des deux est non nul.
        Aucune valeur de repli n'est produite ici ni par les appelants.
        """
        if not settings.REPORTING_SECRET:
            return None, _failure(
                REASON_NOT_CONFIGURED,
                "Le jeton de reporting (REPORTING_SECRET) n'est pas configuré pour cet "
                "établissement : le GRC ne peut pas interroger le PMS.",
                endpoint,
            )

        url = f"{self.base_url}{endpoint}"

        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(url, headers=self._headers)
        except Exception as exc:
            logger.error("PMS injoignable sur %s : %s", url, exc)
            return None, _failure(
                REASON_UNREACHABLE,
                f"Le PMS est injoignable ({exc.__class__.__name__}).",
                endpoint,
            )

        if response.status_code == 401:
            logger.error("Jeton de reporting refusé par le PMS sur %s", url)
            return None, _failure(
                REASON_UNAUTHORIZED,
                "Le PMS a refusé le jeton de reporting (401). La clé partagée diffère "
                "entre le GRC et l'établissement.",
                endpoint,
            )

        if response.status_code == 503:
            logger.warning("API de reporting désactivée côté PMS sur %s", url)
            return None, _failure(
                REASON_UNAVAILABLE,
                "L'API de reporting est désactivée sur cet établissement "
                "(module « api » non activé).",
                endpoint,
            )

        if response.status_code != 200:
            logger.warning("Réponse inattendue du PMS sur %s : %s", url, response.status_code)
            return None, _failure(
                REASON_UNAVAILABLE,
                f"Le PMS a répondu {response.status_code}.",
                endpoint,
            )

        try:
            payload = response.json()
        except ValueError:
            logger.error("Réponse non-JSON du PMS sur %s", url)
            return None, _failure(
                REASON_BAD_PAYLOAD,
                "Le PMS a renvoyé une réponse illisible (JSON attendu).",
                endpoint,
            )

        if not isinstance(payload, dict):
            return None, _failure(
                REASON_BAD_PAYLOAD,
                "Le PMS a renvoyé une structure inattendue (objet JSON attendu).",
                endpoint,
            )

        return payload, None

    async def _envelope(self, endpoint: str) -> Dict[str, Any]:
        data, failure = await self._fetch(endpoint)
        if failure is not None:
            return failure
        return _success(data, endpoint)

    async def get_financial_summary(self) -> Dict[str, Any]:
        return await self._envelope("/api/reporting/summary")

    async def get_cash_audit(self) -> Dict[str, Any]:
        return await self._envelope("/api/reporting/cash-audit")

    async def get_alerts_anomalies(self) -> Dict[str, Any]:
        return await self._envelope("/api/reporting/alerts")


wetchah_connector = WetchahAppConnector()
