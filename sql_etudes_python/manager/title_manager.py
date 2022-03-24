from sql_etudes_python.manager import Session
from sql_etudes_python.entities.entities import Title

# TODO modify to return list of strings
def get_all_distinct_titles():
    with Session() as session:
        return session.query(Title.title) \
            .distinct() \
            .all()


if __name__ == '__main__':
    res = get_all_distinct_titles()