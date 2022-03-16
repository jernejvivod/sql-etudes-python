import datetime

from sqlalchemy import func, asc, select
from sqlalchemy.orm import joinedload, contains_eager

from . import Session
from ..entities.entities import Employee, Title, DeptManager, DeptEmp, Salary


def get_all_employees(year=None):
    year_filter = [Salary.to_date == datetime.date(9999, 1, 1)] \
        if year is None \
        else [Salary.from_date <= datetime.date(year, 12, 31), Salary.to_date >= datetime.date(year, 1, 1)]

    with Session() as session:
        sbq = select(Employee.emp_no.distinct()) \
            .join(Salary) \
            .filter(*year_filter)
        return session.query(Employee).filter(Employee.emp_no.in_(sbq)).all()


def get_employees_for_title(title, year=None):
    year_filter = [Title.to_date == datetime.date(9999, 1, 1)] \
        if year is None \
        else [Title.from_date <= datetime.date(year, 12, 31), Title.to_date >= datetime.date(year, 1, 1)]

    with Session() as session:
        return session.query(Employee) \
            .join(Title) \
            .filter(Title.title == title.title) \
            .filter(*year_filter) \
            .all()


def get_employees_managers(year=None):
    year_filter = [DeptManager.to_date == datetime.date(9999, 1, 1)] \
        if year is None \
        else [DeptManager.from_date <= datetime.date(year, 12, 31), DeptManager.to_date >= datetime.date(year, 1, 1)]

    with Session() as session:
        return session.query(Employee) \
            .join(DeptManager) \
            .filter(*year_filter) \
            .all()


def get_employees_dept(dept, year=None):
    year_filter = [DeptEmp.to_date == datetime.date(9999, 1, 1)] \
        if year is None \
        else [DeptEmp.from_date <= datetime.date(year, 12, 31), DeptEmp.to_date >= datetime.date(year, 1, 1)]

    with Session() as session:
        return session.query(Employee) \
            .join(DeptEmp) \
            .filter(DeptEmp.dept_no == dept.dept_no) \
            .filter(*year_filter) \
            .all()


def get_employees_above_salary_percentile(percentile, year=None):
    year_filter = [Salary.to_date == datetime.date(9999, 1, 1)] \
        if year is None \
        else [Salary.from_date <= datetime.date(year, 12, 31), Salary.to_date >= datetime.date(year, 1, 1)]

    with Session() as session:
        percentile_val = session.query(func.percentile_disc(percentile).within_group(asc(Salary.salary))).filter(*year_filter).one()[0]
        return session.query(Employee) \
            .join(Salary) \
            .filter(*year_filter) \
            .filter(Salary.salary > percentile_val) \
            .options(contains_eager(Employee.salaries)) \
            .all()


def get_employees_above_salary_percentile_for_title(percentile, title, year=None):
    year_filter = [Title.to_date == datetime.date(9999, 1, 1)] \
        if year is None \
        else [Title.from_date <= datetime.date(year, 12, 31), Title.to_date >= datetime.date(year, 1, 1)]

    with Session() as session:
        percentile_val = session.query(func.percentile_cont(percentile).within_group(asc(Salary.salary))).join(Employee, Title).filter(*year_filter).one()[0]
        return session.query(Employee) \
            .join(Salary, Title) \
            .filter(Title.title == title.title) \
            .filter(*year_filter) \
            .filter(Salary.salary > percentile_val) \
            .all()


def get_employees_above_salary_percentile_for_managers(percentile, year=None):
    year_filter = (DeptManager.to_date == datetime.date(9999, 1, 1)) \
        if year is None \
        else (DeptManager.from_date <= datetime.date(year, 12, 31), DeptManager.to_date >= datetime.date(year, 1, 1))

    with Session() as session:
        percentile_val = session.query(func.percentile_cont(percentile).within_group(asc(Salary.salary))).filter(*year_filter).one()[0]
        return session.query(Employee) \
            .join(Salary) \
            .filter(*year_filter) \
            .filter(Salary.salary > percentile_val) \
            .all()


def get_employees_above_salary_percentile_for_dept(percentile, dept, year=None):
    year_filter = (DeptEmp.to_date == datetime.date(9999, 1, 1)) \
        if year is None \
        else (DeptEmp.from_date <= datetime.date(year, 12, 31), DeptEmp.to_date >= datetime.date(year, 1, 1))

    with Session() as session:
        percentile_val = session.query(func.percentile_cont(percentile).within_group(asc(Salary.salary))).filter(*year_filter).one()[0]
        return session.query(Employee) \
            .join(Salary) \
            .join(DeptEmp) \
            .filter(DeptEmp.dept_no == dept.dept_no) \
            .filter(*year_filter) \
            .filter(Salary.salary > percentile_val) \
            .all()
