"""
Generador de perfiles de vehículos.

Crea una flota de vehículos con características realistas:
- Tipos: eléctrico, gasolina, híbrido, deportivo
- Cada tipo tiene parámetros base distintos (consumo, potencia, capacidad)
- Los perfiles se usan como semilla para la simulación de telemetría
"""

import numpy as np
import pandas as pd
from typing import Optional
import uuid


# Definición de tipos de vehículo con sus parámetros base
VEHICLE_TYPES = {
    "electrico": {
        "fuel_type": "electrico",
        "battery_capacity_kwh": (40, 100),     # rango min-max
        "motor_power_kw": (100, 300),
        "max_speed_kmh": (140, 200),
        "base_consumption_city": (12, 18),     # kWh/100km
        "base_consumption_highway": (16, 24),
        "weight_kg": (1500, 2200),
        "co2_emissions": 0,
    },
    "gasolina": {
        "fuel_type": "gasolina",
        "tank_capacity_l": (40, 70),
        "motor_power_kw": (60, 150),
        "max_speed_kmh": (160, 220),
        "base_consumption_city": (6, 10),      # L/100km
        "base_consumption_highway": (5, 8),
        "weight_kg": (1100, 1800),
        "co2_emissions": (120, 200),           # g/km
    },
    "hibrido": {
        "fuel_type": "hibrido",
        "battery_capacity_kwh": (8, 20),
        "tank_capacity_l": (35, 55),
        "motor_power_kw": (80, 200),
        "max_speed_kmh": (150, 210),
        "base_consumption_city": (3, 6),       # L/100km (menor en ciudad)
        "base_consumption_highway": (5, 7),
        "weight_kg": (1400, 2000),
        "co2_emissions": (60, 110),
    },
    "deportivo": {
        "fuel_type": "gasolina",
        "tank_capacity_l": (50, 80),
        "motor_power_kw": (200, 450),
        "max_speed_kmh": (220, 320),
        "base_consumption_city": (10, 16),     # L/100km
        "base_consumption_highway": (8, 12),
        "weight_kg": (1300, 1700),
        "co2_emissions": (180, 300),
    },
}

# Proporción por defecto de cada tipo en la flota
DEFAULT_TYPE_DISTRIBUTION = {
    "electrico": 0.25,
    "gasolina": 0.35,
    "hibrido": 0.25,
    "deportivo": 0.15,
}


class VehicleProfileGenerator:
    """Genera perfiles de vehículos para la flota simulada."""

    def __init__(self, seed: Optional[int] = 42):
        self.rng = np.random.default_rng(seed)

    def _sample_range(self, range_tuple: tuple) -> float:
        """Muestrea un valor uniforme dentro de un rango (min, max)."""
        low, high = range_tuple
        return self.rng.uniform(low, high)

    def generate_single_profile(self, vehicle_type: str) -> dict:
        """Genera un perfil individual de vehículo."""
        if vehicle_type not in VEHICLE_TYPES:
            raise ValueError(
                f"Tipo desconocido: {vehicle_type}. "
                f"Opciones: {list(VEHICLE_TYPES.keys())}"
            )

        specs = VEHICLE_TYPES[vehicle_type]
        profile = {
            "vehicle_id": str(uuid.uuid4()),
            "vehicle_type": vehicle_type,
            "fuel_type": specs["fuel_type"],
            "motor_power_kw": round(self._sample_range(specs["motor_power_kw"]), 1),
            "max_speed_kmh": round(self._sample_range(specs["max_speed_kmh"]), 0),
            "base_consumption_city": round(
                self._sample_range(specs["base_consumption_city"]), 2
            ),
            "base_consumption_highway": round(
                self._sample_range(specs["base_consumption_highway"]), 2
            ),
            "weight_kg": round(self._sample_range(specs["weight_kg"]), 0),
        }

        # Campos específicos por tipo
        if "battery_capacity_kwh" in specs:
            profile["battery_capacity_kwh"] = round(
                self._sample_range(specs["battery_capacity_kwh"]), 1
            )
        else:
            profile["battery_capacity_kwh"] = None

        if "tank_capacity_l" in specs:
            profile["tank_capacity_l"] = round(
                self._sample_range(specs["tank_capacity_l"]), 1
            )
        else:
            profile["tank_capacity_l"] = None

        if isinstance(specs["co2_emissions"], tuple):
            profile["co2_emissions_gkm"] = round(
                self._sample_range(specs["co2_emissions"]), 1
            )
        else:
            profile["co2_emissions_gkm"] = specs["co2_emissions"]

        # Año del modelo (más recientes para eléctricos)
        if vehicle_type == "electrico":
            profile["model_year"] = int(self.rng.choice(range(2020, 2026)))
        elif vehicle_type == "deportivo":
            profile["model_year"] = int(self.rng.choice(range(2018, 2026)))
        else:
            profile["model_year"] = int(self.rng.choice(range(2016, 2026)))

        return profile

    def generate_fleet(
        self,
        n_vehicles: int = 50,
        type_distribution: Optional[dict] = None,
    ) -> pd.DataFrame:
        """
        Genera una flota completa de vehículos.

        Parameters
        ----------
        n_vehicles : int
            Número total de vehículos a generar.
        type_distribution : dict, optional
            Proporción de cada tipo. Si None, usa DEFAULT_TYPE_DISTRIBUTION.

        Returns
        -------
        pd.DataFrame
            DataFrame con un perfil por fila.
        """
        if type_distribution is None:
            type_distribution = DEFAULT_TYPE_DISTRIBUTION

        # Calcular cuántos de cada tipo
        counts = {}
        remaining = n_vehicles
        types = list(type_distribution.keys())

        for i, vtype in enumerate(types):
            if i == len(types) - 1:
                counts[vtype] = remaining
            else:
                n = round(n_vehicles * type_distribution[vtype])
                counts[vtype] = n
                remaining -= n

        # Generar perfiles
        profiles = []
        for vtype, count in counts.items():
            for _ in range(count):
                profiles.append(self.generate_single_profile(vtype))

        df = pd.DataFrame(profiles)

        # Reordenar columnas
        col_order = [
            "vehicle_id", "vehicle_type", "fuel_type", "model_year",
            "motor_power_kw", "max_speed_kmh", "weight_kg",
            "battery_capacity_kwh", "tank_capacity_l",
            "base_consumption_city", "base_consumption_highway",
            "co2_emissions_gkm",
        ]
        df = df[col_order]

        return df


if __name__ == "__main__":
    gen = VehicleProfileGenerator(seed=42)
    fleet = gen.generate_fleet(n_vehicles=50)
    print(f"Flota generada: {len(fleet)} vehículos")
    print(fleet.groupby("vehicle_type").size())
    print(fleet.head(10))
