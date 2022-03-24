from tqdm import tqdm

from sql_etudes_python import constants
from sql_etudes_python.data_analysis import logger
from sql_etudes_python.data_analysis.res_container import ResContainer
from sql_etudes_python.manager import connect, disconnect

"""
This script is used to obtain the data to perform the analyses required by the tasks using the psycopg2 framework
Each function in this script is associated with one task and either prints the results 
(in the case of functionality duplicated from the script analysis.py from the same folder) or returns a ResContainer instance containing 
the extracted data in the form of key-value-description triplets. 
These ResContainer instances are then used to produce the visualizations in the visualization.py script located in the same package. 
Some results needed for the visualizations are produced (also) by the analysis.py script located in the same package that uses the 
SQLAlchemy framework to query the database.

Author: Jernej Vivod (vivod.jernej@gmail.com)
"""


def get_data_analysis1():
    """Task instructions: Rank the employee titles according to the average salary for each department and for the whole company.
    Present the results in a bar chart.
    """

    logger.info('Performing 1. analysis (psycopg2)')

    def get_results(curs, dept_no):
        """get results for ranking titles by average salary for company or for department
        :param dept_no: if None, compute results for whole company, else for department
        :param curs: psycopg2 cursor
        :return: results of query
        """
        # noinspection PyStringFormat
        sql_query = \
            """SELECT AVG(salaries.salary) as average_salary, titles.title
            FROM employees.employees
            JOIN employees.salaries ON employees.emp_no = salaries.emp_no
            JOIN employees.titles ON employees.emp_no = titles.emp_no
            {0}
            WHERE salaries.to_date = '9999-01-01' 
            AND titles.to_date = '9999-01-01'
            {1}
            GROUP BY titles.title
            ORDER BY average_salary DESC""".format(*(["JOIN employees.dept_emp ON employees.emp_no = dept_emp.emp_no",
                                                      "AND dept_emp.to_date = '9999-01-01' AND dept_emp.dept_no = %(dept_no)s"] if dept_no is not None else ["", ""]))

        curs.execute(sql_query, {'dept_no': dept_no})
        return curs.fetchall()

    # connect to database
    conn = connect()
    with conn:
        with conn.cursor() as curs:
            # RESULTS FOR WHOLE COMPANY
            print('Rankings of the titles for the whole company:')
            for rank, res in enumerate(get_results(curs, None)):
                print('({0}) {1} - {2}'.format(rank, res[1], float(res[0])))

            # RESULTS FOR INDIVIDUAL DEPARTMENTS
            # get all department numbers
            sql_query_departments = \
                """SELECT DISTINCT d.dept_no, d.dept_name
                   FROM employees.departments d
                   ORDER BY d.dept_no"""
            curs.execute(sql_query_departments)
            dept_no_to_dept_name = dict(curs.fetchall())

            res_depts = dict()
            for dept_no in dept_no_to_dept_name.keys():
                res_depts[dept_no] = get_results(curs, dept_no)

            print('Rankings of the titles by department:')
            for dept_no in dept_no_to_dept_name:
                print('##### {0} #####'.format(dept_no_to_dept_name[dept_no]))
                for rank, res in enumerate(res_depts[dept_no]):
                    print('({0}) {1} - {2}'.format(rank, res[1], float(res[0])))

    # disconnect from database
    disconnect(conn)
    logger.info('Finished obtaining data for 1. analysis')


def get_data_analysis4():
    """Task instructions: Check if some employees earn more than their managers. Split the results by year, gender and
    department if such employees exist.
    """

    logger.info('Performing 4. analysis (psycopg2)')

    def get_results(curs, year=None, dept_no=None, gender=None):
        """Compute number of employees earning more than their managers (by year, department number and gender)

        :param curs: psycopg2 cursor
        :param year: year for which to compute the results
        :param dept_no: department number for which to compute the results
        :param gender: gender for which to compute the results
        :return: results of query
        """
        filter_list = ["", "", ""]
        if year is not None:
            filter_list[0] = \
                """ WHERE dept_emp.from_date <= '{0}-12-31' AND dept_emp.to_date >= '{0}-01-01'
                AND managers.from_date <= '{0}-12-31' AND managers.to_date >= '{0}-01-01'
                AND managers_salaries.from_date <= '{0}-12-31' AND managers_salaries.to_date >= '{0}-01-01'
                AND employees_salaries.from_date <= '{0}-12-31' AND employees_salaries.to_date >= '{0}-01-01'
                AND employees_salaries.emp_no <> managers_salaries.emp_no 
                AND employees_salaries.salary > managers_salaries.salary """.format(str(year))
        else:
            filter_list[0] = \
                """ WHERE dept_emp.to_date = '9999-01-01' 
                AND managers.to_date = '9999-01-01' 
                AND managers_salaries.to_date = '9999-01-01' 
                AND employees_salaries.to_date = '9999-01-01' 
                AND employees_salaries.emp_no <> managers_salaries.emp_no 
                AND employees_salaries.salary > managers_salaries.salary """
        if dept_no is not None:
            filter_list[1] = "AND dept_emp.dept_no = %(dept_no)s"
        if gender is not None:
            filter_list[2] = "AND employees.gender = %(gender)s"

        sql_query = \
            """SELECT COUNT(DISTINCT employees.emp_no)
            FROM employees.employees
            JOIN employees.dept_emp on employees.emp_no = dept_emp.emp_no
            JOIN employees.dept_manager as managers on dept_emp.dept_no = managers.dept_no
            JOIN employees.salaries as managers_salaries on managers.emp_no = managers_salaries.emp_no
            JOIN employees.salaries as employees_salaries on employees.emp_no = employees_salaries.emp_no
            {0}
            {1} 
            {2}""".format(*filter_list)

        curs.execute(sql_query, {'dept_no': dept_no, 'gender': gender})
        return curs.fetchall()

    res_container = ResContainer()

    # connect to database
    conn = connect()
    with conn:
        with conn.cursor() as curs:
            # get relevant years
            relevant_years_sql_query = \
                """
                WITH years as (SELECT EXTRACT(YEAR FROM salaries.from_date) as year FROM employees.salaries)
                SELECT DISTINCT year FROM years
                ORDER BY year
                """
            curs.execute(relevant_years_sql_query)
            years = [int(year[0]) for year in curs.fetchall()]

            # get all department numbers
            sql_query_departments = \
                """SELECT DISTINCT d.dept_no, d.dept_name
                   FROM employees.departments d
                   ORDER BY d.dept_no"""
            curs.execute(sql_query_departments)
            dept_no_to_dept_name = dict(curs.fetchall())

            res_container.add_res_with_desc('years', years, 'list of relevant years')
            res_container.add_res_with_desc('dept_names', list(dept_no_to_dept_name.values()), 'list of department names')

            logger.info('computing data segmented by years, departments and genders and storing results in results container')
            for year in tqdm(years):

                # compute number of employees earning more than their managers for year
                res_container.add_res_with_desc(
                    'n_employees_earn_more_than_managers_{0}'.format(year),
                    get_results(curs, year=year)[0][0],
                    'number of employees that earn more than their managers in year {0}'.format(year)
                )
                for dept_no in dept_no_to_dept_name.keys():
                    # compute number of employees earning more than their managers for year and for department
                    res_container.add_res_with_desc(
                        'n_employees_earn_more_than_managers_{0}_{1}'.format(year, dept_no_to_dept_name[dept_no]),
                        get_results(curs, dept_no=dept_no, year=year)[0][0],
                        'number of employees that earn more than their managers in year {0} in department {1}'.format(year, dept_no_to_dept_name[dept_no])
                    )
                # compute number of female employees earning more than their managers for year
                res_container.add_res_with_desc(
                    'n_female_earn_more_than_managers_{0}'.format(year),
                    get_results(curs, year=year, gender=constants.FEMALE)[0][0],
                    'number of female employees that earn more than their managers in year {0}'.format(year)
                )

    disconnect(conn)
    logger.info('Finished obtaining data for 4. analysis')
    return res_container
