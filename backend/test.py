from datetime import datetime, timedelta
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore
from core.config import get_settings


class SchedulerService:
    def __init__(self, db_url: str):
        """Inicializa o APScheduler conectado ao PostgreSQL"""
        jobstores = {
            "default": SQLAlchemyJobStore(url=db_url)
        }

        self.scheduler = BackgroundScheduler(jobstores=jobstores)
        self.scheduler.start()
        print("APScheduler iniciado e conectado ao banco de dados.")

    def add_job(self, func, run_date: datetime, **kwargs):
        """
        Adiciona uma tarefa única para ser executada em um horário/data específicos.
        """
        job = self.scheduler.add_job(func, trigger="date", run_date=run_date, **kwargs)
        print(f"Job '{job.id}' agendado para {run_date}.")
        return job


# -------------------- Exemplo de uso --------------------
if __name__ == "__main__":
    def tarefa():
        print(f"Tarefa executada em: {datetime.now()}")

    db_url = get_settings().SYNC_DB_URL
    scheduler = SchedulerService(db_url=db_url)

    # agenda a execução para daqui a 1 minuto
    agendamento = datetime.now() + timedelta(minutes=2)
    scheduler.add_job(tarefa, run_date=agendamento)

    print(f"Tarefa agendada para {agendamento}. Aguardando execução...")

    # mantém o script ativo para que o scheduler funcione
    import time
    while True:
        time.sleep(10)