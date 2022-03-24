import os
import warnings

import matplotlib.pyplot as plt
import pandas as pd

from sql_etudes_python.data_analysis import logger

"""
This script is used to obtain the results visualizations required by the tasks. The functions are provided
with a ResContainer instance containing the key-value-description triplets representing the results computed
using either the analsys.py or analysis_psycopg2.py scripts. The functions produce plots and LaTeX tables
that are saved to the ./results directory. The functions are called from the main.py script in the root package.

Author: Jernej Vivod (vivod.jernej@gmail.com)
"""


def get_vis_analysis1(res_container):
    """Task instructions: Rank the employee titles according to the average salary for each department
    and for the whole company. Present the results in a bar chart.

    :param res_container: ResContainer instance containing the results to plot
    """
    logger.info('Obtaining visualizations for 1. task')

    # path to results directory
    res_dir_path = os.path.join(os.path.dirname(__file__), 'results/')

    # plot ranking of titles by average salary
    title_to_average_salary_company = res_container.get_res('title_to_average_salary_company')
    plt.bar(*list(zip(*sorted(map(lambda x: (x[0].replace(' ', '\n'), x[1]), title_to_average_salary_company.items()), key=lambda x: x[1], reverse=True))), color='lightskyblue')
    plt.ylim([min(title_to_average_salary_company.values()) - 5000, max(title_to_average_salary_company.values()) + 5000])
    plt.ylabel('Average Salary')
    plt.savefig(os.path.join(res_dir_path, 'salary_rankings.svg'))

    # get table of rankings of titles based on average salary by department
    data_df = pd.DataFrame(res_container.get_res('dept_to_title_to_average_salary'))
    for (col_name, col_data) in data_df.iteritems():
        title_to_rank = {k: idx + 1 for (idx, (k, v)) in enumerate(sorted(data_df[col_name].items(), key=lambda x: x[1], reverse=True)) if v != -1}
        for k in col_data.keys():
            col_data[k] = '{:.1f}'.format(col_data[k]) + ' ({0})'.format(title_to_rank[k]) if k in title_to_rank else '-'

    with open(os.path.join(res_dir_path, 'latex_table_analysis1.tex'), 'w') as f:
        latex_output_str = data_df.style.to_latex(hrules=True, column_format='l|' + 'l' * data_df.shape[1])
        f.write(latex_output_str.replace('\\\\', '\\\\ \\hline', 1))


def get_vis_analysis2(res_container):
    """Task instructions: The company actively pursues gender equality. Prepare an analysis based on salaries and gender distribution
    by departments, managers, and titles. Present results in a chart (or several charts) of your choice.

    :param res_container: ResContainer instance containing the results to plot
    """
    warnings.simplefilter(action='ignore', category=FutureWarning)
    logger.info('Obtaining visualizations for 2. task')

    def append_port_val_to_df(dataframe, val, name):
        """Append value val and 1-val to dataframe (with predefined column names) for specified index name
        """
        return dataframe.append(pd.Series({'Portion female employees': val, 'Portion male employees': 1 - val}, name=name))

    # path to results directory
    res_dir_path = os.path.join(os.path.dirname(__file__), 'results/')

    # plot gender-based stats as a stacked horizontal bar plot
    plt.rcParams.update({'font.size': 7})
    df = pd.DataFrame()
    df = append_port_val_to_df(df, res_container.get_res('portion_female_all'), 'All\nemployees')
    df = append_port_val_to_df(df, res_container.get_res('portion_female_managers'), 'Managers')
    for k, v in res_container.get_res('salary_percentile_to_portion_female').items():
        df = append_port_val_to_df(df, v, '{0}th salary\npercentile'.format(str(int(k * 100))))

    for k, v in res_container.get_res('title_to_portion_female').items():
        df = append_port_val_to_df(df, v, '{0}'.format(k.replace(' ', '\n')))

    get_annotated_stacked_port_barh_plot(df, os.path.join(res_dir_path, 'female_employee_portions.svg'))

    # plot gender ratios for departments
    df = pd.DataFrame()
    for k, v in res_container.get_res('dept_to_portion_female').items():
        df = append_port_val_to_df(df, v, '{0}'.format(k).replace(' ', '\n'))

    get_annotated_stacked_port_barh_plot(df, os.path.join(res_dir_path, 'female_employee_portions2.svg'))


def get_vis_analysis3(res_container):
    """Task instructions: Prepare the same analysis but also on a yearly basis.

    :param res_container: ResContainer instance containing the results to plot
    """
    logger.info('Obtaining visualizations for 3. task')

    # path to results directory
    res_dir_path = os.path.join(os.path.dirname(__file__), 'results/')

    # TODO remove from final code
    import pickle as pkl
    with open('datadata.pkl', 'rb') as f:
        res_container = pkl.load(f)

    # get concatenated data for years
    keys_for_concat = {k: [] for k in res_container.get_res(next(iter(res_container.keys()))).keys()}

    # get dictionary mapping data key values to lists of this data for all years (ascending)
    years = sorted(list(res_container.keys()))
    for year in sorted(res_container.keys()):
        for k in res_container.get_res(year).keys():
            keys_for_concat[k].append(res_container.get_res(year).get_res(k))

    # plot gender ratios (portion female) for various data
    plt.plot(years, keys_for_concat['portion_female_all'], label='Portion female employees')
    plt.plot(years, [d['Senior Engineer'] for d in keys_for_concat['title_to_portion_female']], label='Portion female senior engineers')
    plt.plot(years, [d['Senior Staff'] for d in keys_for_concat['title_to_portion_female']], label='Portion female senior staff')
    plt.plot(years, [d['Manager'] for d in keys_for_concat['title_to_portion_female']], label='Portion female managers')
    plt.plot(years, [d[0.99] for d in keys_for_concat['salary_percentile_to_portion_female']], label='Portion female employees\nin 99th salary percentile')
    plt.ylabel('Portion female employees')
    plt.xticks(years, rotation='60')
    plt.legend(loc='upper right')
    plt.savefig(os.path.join(res_dir_path, 'female_employee_portions_by_year.svg'))


def get_vis_analysis4(res_container):
    """Check if some employees earn more than their managers. Split the results by year, gender and
    department if such employees exist.

    :param res_container: ResContainer instance containing the results to plot
    """

    # path to results directory
    res_dir_path = os.path.join(os.path.dirname(__file__), 'results/')

    # draw plot of number of employees that earn more than their managers wrt. year
    years = res_container.get_res('years')

    # get y-axis values
    n_employees_earn_more_than_managers_for_year = []
    for year in years:
        n_employees_earn_more_than_managers_for_year.append(res_container.get_res('n_employees_earn_more_than_managers_{0}'.format(year)))

    # get and save bar plot
    plt.bar(years, n_employees_earn_more_than_managers_for_year, color='skyblue')
    plt.xticks(years, rotation='65')
    plt.ylabel('Number of employees earning more than their managers')
    plt.savefig(os.path.join(res_dir_path, 'employees_earn_more_than_managers_by_year.svg'))
    plt.clf()

    # draw heatmap of employees that earn more than their managers wrt. year and department
    dept_names = res_container.get_res('dept_names')
    heatmap_data = [[0 for _ in range(len(years))] for _ in range(len(dept_names))]
    for i, year in enumerate(years):
        for j, dept_name in enumerate(dept_names):
            heatmap_data[j][i] = res_container.get_res('n_employees_earn_more_than_managers_{0}_{1}'.format(year, dept_name))

    # draw heatmap
    fig, ax = plt.subplots()
    ax.imshow(heatmap_data)
    ax.set_xticks(range(len(years)), labels=years)
    ax.set_yticks(range(len(dept_names)), labels=dept_names)
    plt.setp(ax.get_xticklabels(), rotation=45, ha="right",
             rotation_mode="anchor")
    fig.tight_layout()
    plt.savefig(os.path.join(res_dir_path, 'employees_earn_more_than_managers_by_year_by_dept.svg'))
    plt.clf()

    # draw stacked horizontal bar plot for ratios of female employees that earn more than their managers wrt. year
    df = pd.DataFrame({k: [p, 1 - p] for k in years
                       for p in
                       [res_container.get_res('n_female_earn_more_than_managers_{0}'.format(k)) /
                        res_container.get_res('n_employees_earn_more_than_managers_{0}'.format(k))]}).T

    df.columns = ['Portion\nfemale employees', 'Portion\nmale employees']
    get_annotated_stacked_port_barh_plot(df, os.path.join(res_dir_path, 'female_employee_portions_earn_more_than_managers.svg'))


def get_vis_analysis5(res_container):
    """Task instructions: Find the most successful department (with highest mean salaries) and chart its characteristics (distribution of titles, salaries, genders, ...).
    Compare this chart with charts from other departments and hypothesize on reasons for success.

    :param res_container: ResContainer instance containing the results to plot
    """
    logger.info('Obtaining visualizations for 5. task')

    # mapping of keys of the results container to the names of rows in the output table
    res_container_key_to_row_name = {
        'portion_female': 'Portion female employees',
        'number_senior': 'Number of senior employees',
        'portion_engineer': 'Portion engineers',
        'number_senior_engineer': 'Number of senior engineers',
        'portion_senior': 'Portion senior employees'
    }

    # path to results directory
    res_dir_path = os.path.join(os.path.dirname(__file__), 'results/')

    # get table for the computed stats
    data_df = pd.DataFrame([pd.Series(res_container.get_res(k), name=res_container_key_to_row_name[k]) for k in res_container_key_to_row_name.keys()])
    sort_col = 'corr. coefficient'
    data_df.columns = [sort_col, 'p-value']
    with open(os.path.join(res_dir_path, 'latex_table_analysis5.tex'), 'w') as f:
        latex_output_str = data_df.sort_values(by=[sort_col]).style.to_latex(hrules=True, column_format='l|' + 'l' * data_df.shape[1])
        f.write(latex_output_str.replace('\\\\', '\\\\ \\hline', 1))


def get_annotated_stacked_port_barh_plot(df, save_path):
    """
    Get horizontal stacked bar plot for portions

    :param df: Pandas nx2 dataframe containing the data to plot
    :param save_path: path for the produced plot
    """
    df_rev = df.iloc[::-1]
    df_rev.plot(kind='barh', stacked=True)
    for i in range(-1, df_rev.shape[0] - 1):
        plt.text(df_rev.iloc[i + 1, 0] - 0.2, i + 0.9, '{0:.2f}%'.format(df_rev.iloc[i + 1, 0] * 100))
        plt.text(df_rev.iloc[i + 1, 0] + 0.1, i + 0.9, '{0:.2f}%'.format(df_rev.iloc[i + 1, 1] * 100))
    plt.legend(loc='upper right')
    plt.savefig(save_path)
