"""
Notation des réponses aux campagnes d'évaluation.

Les règles sont rassemblées ici plutôt que dispersées dans les endpoints :
un score d'auto-évaluation devient une pièce d'audit, il doit pouvoir être
expliqué et rejoué à l'identique.

Barème, volontairement simple et explicite :
  - « oui / non » : oui → 100, non → 0
  - « échelle 1 à 5 » : 1 → 0, 2 → 25, 3 → 50, 4 → 75, 5 → 100
  - « texte libre » et « choix » : non notés (ils documentent, ils ne mesurent
    pas — aucune échelle d'options n'existe dans le modèle de données)

Le score de la campagne est la moyenne des seules réponses notables. Une
réponse non notable n'améliore ni ne dégrade le résultat.

Déclenchement : une question marquée `is_risk_trigger` dont la réponse notée
tombe à 50 ou moins est signalée au contrôleur. Elle ne crée pas de risque
automatiquement — la qualification reste un acte humain, et un registre des
risques qui se remplit tout seul perd sa valeur probante.
"""

from typing import Optional

TRIGGER_THRESHOLD = 50.0

_YES = {"oui", "yes", "true", "1", "conforme"}
_NO = {"non", "no", "false", "0", "non_conforme"}


def score_answer(question_type: str, value: Optional[str]) -> Optional[float]:
    """Note une réponse sur 100, ou None si la question n'est pas notable."""
    if value is None:
        return None

    raw = str(value).strip().lower()
    if raw == "":
        return None

    if question_type == "yes_no":
        if raw in _YES:
            return 100.0
        if raw in _NO:
            return 0.0
        return None

    if question_type == "scale_1_5":
        try:
            level = int(float(raw))
        except ValueError:
            return None
        if not 1 <= level <= 5:
            return None
        return round((level - 1) / 4 * 100, 1)

    # text, choice : documentent sans mesurer.
    return None


def is_triggered(is_risk_trigger: bool, scored_value: Optional[float]) -> bool:
    """Vrai si la réponse mérite d'être portée à l'attention du contrôleur."""
    if not is_risk_trigger or scored_value is None:
        return False
    return scored_value <= TRIGGER_THRESHOLD


def campaign_score(scored_values: list) -> float:
    """Moyenne des réponses notables, sur 100. 0 si aucune n'est notable."""
    values = [v for v in scored_values if v is not None]
    if not values:
        return 0.0
    return round(sum(values) / len(values), 1)
