"""
DAG de Airflow: Health Check cada minuto.

Consulta PostgreSQL para ver cuantos mensajes se han procesado
y verifica que el sistema esta funcionando correctamente.
"""
from datetime import datetime, timedelta
from airflow.decorators import dag, task


@dag(
    dag_id="health_check",
    schedule="* * * * *",  # cada minuto
    start_date=datetime(2025, 1, 1),
    catchup=False,
    tags=["demo", "monitoreo"],
    default_args={
        "retries": 1,
        "retry_delay": timedelta(seconds=10),
    },
)
def health_check_dag():

    @task()
    def check_message_counts() -> dict:
        """Consultar PostgreSQL: cuantos mensajes se han procesado."""
        import psycopg2

        conn = psycopg2.connect(
            host="postgres",
            database="demo",
            user="demo",
            password="demo"
        )

        with conn.cursor() as cur:
            cur.execute(
                "SELECT sensor, count, last_updated "
                "FROM message_counts ORDER BY sensor"
            )
            rows = cur.fetchall()

        conn.close()

        result = {}
        total = 0
        for sensor, count, updated in rows:
            result[sensor] = {"count": count, "last_updated": str(updated)}
            total += count

        result["total"] = total
        print(f"=== HEALTH CHECK ===")
        print(f"Total mensajes procesados: {total}")
        for sensor, data in result.items():
            if sensor != "total":
                print(f"  {sensor}: {data['count']} (ultimo: {data['last_updated']})")

        return result

    @task()
    def evaluate_health(counts: dict) -> str:
        """Evaluar si el sistema esta sano."""
        total = counts.get("total", 0)

        if total == 0:
            status = "WARNING: No hay mensajes procesados aun"
        else:
            status = f"OK: {total} mensajes procesados"

        print(f"Estado: {status}")
        return status

    counts = check_message_counts()
    evaluate_health(counts)


health_check_dag()
