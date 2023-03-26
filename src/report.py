import matplotlib.pyplot as plt
import pandas as pd
from math import pi
import matplotlib.ticker as mtick
import datetime

from calculate import get_metrics_dict

# KPIs format
metrics_is_percentage = {'engagement': True, 'velocity': False, 'independence': True,
                         'learning': True, 'versatility': True, 'complexity': True, 
                         'sociability': True, 'participation': True, 'connection': True,
                         'management': True, 'guidance': True, 'responsibility': True}
# KPIs colors
metrics_colors = {'performance': '#66c2a5',
                  'productivity': '#8da0cb',
                  'adaptability': '#e78ac3',
                  'teamwork': '#a6d854', 
                  'mentoring': '#ffd92f', 
                  'grey': '#b3b3b3',
                  'red': '#fc8d62'}
# colormap
cmap = 'Set3'


def employee_report(employee, year, info, kpi, score, time_split, by_project,
                    yearly, save=None, dpi=1000):
    """
    Creates an employee performance report.

    Parameters
    ----------
    employee : str
        Employee name. 
    year : int
        Year that defines the period of the report. 
    info : pandas.Series
        General information (index): first date, last date, duration,
        #logs, #hours, #issues.
    kpi : pandas.Series
        Performance KPIs (index): velocity, engagement, independence,
        learning, versatility, complexity, sociability, participation,
        connection, management, guidance, responsibility.
    score : pandas.DataFrame
        Aggregated performance KPIs of employees (index): productivity,
        adaptability, teamwork, mentoring, performance.
    time_split : pandas.Series
        Dedicated time split, leadership, collaboration, participation
        (index).
    by_proyect : pandas.Series
        Dedicated time split by project (index).
    yearly : pandas.Series
        Final performance KPI by year (index).
    save : str or path-like or None (default)
        A path or a Python file-like object where the report will be saved.        
    dpi : int
        The resolution in dots per inch to save the report.
    """
    
    def kpi_plot(value, label, ax, sizes=[24, 36], decimals=2, is_percentage=False):
        """ Creates a text plot to present the KPI value.
         
        """
        value_label = value_string(value, decimals, is_percentage)   
        ax.set_axis_off()
        ax.add_artist(plt.text(0.5, 0.7, s=label, size=sizes[0], ha='center'));
        ax.add_artist(plt.text(0.5, 0.3, s=value_label, size=sizes[1], ha='center'));
        
    def gauge_plot(value, title, color, sizes, decimals=0, is_percentage=True):
        """ Creates a gauge plot to present the KPI value.
         
        """
        value_label = value_string(value, decimals, is_percentage)
        value = -value * 100

        startangle = 90
        x = (value * pi *2)/ 100
        left = (startangle * pi *2)/ 360 #this is to control where the bar starts
        plt.xticks([])
        plt.yticks([])
        ax.spines.clear()
        ax.barh(1, x, left=left, height=1, color=color);
        plt.ylim(-3, 3)
        plt.text(0, -3, value_label, ha='center', va='center', fontsize=sizes[0]);
        plt.title(title, fontsize=sizes[1], position=(0.5, 0))
    
    def value_string(value, decimals, is_percentage):
        """ Converts a value in a formatted string.
         
        """
        if type(value) != str:
            if isinstance(value, datetime.date) or isinstance(value, pd.Timestamp):
                value_label = value.strftime('%d/%m/%Y')
            else:
                if is_percentage:
                    value = value * 100
                if decimals == 0:
                    value = round(value)
                else:
                    value = round(value, decimals)
                value_label = str(value)
                if is_percentage:
                    value_label = value_label + '%'
        else:
            value_label = value
            
        return value_label
    
    def pie_plot(series, title, ax, limit=6):
        """ Creates a pie plot.
         
        """
        series = series.sort_values(ascending=False)
        series = series.rename('')
        if len(series) > limit:
            series['other'] = series.iloc[limit:].sum() 
            series = series.drop(series.index[limit:-1])
        series.plot.pie(autopct='%1.1f%%', ax=ax, cmap=cmap, fontsize=20)
        plt.title(title, fontsize=24, position=(0, 0))
    
    def yearly_plot(yearly):
        """ Creates an annotated plot to show the evolution by year.
         
        """
        yearly.fillna(-1).plot(marker='o', linewidth=3, markersize=20, legend=False, fontsize=20, 
                    grid=True, color=metrics_colors['performance'], ax=ax)
        plt.title('Performance by Year', fontsize=24, ha='center')
        for i, x in enumerate(yearly.index):
            if yearly.loc[x] == -1:
                continue
            value = value_string(yearly.loc[x], decimals=1, is_percentage=True)
            location = 0.1
            if yearly.loc[x] > 0.5:
                location = -location
            ax.annotate(text=value, xy=(i, yearly.loc[x]), 
                        xytext=(i - 0.1, yearly.loc[x] + location), fontsize=20)
        ax.yaxis.set_major_formatter(mtick.PercentFormatter(1))
        ax.set_ylim([0, 1])
        
    def score_plot(score):
        """ Creates a bar plot and highlight the employee's score.
         
        """
        score_ = score[['performance']].sort_values(by='performance')
        score_[employee] = score_[score_.index == employee]
        score_.loc[employee, 'performance'] = float('nan')
        
        color = [metrics_colors['grey'], metrics_colors['red']]
        score_.plot.bar(stacked=True, legend=False, ax=ax, fontsize=20, grid=True, color=color)
        plt.title('Performance by Employee', fontsize=24, ha='center')
        plt.xticks([])
        plt.xlabel('')
        ax.yaxis.set_major_formatter(mtick.PercentFormatter(1))
        ax.set_ylim([0, 1])
    
    
    f = plt.figure(figsize=(29, 21))
    subplots = [22, 28]
    rowspan = [2, 2, 2, 2,
                  2, 2, 2,
               5, 6, 6, 
               3, 3, 3, 3, 5,  
               3, 3, 3, 3, 
               3, 3, 3, 3, 5,
               3, 3, 3, 3, 
              ]
    colspan = [12, 5, 5, 5,
                   5, 5, 5,
               12, 8, 8,
               3, 3, 3, 3, 13, 
               3, 3, 3, 3, 
               3, 3, 3, 3, 13,
               3, 3, 3, 3,             
              ]
    location = [(0, 1), (0, 13), (0, 18), (0, 23), 
                        (2, 13), (2, 18), (2, 23), 
                (4, 1), (4, 13), (4, 21),
                (9, 1), (9, 4), (9, 7), (9, 10), (10, 14), 
                (12, 1), (12, 4), (12, 7), (12, 10), 
                (15, 1), (15, 4), (15, 7), (15, 10), (16, 14), 
                (18, 1), (18, 4), (18, 7), (18, 10)]
  
    i = 0
    ax = plt.subplot2grid(shape=subplots, loc=location[i], colspan=colspan[i], rowspan=rowspan[i])
    ax.set_axis_off()    
    ax.text(0, 0, employee.capitalize(), size=50)
    ax.text(0, -0.5, 'Employee Performance Report - ' + str(year), size=30)
    
    for ii, label in enumerate(info.index):
        i = ii + 1
        ax = plt.subplot2grid(shape=subplots, loc=location[i], colspan=colspan[i], rowspan=rowspan[i])
        kpi_plot(
            value=info.loc[label], 
            label=label, 
            sizes=[24, 30], 
            ax=ax
        )
    
    i_gauge = [10, 15, 19, 24, 7]
    for i, label in zip(i_gauge, score.loc[employee].index):
        ax = plt.subplot2grid(shape=subplots, loc=location[i], colspan=colspan[i], rowspan=rowspan[i], projection='polar')
        gauge_plot(
            score.loc[employee, label], 
            label, 
            metrics_colors[label], 
            sizes=[35 + 5 * int(i == 7), 24], 
            decimals=int(i == 7)
        )
        
    i_kpi = [11, 12, 13, 16, 17, 18, 20, 21, 22, 25, 26, 27]
    for i, label in zip(i_kpi, kpi.index):
        ax = plt.subplot2grid(shape=subplots, loc=location[i], colspan=colspan[i], rowspan=rowspan[i])
        kpi_plot(
            value=kpi.loc[label], 
            label=label, 
            ax=ax, 
            decimals=2,
            is_percentage=metrics_is_percentage[label]
        )
    
    i = 23
    ax = plt.subplot2grid(shape=subplots, loc=location[i], colspan=colspan[i], rowspan=rowspan[i])
    score_plot(score)
    
    i = 14
    ax = plt.subplot2grid(shape=subplots, loc=location[i], colspan=colspan[i], rowspan=rowspan[i])
    yearly_plot(yearly)
        
    i_pie = [8, 9]
    titles = ['Time split', 'Time by project']
    for i, series, title in zip(i_pie, [time_split, by_project], titles):
        ax = plt.subplot2grid(shape=subplots, loc=location[i], colspan=colspan[i], rowspan=rowspan[i])
        pie_plot(series, title, ax, limit=6)
    
    f.tight_layout() 
    if save:
        plt.savefig(save + '.pdf', dpi=dpi)
        plt.close(f)
        
        
def data_to_plot(users_and_metrics, year, history):    
    """
    Extract the required information to create the employees' reports.

    Parameters
    ----------
    users_and_metrics : dict
        Dictionary containing the employees' performances information.
        Keys are the years and values the data frames containing the KPIs.
    year : int
        Year that defines the period of the report. 
    history : list
        List of years that defines the previous periods.
        
    Returns
    -------
    employees : list
        List of employees.
    info : pandas.DataFrame
        General information of employees (index): first date, last date,
        duration, #logs, #hours, #issues.
    kpi : pandas.DataFrame
        Performance KPIs of employees (index): velocity, engagement,
        independence, learning, versatility, complexity, sociability,
        participation, connection, management, guidance, responsibility.
    score : pandas.DataFrame
        Aggregated performance KPIs of employees (index): productivity,
        adaptability, teamwork, mentoring, performance.
    yearly : pandas.DataFrame
        Final performance KPI of employees (index) by year (columns).
    time_split : pandas.DataFrame
        Dedicated time split, leadership, collaboration, participation
        (columns), by employee (index).
    by_project : pandas.DataFrame
        Dedicated time split by employee (index) and project (columns).
    """    
    data = users_and_metrics[str(year)].dropna(how='all')
    employees = data.index
    
    metrics_dict = get_metrics_dict()
    score = data[list(metrics_dict.keys()) + ['performance']]

    yearly = [users_and_metrics[str(year)]['performance'].dropna().rename(str(year)) 
              for year in history]
    yearly.append(score['performance'].rename(str(year)))
    yearly = pd.concat(yearly, axis=1)

    columns = data.columns
    info_cols = ['min_date', 'max_date', 'duration', '#logs', '#hours', '#issues']
    time_split_cols = ['leading_time', 'collaboration_time', 'participation_time']
    by_project_cols = [x for x in columns if x[:8] == 'project_' and x[-5:] == '_time']
    by_issue_cols = [x for x in columns if x[:5] == 'type_' and x[-5:] == '_time']

    info = data[info_cols]
    info_rename = {'min_date': 'first date', 'max_date': 'last date'}
    info = info.rename(info_rename, axis=1)
    kpi = sum([cols for cols in metrics_dict.values()], [])
    kpi = data[kpi]
    time_split = data[time_split_cols]
    time_split_rename = {'collaboration_time': 'collaboration',
              'participation_time': 'participation',
              'leading_time': 'leadership'}
    time_split = time_split.rename(time_split_rename, axis=1)
    by_project = data[by_project_cols]
    by_project_rename = {x: x.replace('project_', '').replace('_time', '')
                         for x in by_project_cols}
    by_project = by_project.rename(by_project_rename, axis=1)
    
    return employees, info, kpi, score, yearly, time_split, by_project        