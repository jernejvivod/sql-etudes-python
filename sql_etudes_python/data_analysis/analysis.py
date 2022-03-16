from sql_etudes_python import constants
from sql_etudes_python.manager import department_manager
from sql_etudes_python.manager import employee_manager
from sql_etudes_python.manager import salary_manager
from sql_etudes_python.manager import title_manager


# Rank the employee titles according to the average salary for each department and for the whole company.
# Present the results in a bar chart.
def get_data_analysis1():
    titles = title_manager.get_all_current_unique_titles()
    departments = department_manager.get_all_departments()

    title_to_average_salary_company = dict()
    title_to_dept_to_average_salary = {t.title: dict() for t in titles}

    for title in titles:
        for dept in departments:
            salaries_title_dept = salary_manager.get_salaries_title_dept(title, dept)
            average_salary_title_dept = get_average_salary(salaries_title_dept)
            title_to_dept_to_average_salary[title.title][dept.dept_name] = average_salary_title_dept

        salaries_title_company = salary_manager.get_salaries_title(title)
        average_salary_title_company = get_average_salary(salaries_title_company)
        title_to_average_salary_company[title.title] = average_salary_title_company

    return title_to_average_salary_company, title_to_dept_to_average_salary


# The company actively pursues gender equality. Prepare an analysis based on salaries and gender distribution
# by departments, managers, and titles. Present results in a chart (or several charts) of your choice.
def get_data_analysis2():
    # Compute portion of women/men in company, departments, managers, titles
    all_employees = employee_manager.get_all_employees()
    portion_female_all = get_portion_employees_for_gender(all_employees, constants.FEMALE)

    title_to_portion_female = dict()

    titles = title_manager.get_all_current_unique_titles()
    for title in titles:
        employees_for_title = employee_manager.get_employees_for_title(title, 1994)
        title_to_portion_female[title] = get_portion_employees_for_gender(employees_for_title, constants.FEMALE)

    employees_managers = employee_manager.get_employees_managers()
    portion_female_managers = get_portion_employees_for_gender(employees_managers, constants.FEMALE)

    dept_to_portion_female = dict()

    for dept in department_manager.get_all_departments():
        employees_dept = employee_manager.get_employees_dept(dept)
        dept_to_portion_female[dept.dept_name] = get_portion_employees_for_gender(employees_dept, constants.FEMALE)

    # Compute portion of women/men in top percentiles of earners for departments, managers, titles.

    percentiles = [0.9, 0.95, 0.99]
    salary_percentile_to_portion_female = dict()
    title_to_salary_percentile_to_portion_female = {t.title: dict() for t in titles}

    for percentile in percentiles:
        employees_above_percentile = employee_manager.get_employees_above_salary_percentile(percentile)
        salary_percentile_to_portion_female[percentile] = get_portion_employees_for_gender(employees_above_percentile, constants.FEMALE)

        for title in titles:
            employees_above_percentile_for_title = employee_manager.get_employees_above_salary_percentile_for_title(percentile, title)
            title_to_salary_percentile_to_portion_female[title.title][percentile] = get_portion_employees_for_gender(employees_above_percentile_for_title, constants.FEMALE)
        # TODO for managers, for departments

    # Compute portion of women in senior vs non-senior positions of specific title
    # TODO use title_to_portion_female dict

    # return portion_female_all, title_to_portion_female


# Same as analysis2 but prepare an analysis also on a yearly basis (the same charts by year).
def get_data_analysis3():
    # Plot changes in above values by year
    # TODO parametrize get_data_analysis2 with year
    pass


# Find the most successful department (with highest mean salaries) and chart its characteristics (distribution of titles, salaries, genders, ...).
# Compare this chart with charts from other departments and hypothesize on reasons for success.
def get_data_analysis4():
    pass


def get_average_salary(salaries):
    if salaries:
        return sum(s.salary for s in salaries) / len(salaries)
    else:
        return -1.0


def get_portion_employees_for_gender(employees, gender):
    return len(list(filter(lambda e: e.gender == gender, employees))) / len(employees) \
        if len(employees) > 0 \
        else 0.0
