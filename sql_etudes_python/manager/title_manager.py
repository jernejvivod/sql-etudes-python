import datetime
from ..entities.entities import Title
from . import Session


def get_all_current_unique_titles():
    with Session() as session:
        return session.query(Title.title) \
            .filter(Title.to_date == datetime.date(9999, 1, 1)) \
            .distinct() \
            .all()
