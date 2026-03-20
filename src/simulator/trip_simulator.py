"""
Simulador de viajes completo.

Orquesta la generación de datos para toda la flota:
- Genera viajes diarios para cada vehículo (1-4 viajes/día)
- Asigna estilos de conducción basados en encuestas
- Produce archivos CSV de telemetría y encuestas
- Controla el periodo de simulación (por defecto 30 días)

Correlaciones embebidas a nivel de flota:
- Vehículos con conductores jóvenes → más viajes, más agresivos
- Vehículos eléctricos → más viajes cortos en ciudad
- Horario: más viajes 7-9am y 5-8pm (commute)
"""

import numpy as np
import pandas as pd
from pathlib import Path
from typing import Optional
import os

from .vehicle_profiles import VehicleProfileGenerator
from .telemetry_generator import TelemetryGenerator
from .survey_generator import SurveyGenerator


# Ciudades base para simular ubicaciones de inicio
START_LOCATIONS = {
    "norte":  {"lat": 25.6866, "lon": -100.3161},  # Monterrey
    "centro": {"lat": 19.4326, "lon": -99.1332},   # CDMX
    "sur":    {"lat": 17.0732, "lon": -96.7266},   # Oaxaca
    "este":   {"lat": 19.1738, "lon": -96.1342},   # Veracruz
    "oeste":  {"lat": 20.6597, "lon": -103.3496},  # Guadalajara
}


class TripSimulator:
    """Simulador completo de flota vehicular."""

    def __init__(self, seed: Optional[int] = 42, output_dir: str = "data/raw"):
        self.seed = seed
        self.rng = np.random.default_rng(seed)
        self.output_dir = Path(output_dir)
        self.vpg = VehicleProfileGenerator(seed=seed)
        self.tg = TelemetryGenerator(seed=seed)
        self.sg = SurveyGenerator(seed=seed)

    def _get_daily_trip_count(self, driving_style: str, vehicle_type: str) -> int:
        """Número de viajes diarios basado en perfil."""
        base = 2
        if driving_style == "aggressive":
            base += 1
        if vehicle_type == "electrico":
            base += 1  # viajes más cortos, más frecuentes
        if self.rng.random() < 0.15:
            base = 0  # 15% chance: día sin uso
        return min(base, 4)

    def _get_trip_params(
        self,
        driving_style: str,
        vehicle_type: str,
        hour: int,
    ) -> dict:
        """Parámetros de un viaje individual."""
        # Duración base en segundos
        if hour in [7, 8, 17, 18]:  # commute
            duration = self.rng.integers(1200, 3600)  # 20-60 min
        else:
            duration = self.rng.integers(600, 2400)  # 10-40 min

        # Tipo de vía
        if vehicle_type == "electrico":
            road_weights = [0.50, 0.15, 0.35]  # ciudad más probable
        elif vehicle_type == "deportivo":
            road_weights = [0.25, 0.40, 0.35]  # carretera más probable
        else:
            road_weights = [0.35, 0.30, 0.35]

        road_type = self.rng.choice(["city", "highway", "mixed"], p=road_weights)

        return {
            "duration_seconds": duration,
            "driving_style": driving_style,
            "road_type": road_type,
        }

    def _get_trip_start_hour(self) -> int:
        """Hora de inicio del viaje (distribución bimodal: commute)."""
        # Picos en 7-9 y 17-19
        hours = list(range(6, 23))
        weights = [
            0.04, 0.12, 0.14, 0.08,  # 6-9
            0.04, 0.04, 0.06, 0.08,  # 10-13
            0.06, 0.04, 0.04,        # 14-16
            0.10, 0.12, 0.08,        # 17-19
            0.04, 0.02, 0.02,        # 20-22 (corregido: quitamos hora 23 para tener 17 valores)
        ]
        # Asegurar que tenemos el mismo número de pesos que horas
        weights = weights[:len(hours)]
        total = sum(weights)
        weights = [w / total for w in weights]
        return int(self.rng.choice(hours, p=weights))

    def simulate(
        self,
        n_vehicles: int = 50,
        n_days: int = 30,
        n_surveys: int = 500,
        start_date: str = "2025-01-01",
        save_csv: bool = True,
        verbose: bool = True,
    ) -> dict:
        """
        Ejecuta la simulación completa.

        Parameters
        ----------
        n_vehicles : int
            Número de vehículos en la flota.
        n_days : int
            Días de simulación.
        n_surveys : int
            Número de encuestas a generar.
        start_date : str
            Fecha de inicio de la simulación.
        save_csv : bool
            Si True, guarda CSVs en output_dir.
        verbose : bool
            Si True, imprime progreso.

        Returns
        -------
        dict
            {"fleet": DataFrame, "telemetry": DataFrame, "surveys": DataFrame}
        """
        # 1. Generar flota
        if verbose:
            print(f"Generando flota de {n_vehicles} vehículos...")
        fleet = self.vpg.generate_fleet(n_vehicles)

        # 2. Generar encuestas (asociadas a la flota)
        if verbose:
            print(f"Generando {n_surveys} encuestas...")
        vehicle_ids = fleet["vehicle_id"].tolist()
        surveys = self.sg.generate_surveys(
            n_surveys=n_surveys,
            vehicle_ids=vehicle_ids,
            start_date=start_date,
            end_date=str(
                pd.Timestamp(start_date) + pd.Timedelta(days=n_days)
            ),
        )

        # Crear mapa vehicle_id → driving_style desde encuestas
        style_map = {}
        for _, row in surveys.iterrows():
            if row["vehicle_id"] in fleet["vehicle_id"].values:
                style_map[row["vehicle_id"]] = row["driving_style"]

        # Para vehículos sin encuesta, asignar estilo aleatorio
        for vid in fleet["vehicle_id"]:
            if vid not in style_map:
                style_map[vid] = self.rng.choice(
                    ["calm", "normal", "aggressive"], p=[0.3, 0.5, 0.2]
                )

        # Crear mapa vehicle_id → región desde encuestas
        region_map = {}
        for _, row in surveys.iterrows():
            if row["vehicle_id"] in fleet["vehicle_id"].values:
                region_map[row["vehicle_id"]] = row["region"]

        # 3. Generar telemetría
        if verbose:
            print(f"Simulando {n_days} días de telemetría...")

        all_telemetry = []
        start_ts = pd.Timestamp(start_date)

        for day in range(n_days):
            current_date = start_ts + pd.Timedelta(days=day)
            if verbose and day % 7 == 0:
                print(f"  Día {day + 1}/{n_days} ({current_date.date()})...")

            for _, vehicle in fleet.iterrows():
                vid = vehicle["vehicle_id"]
                vtype = vehicle["vehicle_type"]
                style = style_map.get(vid, "normal")
                profile = vehicle.to_dict()

                # Número de viajes del día
                n_trips = self._get_daily_trip_count(style, vtype)

                for trip_idx in range(n_trips):
                    hour = self._get_trip_start_hour()
                    minute = self.rng.integers(0, 60)
                    trip_start = current_date + pd.Timedelta(
                        hours=int(hour), minutes=int(minute)
                    )

                    trip_params = self._get_trip_params(style, vtype, hour)

                    # Ubicación de inicio
                    region = region_map.get(vid, "centro")
                    loc = START_LOCATIONS.get(region, START_LOCATIONS["centro"])

                    trip_df = self.tg.generate_trip_telemetry(
                        vehicle_profile=profile,
                        start_time=trip_start,
                        start_lat=loc["lat"] + self.rng.normal(0, 0.02),
                        start_lon=loc["lon"] + self.rng.normal(0, 0.02),
                        **trip_params,
                    )

                    # Añadir metadatos
                    trip_df["trip_id"] = f"{vid[:8]}_{day:03d}_{trip_idx}"
                    trip_df["road_type"] = trip_params["road_type"]

                    all_telemetry.append(trip_df)

        telemetry = pd.concat(all_telemetry)
        if verbose:
            print(
                f"Telemetría total: {len(telemetry):,} registros "
                f"({len(all_telemetry)} viajes)"
            )

        # 4. Guardar CSVs
        if save_csv:
            self.output_dir.mkdir(parents=True, exist_ok=True)
            telemetry_dir = self.output_dir / "telemetry"
            surveys_dir = self.output_dir / "surveys"
            telemetry_dir.mkdir(exist_ok=True)
            surveys_dir.mkdir(exist_ok=True)

            fleet_path = self.output_dir / "fleet_profiles.csv"
            fleet.to_csv(fleet_path, index=False)

            surveys_path = surveys_dir / "buyer_surveys.csv"
            surveys.to_csv(surveys_path, index=False)

            # Guardar telemetría particionada por día (archivos más manejables)
            telemetry_reset = telemetry.reset_index()
            for date, group in telemetry_reset.groupby(
                telemetry_reset["timestamp"].dt.date
            ):
                day_path = telemetry_dir / f"telemetry_{date}.csv"
                group.to_csv(day_path, index=False)

            if verbose:
                print(f"\nArchivos guardados en {self.output_dir}/")
                print(f"  - fleet_profiles.csv ({len(fleet)} vehículos)")
                print(f"  - surveys/buyer_surveys.csv ({len(surveys)} encuestas)")
                print(
                    f"  - telemetry/telemetry_YYYY-MM-DD.csv "
                    f"({n_days} archivos diarios)"
                )

        return {
            "fleet": fleet,
            "telemetry": telemetry,
            "surveys": surveys,
        }


if __name__ == "__main__":
    sim = TripSimulator(seed=42)
    results = sim.simulate(
        n_vehicles=10, n_days=3, n_surveys=15, verbose=True
    )
