import re

import scipy.stats as stats
from tqdm import tqdm

from sql_etudes_python import constants
from sql_etudes_python.data_analysis import logger
from sql_etudes_python.data_analysis.res_container import ResContainer
from sql_etudes_python.manager import department_manager
from sql_etudes_python.manager import employee_manager
from sql_etudes_python.manager import salary_manager
from sql_etudes_python.manager import title_manager

"""
This script is used to obtain the data to perform the analyses required by the tasks using the SQLAlchemy ORM framework
Each function in this script is associated with one task and returns a ResContainer instance containing the extracted data in
the form of key-value-description triplets. These ResContainer instances are then used to produce the visualizations in the
visualization.py script located in the same package. Some results needed for the visualizations are produced (also) by the
analysis_psycopg2.py script located in the same package that uses the psycopg2 framework to query the database.

Author: Jernej Vivod (vivod.jernej@gmail.com)
"""


def get_data_analysis1():
    """Task instructions: Rank the employee titles according to the average salary for each department and for the whole company.
    Present the results in a bar chart.

    :return: ResContainer instance containing the obtained results
    """
    logger.info('Obtaining data for 1. analysis')

    # get all current unique titles
    logger.info('Obtaining all distinct titles and departments')
    titles = title_manager.get_all_distinct_titles()
    departments = department_manager.get_all_departments()

    # for each title compute the average salary for the whole company and for a specific department
    title_to_average_salary_company = dict()
    dept_to_title_to_average_salary = {dept.dept_name: dict() for dept in departments}
    logger.info('Computing salary data for titles')
    for title in tqdm(titles, colour='green', desc='Computing data for titles'):

        # for department
        for dept in departments:
            salaries_title_dept = salary_manager.get_salaries_title_dept(title, dept)
            dept_to_title_to_average_salary[dept.dept_name][title.title] = get_average_salary(salaries_title_dept)

        # for whole company
        title_to_average_salary_company[title.title] = get_average_salary(salary_manager.get_salaries_title(title))

    # add results to results container and return
    logger.info('Storing results in results container')
    res_container = ResContainer()
    res_container.add_res_with_desc(
        key='title_to_average_salary_company',
        res=title_to_average_salary_company,
        desc='map of titles to the average salary for the title for the whole company'
    )
    res_container.add_res_with_desc(
        key='dept_to_title_to_average_salary',
        res=dept_to_title_to_average_salary,
        desc='map of titles to the average salary for a specific department'
    )

    logger.info('Finished obtaining data for 1. analysis')
    return res_container


# The company actively pursues gender equality. Prepare an analysis based on salaries and gender distribution
# by departments, managers, and titles. Present results in a chart (or several charts) of your choice.
def get_data_analysis2():
    """Task instructions: The company actively pursues gender equality. Prepare an analysis based on salaries and gender distribution
    by departments, managers, and titles. Present results in a chart (or several charts) of your choice.

    :return: ResContainer instance containing the obtained results
    """
    logger.info('Obtaining data for 2. analysis')

    # get results irrespective of year
    data = get_gender_based_data(year=None)
    logger.info('Finished obtaining data for 2. analysis')
    return data


# Same as analysis2 but prepare an analysis also on a yearly basis (the same charts by year).
def get_data_analysis3():
    """Task instructions: Prepare the same analysis but also on a yearly basis.

    :return: ResContainer instance containing the obtained results
    """
    logger.info('Obtaining data for 3. analysis')

    # get list of relevant years
    logger.info('Obtaining list of relevant years')
    years = salary_manager.get_distinct_years_salaries_asc()

    # get and return results for each relevant year
    res_container = ResContainer()
    for year in years[:-1]:
        logger.info('Obtaining data for year {0}'.format(year))
        res_container.add_res_with_desc(str(year), get_gender_based_data(year), 'gender-based data for year {0}'.format(year))

    logger.info('Finished obtaining data for 3. analysis')
    return res_container


# Find the most successful department (with highest mean salaries) and chart its characteristics (distribution of titles, salaries, genders, ...).
# Compare this chart with charts from other departments and hypothesize on reasons for success.
def get_data_analysis5():
    """Task instructions: Find the most successful department (with highest mean salaries) and chart its characteristics (distribution of titles, salaries, genders, ...).
    Compare this chart with charts from other departments and hypothesize on reasons for success.

    :return: ResContainer instance containing the obtained results
    """
    logger.info('Obtaining data for 5. analysis')

    # compute mean salaries (current) for departments
    logger.info('Obtaining list of departments')
    departments = department_manager.get_all_departments()
    dept_no_to_mean_salary = dict()
    logger.info('Computing mean salary for all departments')
    for dept in tqdm(departments, colour='green', desc='Computing mean salary for departments'):
        dept_no_to_mean_salary[dept.dept_no] = salary_manager.get_mean_salary_dept(dept)

    # Compute lists of characteristics (single value) for each department (for Pearson correlation computation)
    # portion of female employees for departments
    dept_no_to_portion_number_female = dict()
    # portion of employees with title for department
    dept_no_to_title_to_portion_number = {dept.dept_no: dict() for dept in departments}
    # portion of senior titles for department
    dept_no_to_portion_number_senior = dict()
    # percentile values for department
    dept_no_to_salary_percentile_value = {dept.dept_no: dict() for dept in departments}

    titles = title_manager.get_all_distinct_titles()
    percentiles = [0.5, 0.75, 0.9, 0.95, 0.99]
    logger.info('Computing data for statistical correlation analysis for departments')
    for dept in tqdm(departments, colour='green', desc='computing data for correlation analysis for all departments'):
        # initialize counter of senior employees
        num_senior = 0
        employees_dept = employee_manager.get_employees_dept(dept)
        dept_no_to_portion_number_female[dept.dept_no] = \
            (get_portion_employees_for_gender(employees_dept, constants.FEMALE), get_number_employees_for_gender(employees_dept, constants.FEMALE))
        for title in titles:
            employees_dept_title = employee_manager.get_employees_for_title_for_department(dept, title)
            dept_no_to_title_to_portion_number[dept.dept_no][title.title] = (len(employees_dept_title) / len(employees_dept), len(employees_dept_title))
            if title in constants.SENIOR_TITLES:
                num_senior += len(employees_dept_title)

        dept_no_to_portion_number_senior[dept.dept_no] = (num_senior / len(employees_dept), num_senior)

        for percentile in percentiles:
            dept_no_to_salary_percentile_value[dept.dept_no][percentile] = salary_manager.get_percentile_value_dept(dept, percentile)

    # get sorted list of department numbers for aligning lists for computing statistics
    dept_nos_sorted = sorted(map(lambda x: x.dept_no, departments))

    logger.info('Computing correlation analysis and storing the results')

    # Initialize results container
    res_container = ResContainer()

    # add mean salaries for departments to results container
    res_container.add_res_with_desc('dept_no_to_mean_salary', dept_no_to_mean_salary, 'mapping of department numbers to mean salaries')

    # add computed statistics
    # 1. portion female employees
    p_corr_portion_female = p_corr([dept_no_to_portion_number_female[d][0] for d in dept_nos_sorted], [dept_no_to_mean_salary[d] for d in dept_nos_sorted])
    res_container.add_res_with_desc('portion_female', p_corr_portion_female, 'pearsonr results for the portion of female employees')

    # 1A. number female employees
    p_corr_num_female = p_corr([dept_no_to_portion_number_female[d][1] for d in dept_nos_sorted], [dept_no_to_mean_salary[d] for d in dept_nos_sorted])
    res_container.add_res_with_desc('number_female', p_corr_num_female, 'pearsonr results for the number of female employees')

    # 2., 2A., ... portion/number of title
    for title in titles:
        p_corr_portion_title = p_corr([dept_no_to_title_to_portion_number[d][title.title][0] for d in dept_nos_sorted], [dept_no_to_mean_salary[d] for d in dept_nos_sorted])
        p_corr_num_title = p_corr([dept_no_to_title_to_portion_number[d][title.title][1] for d in dept_nos_sorted], [dept_no_to_mean_salary[d] for d in dept_nos_sorted])
        title_snake_case = re.sub(r'(?<!^)(?=[A-Z])', '_', title.title.replace(' ', '')).lower()
        res_container.add_res_with_desc('portion_{0}'.format(title_snake_case), p_corr_portion_title, 'pearsonr results for the portion of {0} titles'.format(title.title))
        res_container.add_res_with_desc('number_{0}'.format(title_snake_case), p_corr_num_title, 'pearsonr results for the portion of {0} titles'.format(title.title))

    # 3. portion senior titles
    p_corr_portion_senior = p_corr([dept_no_to_portion_number_female[d][0] for d in dept_nos_sorted], [dept_no_to_mean_salary[d] for d in dept_nos_sorted])
    res_container.add_res_with_desc('portion_senior', p_corr_portion_senior, 'pearsonr results for the portion of employees with senior titles')

    # 3A. number senior titles
    p_corr_portion_senior = p_corr([dept_no_to_portion_number_female[d][1] for d in dept_nos_sorted], [dept_no_to_mean_salary[d] for d in dept_nos_sorted])
    res_container.add_res_with_desc('number_senior', p_corr_portion_senior, 'pearsonr results for the number of employees with senior titles')

    # 4. percentile values
    for percentile in percentiles:
        p_corr_percentile_value = p_corr([dept_no_to_salary_percentile_value[d][percentile] for d in dept_nos_sorted], [dept_no_to_mean_salary[d] for d in dept_nos_sorted])
        res_container.add_res_with_desc('percentile_value_{0}'.format(int(percentile * 100)), p_corr_percentile_value, 'pearsonr results for the {0}th percentile value'.format(int(percentile * 100)))

    logger.info('Finished obtaining data for 5. analysis')
    return res_container


def get_average_salary(salaries):
    if salaries:
        return sum(s.salary for s in salaries) / len(salaries)
    else:
        return -1.0


def get_portion_employees_for_gender(employees, gender):
    return get_number_employees_for_gender(employees, gender) / len(employees) \
        if len(employees) > 0 \
        else 0.0


def get_number_employees_for_gender(employees, gender):
    return len(list(filter(lambda e: e.gender == gender, employees)))


def p_corr(data1, data2):
    return stats.pearsonr(data1, data2)


def get_gender_based_data(year=None):
    # compute portion of female employees in the whole company
    logger.info('Obtaining portion of female employees')
    all_employees = employee_manager.get_all_employees(year)
    portion_female_all = get_portion_employees_for_gender(all_employees, constants.FEMALE)

    # compute portion of female employees for a specific title
    title_to_portion_female = dict()
    titles = title_manager.get_all_distinct_titles()
    logger.info('Obtaining portion of female employees for titles')
    for title in tqdm(titles, colour='green', desc='Obtaining portions of female employees for all titles'):
        employees_for_title = employee_manager.get_employees_for_title(title, year)
        title_to_portion_female[title.title] = get_portion_employees_for_gender(employees_for_title, constants.FEMALE)

    # compute portion of female employees that are department managers
    logger.info('Obtaining portion of female managers')
    employees_managers = employee_manager.get_employees_managers(year)
    portion_female_managers = get_portion_employees_for_gender(employees_managers, constants.FEMALE)

    # compute portion of females in a specific department
    dept_to_portion_female = dict()
    departments = department_manager.get_all_departments()
    logger.info('Obtaining portion of female employees for departments')
    for dept in tqdm(departments, colour='green', desc='Obtaining portions of female employees for all departments'):
        employees_dept = employee_manager.get_employees_dept(dept, year)
        dept_to_portion_female[dept.dept_name] = get_portion_employees_for_gender(employees_dept, constants.FEMALE)

    # Compute portion of women/men in top percentiles of earners for departments, managers, titles.
    percentiles = [0.9, 0.95, 0.99]
    salary_percentile_to_portion_female = dict()
    title_to_salary_percentile_to_portion_female = {t.title: dict() for t in titles}
    dept_to_salary_percentile_to_portion_female = {d.dept_name: dict() for d in departments}
    salary_percentile_to_portion_female_managers = dict()

    logger.info('Obtaining portions of female employees for salary percentiles (company, title, managers, departments)')
    for percentile in tqdm(percentiles, colour='green', desc='Obtaining portions of female employees for salary percentiles'):
        employees_above_percentile = employee_manager.get_employees_above_salary_percentile(percentile, year)
        salary_percentile_to_portion_female[percentile] = get_portion_employees_for_gender(employees_above_percentile, constants.FEMALE)

        for title in titles:
            employees_above_percentile_for_title = employee_manager.get_employees_above_salary_percentile_for_title(percentile, title, year)
            title_to_salary_percentile_to_portion_female[title.title][percentile] = get_portion_employees_for_gender(employees_above_percentile_for_title, constants.FEMALE)

        employees_above_percentile_managers = employee_manager.get_employees_above_salary_percentile_for_managers(percentile, year)
        salary_percentile_to_portion_female_managers[percentile] = get_portion_employees_for_gender(employees_above_percentile_managers, constants.FEMALE)

        for dept in departments:
            employees_above_percentile_for_dept = employee_manager.get_employees_above_salary_percentile_for_dept(percentile, dept, year)
            dept_to_salary_percentile_to_portion_female[dept.dept_name][percentile] = get_portion_employees_for_gender(employees_above_percentile_for_dept, constants.FEMALE)

    # Add results to results container and return.

    logger.info('Storing results in results container')

    res_container = ResContainer()
    res_container.add_res_with_desc(
        key='portion_female_all',
        res=portion_female_all,
        desc='portion of female employees in the company'
    )
    res_container.add_res_with_desc(
        key='title_to_portion_female',
        res=title_to_portion_female,
        desc='map of company titles to portion of female employees having the title'
    )
    res_container.add_res_with_desc(
        key='portion_female_managers',
        res=portion_female_managers,
        desc='portion of female managers'
    )
    res_container.add_res_with_desc(
        key='dept_to_portion_female',
        res=dept_to_portion_female,
        desc='map of departments to portions of female employees working in the department'
    )
    res_container.add_res_with_desc(
        key='salary_percentile_to_portion_female',
        res=salary_percentile_to_portion_female,
        desc='map of a set of percentiles to portions of female employees in that salary percentile'
    )
    res_container.add_res_with_desc(
        key='title_to_salary_percentile_to_portion_female',
        res=title_to_salary_percentile_to_portion_female,
        desc='map of titles to percentiles to portions of female employees in that percentile for that title'
    )
    res_container.add_res_with_desc(
        key='salary_percentile_to_portion_female_managers',
        res=salary_percentile_to_portion_female_managers,
        desc='map of salary percentiles to portions of female employees for managers in that salary percentile'
    )
    res_container.add_res_with_desc(
        key='dept_to_salary_percentile_to_portion_female',
        res=dept_to_salary_percentile_to_portion_female,
        desc='map of departments to salary percentiles to portions of female employees having in that salary percentile for that department'
    )

    return res_container
