from sql_etudes_python.data_analysis import analysis, visualization
from sql_etudes_python.data_analysis import analysis_psycopg2

"""Main script used to produce the data needed for the analysis and visualize it.

See the README.md in the project root folder for more information.
    
"""

if __name__ == '__main__':
    # get data and perform visualizations for the 1. task
    # res_container_analysis1 = analysis.get_data_analysis1()
    # visualization.get_vis_analysis1(res_container_analysis1)

    # # get data and perform visualizations for the 2. task
    # res_container_analysis2 = analysis.get_data_analysis2()
    # visualization.get_vis_analysis2(res_container_analysis2)

    # get data and perform visualizations for the 3. task
    # res_container_analysis3 = analysis.get_data_analysis3()
    # visualization.get_vis_analysis3(res_container_analysis3)
    # visualization.get_vis_analysis3(None)

    # get data and perform visualizations for the 4. task
    res_container_analysis4 = analysis_psycopg2.get_data_analysis4()
    visualization.get_vis_analysis4(res_container_analysis4)

    # get data and perform visualizations for the 5. task
    # res_container_analysis5 = analysis.get_data_analysis5()
    # visualization.get_vis_analysis5(res_container_analysis5)
