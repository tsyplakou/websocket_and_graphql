from typing import List, Optional

import strawberry
from fastapi import FastAPI
from strawberry.fastapi import GraphQLRouter

# Храним задачи в памяти (имитация базы данных)
tasks = []


# Определяем GraphQL модель для задачи
@strawberry.type
class Task:
    id: int
    title: str
    completed: bool


# Запросы GraphQL
@strawberry.type
class Query:
    @strawberry.field
    def get_tasks(self) -> List[Task]:
        """Возвращает список всех задач"""
        return tasks

    @strawberry.field
    def get_task(self, id: int) -> Optional[Task]:
        """Получает задачу по ID"""
        return next((task for task in tasks if task.id == id), None)


# Мутации GraphQL (изменение данных)
@strawberry.type
class Mutation:
    @strawberry.mutation
    def create_task(self, title: str) -> Task:
        """Создаёт новую задачу"""
        new_task = Task(id=len(tasks) + 1, title=title, completed=False)
        tasks.append(new_task)
        return new_task

    @strawberry.mutation
    def complete_task(self, id: int) -> Optional[Task]:
        """Отмечает задачу как выполненную"""
        task = next((task for task in tasks if task.id == id), None)
        if task:
            task.completed = True
        return task

    @strawberry.mutation
    def delete_task(self, id: int) -> Optional[Task]:
        """Отмечает задачу как выполненную"""
        task = next((task for task in tasks if task.id == id), None)
        tasks.remove(task)
        return True


# Создаём GraphQL API
schema = strawberry.Schema(query=Query, mutation=Mutation)
graphql_app = GraphQLRouter(schema)

# Запускаем FastAPI
app = FastAPI()
app.include_router(graphql_app, prefix="/graphql")

# Запуск сервера:
# uvicorn server:app --reload
