"""
BigQuery Helper para NYC Taxi Analysis.

Proporciona:
- Conexión a BigQuery con autenticación por defecto
- Cache de queries en parquet (evita re-ejecutar consultas costosas)
- Estimación de costos antes de ejecutar
- Funciones de muestreo seguro
"""

import hashlib
import json
import time
from pathlib import Path

import pandas as pd

# Default dataset
DATASET = "bigquery-public-data.new_york_taxi_trips.tlc_yellow_trips_2015"

# Precio por TB procesado (on-demand pricing)
COST_PER_TB = 6.25  # USD

# Directorio de cache relativo al proyecto
_PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
CACHE_DIR = _PROJECT_ROOT / "data" / "nyc_taxi" / "cache"


class BigQueryHelper:
    """Helper para queries BigQuery con cache local en parquet."""

    def __init__(self, project_id: str | None = None, cache_dir: Path | str | None = None):
        """
        Inicializa el helper de BigQuery.

        Parameters
        ----------
        project_id : str, optional
            ID del proyecto GCP. Si es None, usa el proyecto por defecto de gcloud.
        cache_dir : Path or str, optional
            Directorio para cache de resultados. Por defecto: data/nyc_taxi/cache/
        """
        from google.cloud import bigquery

        self.client = bigquery.Client(project=project_id)
        self.cache_dir = Path(cache_dir) if cache_dir else CACHE_DIR
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.project_id = self.client.project

        print(f"✓ Conectado a BigQuery - Proyecto: {self.project_id}")
        print(f"✓ Cache en: {self.cache_dir}")

    def _query_hash(self, query: str) -> str:
        """Genera un hash único para una query SQL."""
        normalized = " ".join(query.strip().split())
        return hashlib.md5(normalized.encode()).hexdigest()[:12]

    def _cache_path(self, query: str, label: str | None = None) -> Path:
        """Genera la ruta del archivo de cache."""
        hash_str = self._query_hash(query)
        name = f"{label}_{hash_str}" if label else hash_str
        return self.cache_dir / f"{name}.parquet"

    def estimate_cost(self, query: str) -> dict:
        """
        Estima el costo de una query sin ejecutarla.

        Parameters
        ----------
        query : str
            Query SQL a estimar.

        Returns
        -------
        dict
            Diccionario con bytes_processed, gb, tb, estimated_cost_usd.
        """
        from google.cloud import bigquery

        job_config = bigquery.QueryJobConfig(dry_run=True, use_query_cache=False)
        job = self.client.query(query, job_config=job_config)

        bytes_processed = job.total_bytes_processed
        gb = bytes_processed / (1024**3)
        tb = bytes_processed / (1024**4)
        cost = tb * COST_PER_TB

        result = {
            "bytes_processed": bytes_processed,
            "gb": round(gb, 3),
            "tb": round(tb, 6),
            "estimated_cost_usd": round(cost, 4),
        }

        print(f"📊 Estimación: {result['gb']:.3f} GB → ${result['estimated_cost_usd']:.4f} USD")
        return result

    def run_query(
        self,
        query: str,
        label: str | None = None,
        use_cache: bool = True,
        max_cost_usd: float = 1.0,
        show_estimate: bool = True,
    ) -> pd.DataFrame:
        """
        Ejecuta una query con cache y control de costos.

        Parameters
        ----------
        query : str
            Query SQL a ejecutar.
        label : str, optional
            Etiqueta para el archivo de cache (más legible que el hash).
        use_cache : bool, default True
            Si True, busca en cache antes de ejecutar.
        max_cost_usd : float, default 1.0
            Costo máximo permitido en USD. Lanza error si se excede.
        show_estimate : bool, default True
            Si True, muestra la estimación de costos.

        Returns
        -------
        pd.DataFrame
            Resultado de la query como DataFrame.
        """
        cache_file = self._cache_path(query, label)

        # Intentar leer de cache
        if use_cache and cache_file.exists():
            df = pd.read_parquet(cache_file)
            # Convertir columnas object que contienen Decimal a float
            import decimal

            for col in df.columns:
                if df[col].dtype == object and len(df) > 0:
                    sample = df[col].dropna().iloc[0] if not df[col].dropna().empty else None
                    if isinstance(sample, decimal.Decimal):
                        df[col] = df[col].astype(float)
            print(f"📁 Cache hit: {cache_file.name} ({len(df):,} filas)")
            return df

        # Estimar costo
        if show_estimate:
            estimate = self.estimate_cost(query)
            if estimate["estimated_cost_usd"] > max_cost_usd:
                raise ValueError(
                    f"Query excede el límite de costo: "
                    f"${estimate['estimated_cost_usd']:.4f} > ${max_cost_usd:.2f}. "
                    f"Usa max_cost_usd={estimate['estimated_cost_usd'] + 0.5:.1f} para permitirla."
                )

        # Ejecutar query
        print(f"⏳ Ejecutando query...")
        start = time.time()
        df = self.client.query(query).to_dataframe()
        elapsed = time.time() - start

        # Convertir columnas decimal.Decimal a float (BigQuery NUMERIC llega como Decimal)
        import decimal

        for col in df.columns:
            if df[col].dtype == object and len(df) > 0:
                sample = df[col].dropna().iloc[0] if not df[col].dropna().empty else None
                if isinstance(sample, decimal.Decimal):
                    df[col] = df[col].astype(float)

        print(f"✓ Completado: {len(df):,} filas en {elapsed:.1f}s")

        # Guardar en cache
        if use_cache:
            df.to_parquet(cache_file, index=False)
            size_mb = cache_file.stat().st_size / (1024**2)
            print(f"💾 Cache guardado: {cache_file.name} ({size_mb:.1f} MB)")

        return df

    # Aliases para compatibilidad con notebooks
    query_to_df = run_query
    query = run_query

    def get_table_info(self, table_id: str = DATASET) -> dict:
        """
        Obtiene información sobre una tabla de BigQuery.

        Parameters
        ----------
        table_id : str
            ID completo de la tabla (proyecto.dataset.tabla).

        Returns
        -------
        dict
            Información de la tabla: filas, tamaño, esquema.
        """
        table = self.client.get_table(table_id)

        info = {
            "table_id": str(table.reference),
            "num_rows": table.num_rows,
            "size_gb": round(table.num_bytes / (1024**3), 2),
            "created": table.created,
            "modified": table.modified,
            "schema": [
                {"name": f.name, "type": f.field_type, "mode": f.mode, "description": f.description}
                for f in table.schema
            ],
        }

        print(f"📋 Tabla: {info['table_id']}")
        print(f"   Filas: {info['num_rows']:,}")
        print(f"   Tamaño: {info['size_gb']:.2f} GB")
        print(f"   Columnas: {len(info['schema'])}")

        return info

    def sample_query(
        self,
        columns: str = "*",
        table: str = DATASET,
        n: int = 10_000,
        where: str | None = None,
        seed: int = 42,
    ) -> str:
        """
        Genera una query con muestreo aleatorio reproducible.

        Parameters
        ----------
        columns : str
            Columnas a seleccionar.
        table : str
            Tabla de BigQuery.
        n : int
            Número de filas a muestrear.
        where : str, optional
            Condición WHERE adicional.
        seed : int
            Semilla para reproducibilidad (usada con FARM_FINGERPRINT).

        Returns
        -------
        str
            Query SQL con muestreo.
        """
        where_clause = f"WHERE {where}" if where else ""
        query = f"""
        SELECT {columns}
        FROM `{table}`
        {where_clause}
        WHERE MOD(ABS(FARM_FINGERPRINT(CAST(vendor_id AS STRING) || CAST(pickup_datetime AS STRING))), 100000) < {n * 100000 // 150_000_000}
        LIMIT {n}
        """
        # Simplificación: usar ORDER BY + LIMIT con hash para reproducibilidad
        if where:
            query = f"""
            SELECT {columns}
            FROM `{table}`
            WHERE {where}
            ORDER BY FARM_FINGERPRINT(CAST(pickup_datetime AS STRING) || CAST(dropoff_datetime AS STRING))
            LIMIT {n}
            """
        else:
            query = f"""
            SELECT {columns}
            FROM `{table}`
            ORDER BY FARM_FINGERPRINT(CAST(pickup_datetime AS STRING) || CAST(dropoff_datetime AS STRING))
            LIMIT {n}
            """
        return query

    def list_cache(self) -> pd.DataFrame:
        """Lista todos los archivos en cache con su tamaño."""
        files = list(self.cache_dir.glob("*.parquet"))
        if not files:
            print("📁 Cache vacío")
            return pd.DataFrame(columns=["file", "size_mb", "rows", "modified"])

        records = []
        for f in sorted(files):
            try:
                df_temp = pd.read_parquet(f)
                rows = len(df_temp)
            except Exception:
                rows = -1
            records.append(
                {
                    "file": f.name,
                    "size_mb": round(f.stat().st_size / (1024**2), 2),
                    "rows": rows,
                    "modified": pd.Timestamp.fromtimestamp(f.stat().st_mtime),
                }
            )

        df = pd.DataFrame(records)
        total_mb = df["size_mb"].sum()
        print(f"📁 Cache: {len(df)} archivos, {total_mb:.1f} MB total")
        return df

    def clear_cache(self, confirm: bool = False) -> None:
        """Elimina todos los archivos de cache."""
        files = list(self.cache_dir.glob("*.parquet"))
        if not files:
            print("📁 Cache ya está vacío")
            return

        if not confirm:
            total_mb = sum(f.stat().st_size for f in files) / (1024**2)
            print(f"⚠️  Se eliminarán {len(files)} archivos ({total_mb:.1f} MB)")
            print("   Usa clear_cache(confirm=True) para confirmar")
            return

        for f in files:
            f.unlink()
        print(f"🗑️  Eliminados {len(files)} archivos de cache")
