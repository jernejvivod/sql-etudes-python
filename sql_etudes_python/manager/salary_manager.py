import datetime
from sqlalchemy import select

from . import Session
from ..entities.entities import Employee, Title, DeptEmp, Salary


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
