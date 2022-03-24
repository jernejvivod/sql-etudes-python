import datetime

from sqlalchemy import select, extract, asc, func

from sql_etudes_python.manager import Session
from sql_etudes_python.entities.entities import Employee, Title, DeptEmp, Salary


def get_salaries_title(title):
    with Session() as session:
        sbq = select(Employee.emp_no) \
            .join(Title) \
            .filter(Title.title == title.title, Title.to_date == datetime.date(9999, 1, 1))
        return session.query(Salary) \
            .filter(Salary.emp_no.in_(sbq), Salary.to_date == datetime.date(9999, 1, 1)) \
            .all()


def get_salaries_title_dept(title, dept):
    with Session() as session:
        sbq = select(Employee.emp_no) \
            .join(Title) \
            .join(DeptEmp) \
            .filter(Title.title == title.title,
                    Title.to_date == datetime.date(9999, 1, 1),
                    DeptEmp.dept_no == dept.dept_no,
                    DeptEmp.to_date == datetime.date(9999, 1, 1))
        return session.query(Salary) \
            .filter(Salary.emp_no.in_(sbq), Salary.to_date == datetime.date(9999, 1, 1)) \
            .all()


def get_distinct_years_salaries_asc():
    with Session() as session:
        return list(
            map(lambda x: int(x[0]),
                session.query(extract('year', Salary.from_date).label('year'))
                .distinct()
                .order_by(asc('year')).all()
                )
        )


def get_mean_salary_dept(dept, year=None):
    year_filter = [Salary.to_date == datetime.date(9999, 1, 1)] \
        if year is None \
        else [Salary.from_date <= datetime.date(year, 12, 31), Salary.to_date >= datetime.date(year, 1, 1)]
    with Session() as session:
        return int(session.query(func.avg(Salary.salary).label('mean_salary_for_dept'))
                   .join(Employee, DeptEmp).filter(DeptEmp.dept_no == dept.dept_no)
                   .filter(*year_filter).one().mean_salary_for_dept)


def get_percentile_value_dept(dept, percentile, year=None):
    year_filter = [Salary.to_date == datetime.date(9999, 1, 1), DeptEmp.to_date == datetime.date(9999, 1, 1)] \
        if year is None \
        else [Salary.from_date <= datetime.date(year, 12, 31), Salary.to_date >= datetime.date(year, 1, 1),
              DeptEmp.from_date <= datetime.date(year, 12, 31), DeptEmp.to_date >= datetime.date(year, 1, 1)]

    with Session() as session:
        return session.query(func.percentile_cont(percentile).within_group(asc(Salary.salary)).label('percentile_val')) \
            .join(Employee, DeptEmp) \
            .filter(DeptEmp.dept_no == dept.dept_no) \
            .filter(*year_filter) \
            .one() \
            .percentile_val
