from sqlalchemy import Column, Integer, String, Date, ForeignKey
from sqlalchemy.orm import declarative_base, relationship

# base classes ###
Base = declarative_base()


class TableSchema:
    __table_args__ = {"schema": "employees"}


# /base classes ###


# departments
class Department(Base, TableSchema):
    __tablename__ = 'departments'
    dept_no = Column(String, primary_key=True)
    dept_name = Column(String)


# dept_emp
class DeptEmp(Base, TableSchema):
    __tablename__ = 'dept_emp'
    emp_no = Column(Integer, ForeignKey('employees.employees.emp_no'), primary_key=True)
    dept_no = Column(String, ForeignKey('employees.departments.dept_no'), primary_key=True)
    dept = relationship("Department", backref="dept_emp")
    employee = relationship("Employee", backref="dept_emp")
    from_date = Column(Date)
    to_date = Column(Date)


# dept_manager
class DeptManager(Base, TableSchema):
    __tablename__ = 'dept_manager'
    dept_no = Column(String, ForeignKey('employees.departments.dept_no'))
    emp_no = Column(Integer, ForeignKey('employees.employees.emp_no'), primary_key=True)
    dept = relationship("Department", backref="dept_manager")
    employee = relationship("Employee", backref="dept_manager")
    from_date = Column(Date)
    to_date = Column(Date)


# employees
class Employee(Base, TableSchema):
    __tablename__ = 'employees'
    emp_no = Column(Integer, primary_key=True)
    birth_date = Column(Date)
    first_name = Column(String)
    last_name = Column(String)
    gender = Column(String)
    hire_date = Column(Date)


# salaries
class Salary(Base, TableSchema):
    __tablename__ = 'salaries'
    emp_no = Column(Integer, ForeignKey('employees.employees.emp_no'), primary_key=True)
    employee = relationship("Employee", backref="salaries")
    salary = Column(Integer)
    from_date = Column(Date, primary_key=True)
    to_date = Column(Date)


# titles
class Title(Base, TableSchema):
    __tablename__ = 'titles'
    emp_no = Column(Integer, ForeignKey('employees.employees.emp_no'), primary_key=True)
    employee = relationship("Employee", backref="title")
    title = Column(String)
    from_date = Column(Date)
    to_date = Column(Date)
