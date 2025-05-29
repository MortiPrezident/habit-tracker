from fastapi import APIRouter, HTTPException, status, Depends, Body
from web.database import get_async_session
from sqlalchemy.ext.asyncio import AsyncSession
from web.models import User, Habit
from web.dependencies import get_current_user
from web.schemas import (
    HabitCreate,
    HabitsOut,
    HabitEdit,
    HabitOut,
    HabitsSynchronizationOut,
)
from sqlalchemy.future import select
from sqlalchemy import update, delete, and_, join

router = APIRouter(prefix="/habit", tags=["habit"])


@router.post("/created")
async def created_habit(
    habit_new: HabitCreate,
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_async_session),
) -> HabitOut:
    try:
        habit = Habit(
            name=habit_new.name,
            description=habit_new.description,
            alert_time=habit_new.alert_time,
            user_id=user.id,
        )
        session.add(habit)

        await session.commit()

        return HabitOut(
            id=habit.id,
            name=habit.name,
            description=habit.description,
            alert_time=habit.alert_time,
            count=habit.count,
            user_id=habit.user_id,
            completed=habit.completed,
        )

    except Exception:
        await session.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed created habit",
        )


@router.get("/habits")
async def get_habits(
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_async_session),
) -> HabitsOut:
    try:
        res = await session.execute(select(Habit).where(Habit.user_id == user.id))
        habits = res.scalars().all()

        return HabitsOut(habits=habits)

    except Exception as e:
        await session.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed get habit {e}",
        )


@router.get("/habits_all", response_model=HabitsSynchronizationOut)
async def get_habits_all(session: AsyncSession = Depends(get_async_session)):
    try:
        query = (
            select(
                Habit.id.label("habit_id"),
                User.chat_id.label("chat_id"),
                Habit.name.label("habit_name"),
                Habit.alert_time.label("time_str"),
            )
            .select_from(join(Habit, User, Habit.user_id == User.id))
            .where(and_(Habit.completed.is_(False), Habit.count < 21))
        )

        result = await session.execute(query)
        rows = result.all()

        habits_out = [
            {
                "habit_id": row.habit_id,
                "chat_id": row.chat_id,
                "habit_name": row.habit_name,
                "time_str": row.time_str,
            }
            for row in rows
        ]

        return HabitsSynchronizationOut(habits=habits_out)

    except Exception as e:
        await session.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed get habits_all: {e}",
        )


@router.post("/decrease_uncompleted")
async def decrease_uncompleted_habits(
    session: AsyncSession = Depends(get_async_session),
):
    try:
        await session.execute(
            update(Habit)
            .where(and_(Habit.completed.is_(False), Habit.count > 0, Habit.count != 21))
            .values(count=Habit.count - 1)
        )
        await session.execute(
            update(Habit)
            .where(and_(Habit.completed.is_(True), Habit.count != 21))
            .values(completed=False)
        )

        await session.commit()
        return

    except Exception as e:
        await session.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed decrease_uncompleted {e}",
        )


@router.post("/edit")
async def edit_habit(
    habit_in: HabitEdit, session: AsyncSession = Depends(get_async_session)
) -> HabitOut:
    query = (
        update(Habit)
        .where(Habit.id == habit_in.id)
        .values(
            **{
                k: v
                for k, v in habit_in.model_dump().items()
                if k != "id" and v is not None
            }
        )
    )

    res = await session.execute(query)

    await session.commit()

    if res.rowcount == 0:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed edit habit",
        )

    res = await session.execute(select(Habit).where(Habit.id == habit_in.id))
    habit = res.scalars().first()

    return HabitOut(
        id=habit.id,
        name=habit.name,
        description=habit.description,
        count=habit.count,
        alert_time=habit.alert_time,
        user_id=habit.user_id,
        completed=habit.completed,
    )


@router.post("/completed")
async def completed_habit_by_id(
    data: dict = Body(...), session: AsyncSession = Depends(get_async_session)
) -> HabitOut:
    id = data["id"]
    result = await session.execute(select(Habit).where(Habit.id == id))
    habit = result.scalars().first()

    habit.completed = True
    habit.count += 1
    await session.commit()

    return HabitOut(
        id=habit.id,
        name=habit.name,
        description=habit.description,
        count=habit.count,
        alert_time=habit.alert_time,
        user_id=habit.user_id,
        completed=habit.completed,
    )


@router.post("/delete")
async def delete_habit_by_id(
    data: dict = Body(...), session: AsyncSession = Depends(get_async_session)
):
    try:
        habit_id = int(data["habit_id"])
        query = delete(Habit).where(Habit.id == habit_id)

        res = await session.execute(query)

        await session.commit()

        if res.rowcount == 0:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Habit with id {habit_id} not found",
            )

        return
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed delete habit {e}",
        )


@router.get("/check")
async def check_completed(
    data: dict = Body(...), session: AsyncSession = Depends(get_async_session)
):
    habit_id = data["id"]
    result = await session.execute(select(Habit).where(Habit.id == habit_id))
    habit = result.scalars().first()

    await session.commit()

    return {"completed": habit.completed, "count": habit.count}
