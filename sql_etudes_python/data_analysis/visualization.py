from . import analysis


# Rank the employee titles according to the average salary for each department and for the whole company.
# Present the results in a bar chart.
def get_vis_analysis1():
    title_to_average_salary_company, title_to_dept_to_average_salary = analysis.get_data_analysis1()


# The company actively pursues gender equality. Prepare an analysis based on salaries and gender distribution
# by departments, managers, and titles. Present results in a chart (or several charts) of your choice.
def get_vis_analysis2():
    data = analysis.get_data_analysis2()


# Same as analysis2 but prepare an analysis also on a yearly basis (the same charts by year).
def get_vis_analysis3():
    data = analysis.get_data_analysis3()


# Find the most successful department (with highest mean salaries) and chart its characteristics (distribution of titles, salaries, genders, ...).
# Compare this chart with charts from other departments and hypothesize on reasons for success.
def get_vis_analysis4():
    data = analysis.get_data_analysis4()
