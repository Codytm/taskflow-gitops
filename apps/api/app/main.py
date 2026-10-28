from collections.abc import Generator
from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI, HTTPException, Response
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import create_engine, select, text
from sqlalchemy.orm import Session, sessionmaker

from app.config import Settings
from app.models import Base, Task
from app.schemas import TaskCreate, TaskRead, TaskUpdate


def make_engine(database_url: str):
    connect_args = {"check_same_thread": False} if database_url.startswith("sqlite") else {}
    return create_engine(database_url, connect_args=connect_args)


def create_app(database_url: str | None = None) -> FastAPI:
    settings = Settings()
    url = database_url or settings.database_url
    engine = make_engine(url)
    session_factory = sessionmaker(bind=engine, autoflush=False, autocommit=False)

    @asynccontextmanager
    async def lifespan(app: FastAPI):
        Base.metadata.create_all(bind=engine)
        yield
        engine.dispose()

    app = FastAPI(title="TaskFlow", lifespan=lifespan)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origin_list,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    def get_db() -> Generator[Session]:
        db = session_factory()
        try:
            yield db
        finally:
            db.close()

    @app.get("/healthz")
    def healthz() -> dict[str, str]:
        return {"status": "ok"}

    @app.get("/readyz")
    def readyz(db: Session = Depends(get_db)) -> dict[str, str]:
        try:
            db.execute(text("SELECT 1"))
        except Exception as exc:
            raise HTTPException(status_code=503, detail="database unavailable") from exc
        return {"status": "ready"}

    @app.get("/tasks", response_model=list[TaskRead])
    def list_tasks(db: Session = Depends(get_db)) -> list[Task]:
        return list(db.scalars(select(Task).order_by(Task.created_at.desc(), Task.id.desc())))

    @app.post("/tasks", response_model=TaskRead, status_code=201)
    def create_task(payload: TaskCreate, db: Session = Depends(get_db)) -> Task:
        task = Task(title=payload.title, notes=payload.notes)
        db.add(task)
        db.commit()
        db.refresh(task)
        return task

    @app.patch("/tasks/{task_id}", response_model=TaskRead)
    def update_task(task_id: int, payload: TaskUpdate, db: Session = Depends(get_db)) -> Task:
        task = db.get(Task, task_id)
        if task is None:
            raise HTTPException(status_code=404, detail="task not found")
        for key, value in payload.model_dump(exclude_unset=True).items():
            setattr(task, key, value)
        db.commit()
        db.refresh(task)
        return task

    @app.delete("/tasks/{task_id}", status_code=204)
    def delete_task(task_id: int, db: Session = Depends(get_db)) -> Response:
        task = db.get(Task, task_id)
        if task is None:
            raise HTTPException(status_code=404, detail="task not found")
        db.delete(task)
        db.commit()
        return Response(status_code=204)

    return app


app = create_app()
