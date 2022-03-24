from sql_etudes_python.entities.entities import Department
from sql_etudes_python.manager import Session


def get_all_departments():
    with Session() as session:
        return session.query(Department) \
            .all()
