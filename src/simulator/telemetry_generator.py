"""
Generador de datos de telemetría vehicular.

Genera señales realistas de sensores para un vehículo durante un viaje:
- Velocidad con perfiles de aceleración/crucero/frenado
- Consumo correlacionado con velocidad y aceleración
- Batería SOC que decrece con el consumo
- RPM correlacionado con velocidad
- GPS con rutas simuladas
- Temperatura de batería correlacionada con uso

Correlaciones embebidas intencionalmente:
- Mayor velocidad → mayor consumo
- Aceleración brusca → picos de consumo
- Conducción agresiva → mayor variabilidad en velocidad
- Temperatura alta → degradación más rápida de batería
"""

import numpy as np
import pandas as pd
from typing import Optional


class TelemetryGenerator:
    """Genera telemetría de sensores para un viaje individual."""

    def __init__(self, seed: Optional[int] = None):
        self.rng = np.random.default_rng(seed)

    def generate_speed_profile(
        self,
        duration_seconds: int,
        driving_style: str = "normal",
        road_type: str = "city",
    ) -> np.ndarray:
        """
        Genera un perfil de velocidad realista para un viaje.

        Parameters
        ----------
        duration_seconds : int
            Duración del viaje en segundos.
        driving_style : str
            Estilo: "calm", "normal", "aggressive".
        road_type : str
            Tipo de vía: "city", "highway", "mixed".

        Returns
        -------
        np.ndarray
            Array de velocidades (km/h) a 1 Hz.
        """
        # Parámetros según estilo de conducción
        style_params = {
            "calm":       {"accel_factor": 0.6, "speed_noise": 2, "brake_intensity": 0.5},
            "normal":     {"accel_factor": 1.0, "speed_noise": 4, "brake_intensity": 1.0},
            "aggressive": {"accel_factor": 1.8, "speed_noise": 8, "brake_intensity": 1.8},
        }

        # Velocidades objetivo según tipo de vía
        road_params = {
            "city":    {"v_targets": [0, 30, 50, 40, 0, 50, 30, 0], "v_max": 60},
            "highway": {"v_targets": [0, 60, 100, 120, 110, 120, 80, 0], "v_max": 130},
            "mixed":   {"v_targets": [0, 40, 60, 100, 60, 40, 80, 0], "v_max": 110},
        }

        params = style_params.get(driving_style, style_params["normal"])
        road = road_params.get(road_type, road_params["city"])

        # Interpolar entre velocidades objetivo
        n_targets = len(road["v_targets"])
        target_indices = np.linspace(0, duration_seconds - 1, n_targets).astype(int)
        speed = np.zeros(duration_seconds)

        # Crear perfil base interpolando
        for i in range(n_targets - 1):
            start_idx = target_indices[i]
            end_idx = target_indices[i + 1]
            segment_len = end_idx - start_idx
            if segment_len > 0:
                speed[start_idx:end_idx] = np.linspace(
                    road["v_targets"][i],
                    road["v_targets"][i + 1],
                    segment_len,
                )
        speed[target_indices[-1]:] = road["v_targets"][-1]

        # Añadir variabilidad según estilo
        noise = self.rng.normal(0, params["speed_noise"], duration_seconds)
        # Suavizar el ruido para que sea más realista
        kernel_size = 10
        noise = np.convolve(noise, np.ones(kernel_size) / kernel_size, mode="same")
        speed += noise * params["accel_factor"]

        # Simular paradas en ciudad (semáforos)
        if road_type == "city":
            n_stops = self.rng.integers(3, 8)
            stop_positions = self.rng.choice(
                range(duration_seconds // 6, duration_seconds - duration_seconds // 6),
                size=min(n_stops, duration_seconds // 60),
                replace=False,
            )
            for pos in stop_positions:
                stop_duration = self.rng.integers(10, 40)
                end = min(pos + stop_duration, duration_seconds)
                # Frenado gradual
                brake_len = min(30, pos)
                if brake_len > 0:
                    speed[pos - brake_len:pos] = np.linspace(
                        speed[max(0, pos - brake_len)], 0, brake_len
                    )
                speed[pos:end] = 0
                # Aceleración gradual
                accel_len = min(20, duration_seconds - end)
                if accel_len > 0 and end + accel_len < duration_seconds:
                    speed[end:end + accel_len] = np.linspace(
                        0, speed[min(end + accel_len, duration_seconds - 1)], accel_len
                    )

        # Limitar velocidad
        speed = np.clip(speed, 0, road["v_max"])

        return speed

    def generate_trip_telemetry(
        self,
        vehicle_profile: dict,
        duration_seconds: int = 1800,
        driving_style: str = "normal",
        road_type: str = "city",
        start_time: Optional[pd.Timestamp] = None,
        start_lat: float = 19.4326,
        start_lon: float = -99.1332,
    ) -> pd.DataFrame:
        """
        Genera un DataFrame completo de telemetría para un viaje.

        Parameters
        ----------
        vehicle_profile : dict
            Perfil del vehículo (de VehicleProfileGenerator).
        duration_seconds : int
            Duración del viaje en segundos.
        driving_style : str
            Estilo de conducción.
        road_type : str
            Tipo de vía.
        start_time : pd.Timestamp, optional
            Inicio del viaje. Default: ahora.
        start_lat, start_lon : float
            Coordenadas de inicio.

        Returns
        -------
        pd.DataFrame
            Telemetría segundo a segundo.
        """
        if start_time is None:
            start_time = pd.Timestamp.now()

        # --- Velocidad ---
        speed = self.generate_speed_profile(duration_seconds, driving_style, road_type)

        # --- Aceleración (derivada de velocidad) ---
        acceleration = np.diff(speed, prepend=speed[0]) / 3.6  # m/s²

        # --- RPM (correlacionado con velocidad) ---
        # RPM ≈ velocidad * factor + idle + ruido
        rpm_factor = vehicle_profile["motor_power_kw"] * 8
        rpm = speed * rpm_factor / vehicle_profile["max_speed_kmh"] + 800
        rpm += self.rng.normal(0, 50, duration_seconds)
        rpm = np.clip(rpm, 700, 7000)

        # --- Consumo (correlación fuerte con velocidad y aceleración) ---
        is_electric = vehicle_profile["fuel_type"] == "electrico"
        base_consumption = (
            vehicle_profile["base_consumption_city"]
            if road_type == "city"
            else vehicle_profile["base_consumption_highway"]
        )

        # Consumo instantáneo: base + efecto velocidad + efecto aceleración
        speed_factor = (speed / 100) ** 2  # consumo crece cuadráticamente
        accel_factor = np.maximum(acceleration, 0) * 2  # aceleración aumenta consumo
        consumption = base_consumption * (0.5 + speed_factor + accel_factor)
        consumption += self.rng.normal(0, base_consumption * 0.05, duration_seconds)
        consumption = np.maximum(consumption, 0)
        # Consumo 0 cuando el vehículo está parado
        consumption[speed < 1] = 0.1 if not is_electric else 0.05  # consumo residual

        # --- Batería SOC (para eléctricos e híbridos) ---
        if vehicle_profile.get("battery_capacity_kwh"):
            battery_capacity = vehicle_profile["battery_capacity_kwh"]
            # Consumo acumulado en kWh
            if is_electric:
                energy_used_kwh = np.cumsum(consumption / 3600)  # kWh/s acumulado
            else:
                # Híbridos: batería contribuye ~30% en ciudad
                city_factor = 0.3 if road_type == "city" else 0.1
                energy_used_kwh = np.cumsum(
                    consumption * city_factor / 3600
                )
            soc = 100 - (energy_used_kwh / battery_capacity * 100)
            soc = np.clip(soc, 0, 100)
        else:
            soc = np.full(duration_seconds, np.nan)

        # --- Nivel de combustible (para gasolina/híbrido/deportivo) ---
        if vehicle_profile.get("tank_capacity_l"):
            tank = vehicle_profile["tank_capacity_l"]
            fuel_used = np.cumsum(consumption / 3600)  # L/s acumulado
            fuel_level = 100 - (fuel_used / tank * 100)
            fuel_level = np.clip(fuel_level, 0, 100)
        else:
            fuel_level = np.full(duration_seconds, np.nan)

        # --- Voltaje de batería ---
        if vehicle_profile.get("battery_capacity_kwh"):
            nominal_voltage = 400 if is_electric else 48
            battery_voltage = nominal_voltage * (0.8 + 0.2 * soc / 100)
            battery_voltage += self.rng.normal(0, 1, duration_seconds)
        else:
            battery_voltage = 12.6 + self.rng.normal(0, 0.2, duration_seconds)

        # --- Corriente de batería ---
        battery_current = consumption * 10 + self.rng.normal(0, 2, duration_seconds)
        battery_current = np.maximum(battery_current, 0)

        # --- Temperatura batería (sube con uso intenso) ---
        base_temp = 25 + self.rng.normal(0, 2)
        temp_increase = np.cumsum(np.abs(acceleration) * 0.001 + speed * 0.0001)
        battery_temp = base_temp + temp_increase
        battery_temp += self.rng.normal(0, 0.5, duration_seconds)
        battery_temp = np.clip(battery_temp, 15, 55)

        # --- GPS (ruta simulada) ---
        # Movimiento simplificado: heading aleatorio suavizado
        heading = np.cumsum(self.rng.normal(0, 2, duration_seconds))
        heading = heading % 360
        # Desplazamiento basado en velocidad
        dx = speed / 3600 * np.cos(np.radians(heading)) / 111  # grados lat
        dy = speed / 3600 * np.sin(np.radians(heading)) / (
            111 * np.cos(np.radians(start_lat))
        )  # grados lon
        lat = start_lat + np.cumsum(dx)
        lon = start_lon + np.cumsum(dy)

        # --- Motor power ---
        motor_power = (
            vehicle_profile["motor_power_kw"]
            * (speed / vehicle_profile["max_speed_kmh"])
            * (1 + np.maximum(acceleration, 0))
        )
        motor_power += self.rng.normal(0, 2, duration_seconds)
        motor_power = np.clip(motor_power, 0, vehicle_profile["motor_power_kw"] * 1.1)

        # --- Timestamps ---
        timestamps = pd.date_range(start=start_time, periods=duration_seconds, freq="s")

        # --- Construir DataFrame ---
        df = pd.DataFrame({
            "timestamp": timestamps,
            "vehicle_id": vehicle_profile["vehicle_id"],
            "speed_kmh": np.round(speed, 2),
            "acceleration_ms2": np.round(acceleration, 3),
            "motor_rpm": np.round(rpm, 0),
            "motor_power_kw": np.round(motor_power, 2),
            "fuel_consumption_rate": np.round(consumption, 4),
            "fuel_level_pct": np.round(fuel_level, 2),
            "battery_voltage": np.round(battery_voltage, 2),
            "battery_current_a": np.round(battery_current, 2),
            "battery_soc_pct": np.round(soc, 2),
            "battery_temp_c": np.round(battery_temp, 1),
            "gps_lat": np.round(lat, 6),
            "gps_lon": np.round(lon, 6),
            "gps_heading": np.round(heading % 360, 1),
            "gps_altitude_m": np.round(
                2240 + np.cumsum(self.rng.normal(0, 0.1, duration_seconds)), 1
            ),
        })

        df = df.set_index("timestamp")
        return df


if __name__ == "__main__":
    from vehicle_profiles import VehicleProfileGenerator

    vpg = VehicleProfileGenerator(seed=42)
    fleet = vpg.generate_fleet(5)
    profile = fleet.iloc[0].to_dict()

    tg = TelemetryGenerator(seed=42)
    trip = tg.generate_trip_telemetry(
        profile, duration_seconds=600, driving_style="aggressive", road_type="city"
    )
    print(f"Telemetría generada: {trip.shape}")
    print(trip.head())
    print(trip.describe())
