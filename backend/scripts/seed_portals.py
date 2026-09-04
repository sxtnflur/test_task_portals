"""Seed the `portals` table with demo data.

Assumes the schema already exists (run `alembic upgrade head` first) - this
script only inserts rows, it never creates tables itself, so it can't drift
from what the migrations define.

Usage (from anywhere - it locates backend/src itself):

    python backend/scripts/seed_portals.py
    python backend/scripts/seed_portals.py --reset
    python backend/scripts/seed_portals.py --extra 20
    python backend/scripts/seed_portals.py --reset --extra 20 --database-url postgresql+asyncpg://...

DATABASE_URL / --database-url follow the same resolution as the app itself
(backend/src/config/settings.py): an explicit --database-url wins, otherwise
the DATABASE_URL env var, otherwise backend/.env.
"""

import argparse
import asyncio
import datetime
import random
import sys
from pathlib import Path

BACKEND_SRC = Path(__file__).resolve().parents[1] / "src"
if str(BACKEND_SRC) not in sys.path:
    sys.path.insert(0, str(BACKEND_SRC))

from sqlalchemy import delete  # noqa: E402

from domain.portal.entities.portal import Portal  # noqa: E402
from domain.portal.enums import PortalStatusEnum  # noqa: E402
from domain.portal.value_objects.energy import Energy  # noqa: E402
from domain.portal.value_objects.expires_at import ExpiresAt  # noqa: E402
from domain.portal.value_objects.stability import PortalStability  # noqa: E402
from infra.db import PortalModel, create_engine, create_session_factory, session_scope  # noqa: E402
from infra.repositories.postgres import PostgresPortalRepository  # noqa: E402


def _portal(
    portal_id: int,
    name: str,
    world_destination: str,
    *,
    energy: int,
    stability: float,
    expires_in_minutes: float,
    status: PortalStatusEnum = PortalStatusEnum.open,
    count_observers: int = 0,
    marked: bool = False,
) -> Portal:
    return Portal(
        portal_id=portal_id,
        name=name,
        world_destination=world_destination,
        energy=Energy(energy),
        stability=PortalStability(stability),
        expires_at=ExpiresAt(datetime.datetime.utcnow() + datetime.timedelta(minutes=expires_in_minutes)),
        count_observers=count_observers,
        marked=marked,
        status=status,
    )


def curated_portals() -> list[Portal]:
    """A small, deliberately varied set covering every state the UI cares
    about: each risk factor on its own, a safe portal, a closed one, one
    with observers, one marked, and one already past its natural expiry.
    """
    return [
        _portal(1, "Alpha Gate", "Mars", energy=2, stability=9.0, expires_in_minutes=600),
        _portal(2, "Betelgeuse Rift", "Betelgeuse", energy=1, stability=1.5, expires_in_minutes=600),
        _portal(3, "Cinder Breach", "Io", energy=9, stability=8.0, expires_in_minutes=600),
        _portal(4, "Driftwood Seam", "Europa", energy=1, stability=9.0, expires_in_minutes=8),
        _portal(5, "Ember Hollow", "Titan", energy=8, stability=2.0, expires_in_minutes=240, count_observers=3),
        _portal(6, "Frostgate", "Enceladus", energy=0, stability=10.0, expires_in_minutes=1440, marked=True),
        _portal(7, "Glasswake", "Ganymede", energy=4, stability=6.5, expires_in_minutes=180),
        _portal(8, "Hollow Vale", "Callisto", energy=0, stability=10.0, expires_in_minutes=90, status=PortalStatusEnum.closed),
    ]


_ADJECTIVES = ["Silent", "Broken", "Whispering", "Ashen", "Hollow", "Distant", "Forgotten", "Shifting", "Pale", "Iron"]
_NOUNS = ["Gate", "Rift", "Breach", "Seam", "Hollow", "Wake", "Vale", "Threshold", "Passage", "Anomaly"]
_WORLDS = ["Mars", "Titan", "Europa", "Ganymede", "Callisto", "Enceladus", "Io", "Triton", "Vesta", "Ceres"]


def random_portals(count: int, *, start_id: int, seed: int | None = None) -> list[Portal]:
    rng = random.Random(seed)
    portals = []
    for offset in range(count):
        portal_id = start_id + offset
        name = f"{rng.choice(_ADJECTIVES)} {rng.choice(_NOUNS)}"
        world = rng.choice(_WORLDS)
        # A slice of these end up already expired (negative minutes), so a
        # freshly seeded DB also has a few naturally closed portals.
        expires_in_minutes = rng.uniform(-120, 2000)
        portals.append(
            _portal(
                portal_id,
                name,
                world,
                energy=rng.randint(0, 10),
                stability=round(rng.uniform(0, 10), 1),
                expires_in_minutes=expires_in_minutes,
                count_observers=rng.choice([0, 0, 0, 1, 2]),
                marked=rng.random() < 0.15,
            )
        )
    return portals


async def seed(database_url: str, *, reset: bool, extra: int, seed_value: int | None) -> None:
    engine = create_engine(database_url)
    session_factory = create_session_factory(engine)

    portals = curated_portals()
    if extra:
        next_id = max(p.id for p in portals) + 1
        portals += random_portals(extra, start_id=next_id, seed=seed_value)

    try:
        async with session_scope(session_factory) as session:
            if reset:
                await session.execute(delete(PortalModel))

            repo = PostgresPortalRepository(session)
            for portal in portals:
                await repo.add(portal)
    finally:
        await engine.dispose()

    print(f"Seeded {len(portals)} portal(s){' (table reset first)' if reset else ''}.")


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument(
        "--database-url",
        default=None,
        help="Overrides DATABASE_URL / backend/.env for this run only.",
    )
    parser.add_argument(
        "--reset",
        action="store_true",
        help="Delete all existing rows in `portals` before inserting the seed data.",
    )
    parser.add_argument(
        "--extra",
        type=int,
        default=0,
        metavar="N",
        help="Also insert N additional randomly generated portals (useful for testing pagination).",
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=None,
        help="Random seed for --extra, for reproducible runs.",
    )
    return parser.parse_args(argv)


def main() -> None:
    args = parse_args()

    database_url = args.database_url
    if database_url is None:
        from config.settings import settings

        database_url = settings.database_url

    asyncio.run(seed(database_url, reset=args.reset, extra=args.extra, seed_value=args.seed))


if __name__ == "__main__":
    main()
