from ..entities.entities import Department
from . import Session


def get_all_departments():
    with Session() as session:
        return session.query(Department)\
            .all()
