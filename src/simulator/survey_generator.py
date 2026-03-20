"""
Generador de encuestas de compradores.

Genera encuestas con correlaciones demográficas intencionales:
- Jóvenes (18-30) → más probable vehículo deportivo, mayor velocidad media
- Ingreso alto → más probable vehículo eléctrico
- Motivo "economía" → híbridos/eléctricos
- Motivo "rendimiento" → deportivos
- Más km recorridos → menor satisfacción (desgaste percibido)
- Uso "ciudad" → eléctricos/híbridos
"""

import numpy as np
import pandas as pd
from typing import Optional
import uuid


# Distribuciones demográficas base
AGE_RANGES = [(18, 25), (26, 35), (36, 45), (46, 55), (56, 70)]
AGE_WEIGHTS = [0.15, 0.30, 0.25, 0.18, 0.12]

GENDERS = ["masculino", "femenino", "otro"]
GENDER_WEIGHTS = [0.48, 0.48, 0.04]

INCOME_BRACKETS = ["bajo", "medio-bajo", "medio", "medio-alto", "alto"]
INCOME_WEIGHTS = [0.10, 0.20, 0.35, 0.25, 0.10]

PURCHASE_REASONS = ["economia", "rendimiento", "seguridad", "tecnologia", "estilo", "ecologia"]

EXPECTED_USAGE = ["ciudad", "carretera", "mixto"]

EDUCATION_LEVELS = ["secundaria", "universidad", "posgrado"]

REGIONS = ["norte", "centro", "sur", "este", "oeste"]


class SurveyGenerator:
    """Genera encuestas de compradores con correlaciones demográficas."""

    def __init__(self, seed: Optional[int] = 42):
        self.rng = np.random.default_rng(seed)

    def _select_vehicle_type_by_demographics(
        self, age: int, income: str, purchase_reason: str, expected_usage: str
    ) -> str:
        """
        Asigna tipo de vehículo con probabilidades condicionadas a demografía.

        Correlaciones embebidas:
        - Jóvenes → más deportivos
        - Ingreso alto → más eléctricos
        - Motivo economía → híbridos/eléctricos
        - Motivo rendimiento → deportivos
        - Uso ciudad → eléctricos/híbridos
        """
        # Probabilidades base
        probs = {"electrico": 0.25, "gasolina": 0.35, "hibrido": 0.25, "deportivo": 0.15}

        # Ajuste por edad
        if age <= 30:
            probs["deportivo"] += 0.15
            probs["gasolina"] += 0.05
            probs["electrico"] -= 0.10
            probs["hibrido"] -= 0.10
        elif age >= 50:
            probs["deportivo"] -= 0.10
            probs["hibrido"] += 0.10

        # Ajuste por ingreso
        if income in ["alto", "medio-alto"]:
            probs["electrico"] += 0.20
            probs["deportivo"] += 0.05
            probs["gasolina"] -= 0.15
            probs["hibrido"] -= 0.10
        elif income in ["bajo", "medio-bajo"]:
            probs["electrico"] -= 0.15
            probs["gasolina"] += 0.15

        # Ajuste por motivo de compra
        if purchase_reason == "economia":
            probs["hibrido"] += 0.15
            probs["electrico"] += 0.10
            probs["deportivo"] -= 0.20
            probs["gasolina"] -= 0.05
        elif purchase_reason == "rendimiento":
            probs["deportivo"] += 0.25
            probs["gasolina"] += 0.05
            probs["electrico"] -= 0.15
            probs["hibrido"] -= 0.15
        elif purchase_reason == "ecologia":
            probs["electrico"] += 0.30
            probs["hibrido"] += 0.10
            probs["deportivo"] -= 0.25
            probs["gasolina"] -= 0.15

        # Ajuste por uso esperado
        if expected_usage == "ciudad":
            probs["electrico"] += 0.10
            probs["hibrido"] += 0.05
            probs["deportivo"] -= 0.10
            probs["gasolina"] -= 0.05
        elif expected_usage == "carretera":
            probs["gasolina"] += 0.10
            probs["deportivo"] += 0.05
            probs["electrico"] -= 0.10
            probs["hibrido"] -= 0.05

        # Normalizar probabilidades (asegurar >= 0)
        for k in probs:
            probs[k] = max(probs[k], 0.02)  # mínimo 2%
        total = sum(probs.values())
        for k in probs:
            probs[k] /= total

        types = list(probs.keys())
        weights = list(probs.values())
        return self.rng.choice(types, p=weights)

    def _generate_driving_style(self, age: int, vehicle_type: str) -> str:
        """
        Asigna estilo de conducción correlacionado con edad y tipo de vehículo.

        Correlaciones:
        - Jóvenes → más agresivos
        - Deportivos → más agresivos
        - Mayores → más calmados
        """
        if age <= 30:
            weights = [0.15, 0.40, 0.45]  # calm, normal, aggressive
        elif age <= 45:
            weights = [0.25, 0.50, 0.25]
        else:
            weights = [0.45, 0.40, 0.15]

        if vehicle_type == "deportivo":
            weights = [w * f for w, f in zip(weights, [0.5, 0.8, 1.5])]

        total = sum(weights)
        weights = [w / total for w in weights]

        return self.rng.choice(["calm", "normal", "aggressive"], p=weights)

    def _generate_satisfaction(
        self,
        age: int,
        income: str,
        vehicle_type: str,
        km_driven: float,
        driving_style: str,
    ) -> int:
        """
        Genera puntuación de satisfacción (1-5) con correlaciones.

        Correlaciones embebidas:
        - Más km → menor satisfacción
        - Ingreso alto + eléctrico → mayor satisfacción
        - Conducción agresiva → menor satisfacción (más problemas)
        """
        base_satisfaction = 3.5

        # Efecto km recorridos (negativo)
        km_effect = -0.5 * (km_driven / 10000)  # -0.5 por cada 10k km

        # Efecto ingreso + tipo
        if income in ["alto", "medio-alto"] and vehicle_type == "electrico":
            income_effect = 0.8
        elif income in ["bajo", "medio-bajo"] and vehicle_type == "deportivo":
            income_effect = -0.5  # caro de mantener
        else:
            income_effect = 0

        # Efecto estilo de conducción
        style_effects = {"calm": 0.3, "normal": 0, "aggressive": -0.4}
        style_effect = style_effects[driving_style]

        # Ruido
        noise = self.rng.normal(0, 0.5)

        score = base_satisfaction + km_effect + income_effect + style_effect + noise
        return int(np.clip(round(score), 1, 5))

    def generate_surveys(
        self,
        n_surveys: int = 500,
        vehicle_ids: Optional[list] = None,
        start_date: str = "2025-01-01",
        end_date: str = "2025-12-31",
    ) -> pd.DataFrame:
        """
        Genera un DataFrame de encuestas de compradores.

        Parameters
        ----------
        n_surveys : int
            Número de encuestas a generar.
        vehicle_ids : list, optional
            Lista de vehicle_ids existentes para asociar.
            Si None, se generan IDs nuevos.
        start_date, end_date : str
            Rango de fechas para las compras.

        Returns
        -------
        pd.DataFrame
            Encuestas con correlaciones demográficas embebidas.
        """
        surveys = []

        start = pd.Timestamp(start_date)
        end = pd.Timestamp(end_date)
        date_range_days = (end - start).days

        for i in range(n_surveys):
            # Demografía base
            age_range_idx = self.rng.choice(len(AGE_RANGES), p=AGE_WEIGHTS)
            age = self.rng.integers(*AGE_RANGES[age_range_idx])

            gender = self.rng.choice(GENDERS, p=GENDER_WEIGHTS)

            # Ingreso correlacionado ligeramente con edad
            if age >= 40:
                income_weights = [0.05, 0.12, 0.30, 0.33, 0.20]
            elif age <= 28:
                income_weights = [0.18, 0.30, 0.35, 0.12, 0.05]
            else:
                income_weights = INCOME_WEIGHTS
            income = self.rng.choice(INCOME_BRACKETS, p=income_weights)

            # Motivo de compra (correlacionado con edad/ingreso)
            if age <= 30:
                reason_weights = [0.10, 0.30, 0.10, 0.20, 0.25, 0.05]
            elif income in ["alto", "medio-alto"]:
                reason_weights = [0.05, 0.15, 0.15, 0.25, 0.15, 0.25]
            else:
                reason_weights = [0.30, 0.10, 0.25, 0.10, 0.10, 0.15]
            purchase_reason = self.rng.choice(PURCHASE_REASONS, p=reason_weights)

            # Uso esperado
            if age <= 30:
                usage_weights = [0.50, 0.20, 0.30]
            elif age >= 50:
                usage_weights = [0.35, 0.35, 0.30]
            else:
                usage_weights = [0.35, 0.30, 0.35]
            expected_usage = self.rng.choice(EXPECTED_USAGE, p=usage_weights)

            # Tipo de vehículo (correlacionado con todo lo anterior)
            vehicle_type = self._select_vehicle_type_by_demographics(
                age, income, purchase_reason, expected_usage
            )

            # Vehicle ID
            if vehicle_ids and i < len(vehicle_ids):
                vid = vehicle_ids[i]
            else:
                vid = str(uuid.uuid4())

            # Estilo de conducción
            driving_style = self._generate_driving_style(age, vehicle_type)

            # Km simulados (jóvenes y agresivos → más km)
            base_km = self.rng.uniform(5000, 30000)
            if age <= 30:
                base_km *= 1.2
            if driving_style == "aggressive":
                base_km *= 1.15
            km_driven = round(base_km, 0)

            # Satisfacción
            satisfaction = self._generate_satisfaction(
                age, income, vehicle_type, km_driven, driving_style
            )

            # Educación
            if income in ["alto", "medio-alto"]:
                edu_weights = [0.05, 0.45, 0.50]
            else:
                edu_weights = [0.30, 0.50, 0.20]
            education = self.rng.choice(EDUCATION_LEVELS, p=edu_weights)

            # Región
            region = self.rng.choice(REGIONS)

            # Recomendaría (correlacionado con satisfacción)
            would_recommend = satisfaction >= 4 or (
                satisfaction == 3 and self.rng.random() > 0.5
            )

            # Fecha de compra
            purchase_date = start + pd.Timedelta(
                days=int(self.rng.integers(0, date_range_days))
            )

            surveys.append({
                "survey_id": str(uuid.uuid4()),
                "vehicle_id": vid,
                "purchase_date": purchase_date,
                "age": int(age),
                "gender": gender,
                "income_bracket": income,
                "education": education,
                "region": region,
                "purchase_reason": purchase_reason,
                "expected_usage": expected_usage,
                "vehicle_type_purchased": vehicle_type,
                "driving_style": driving_style,
                "km_driven": km_driven,
                "satisfaction_score": satisfaction,
                "would_recommend": would_recommend,
            })

        return pd.DataFrame(surveys)


if __name__ == "__main__":
    gen = SurveyGenerator(seed=42)
    surveys = gen.generate_surveys(n_surveys=500)
    print(f"Encuestas generadas: {len(surveys)}")
    print("\nDistribución de tipos de vehículo:")
    print(surveys["vehicle_type_purchased"].value_counts())
    print("\nSatisfacción media por tipo:")
    print(surveys.groupby("vehicle_type_purchased")["satisfaction_score"].mean())
    print("\nEdad media por tipo:")
    print(surveys.groupby("vehicle_type_purchased")["age"].mean())
