import pandas as pd
import numpy as np

from conventions import Calculate


def calculate_worklogs(worklogs):
    """
    Adds useful features to worklogs non depending on time period.

    Parameters
    ----------
    worklogs : pandas.DataFrame
        Preprocessed worklogs.

    Returns
    -------
    worklogs_calc : pandas.DataFrame
        Preprocessed worklogs including new calculated features from issues
        and projects.
    issues : pandas.DataFrame
        Issues features extracted from worklogs.
    projects : pandas.DataFrame
        Projects features extracted from worklogs.
    info : pandas.Series
        General information from the dataset.

    See Also
    --------
    extract_issues, extract_projects, conventions.py
    """
    issues = extract_issues(worklogs)
    
    projects = extract_projects(worklogs, issues)

    # issues & projects in worklogs
    wl_cols = ['issue', 'user', 'date', '#hours']
    worklogs_calc = worklogs[wl_cols]
    issues_rename = {x: 'issue_' + x for x in issues.columns}
    add = issues.rename(issues_rename, axis=1)
    worklogs_calc = worklogs_calc.merge(add,
                                        right_on='issue',
                                        left_on='issue',
                                        how='left')
    projects_rename = {x: 'project_' + x for x in projects.columns}
    add = projects.rename(projects_rename, axis=1)
    worklogs_calc = worklogs_calc.merge(add,
                                        right_on='project',
                                        left_on='issue_project',
                                        how='left')
    
    # new features for metrics calculation
    worklogs_calc['bug_time'] = worklogs_calc['#hours'] * worklogs_calc['issue_is_bug']
    worklogs_calc['learning_time'] = worklogs_calc['#hours'] * worklogs_calc['issue_is_learning']
    worklogs_calc['meeting_time'] = worklogs_calc['#hours'] * worklogs_calc['issue_is_meeting']
    worklogs_calc['managing_time'] = worklogs_calc['#hours'] * worklogs_calc['issue_is_management']
    worklogs_calc['collaboration_time'] = worklogs_calc['#hours'] * (
        (worklogs_calc['user'] != worklogs_calc['issue_leader']
        ) & ~worklogs_calc['issue_leader'].isna())
    worklogs_calc['participation_time'] = worklogs_calc['#hours'] * worklogs_calc['issue_leader'].isna()
    worklogs_calc['leading_time'] = worklogs_calc['#hours'] * (worklogs_calc['user'] == worklogs_calc['issue_leader'])
    
    info = {}
    info['min_date'] = worklogs_calc['date'].min()
    info['max_date'] = worklogs_calc['date'].max()
    info['#logs'] = worklogs_calc.shape[0]
    info['#issues'] = worklogs_calc['issue'].nunique()
    info['#projects'] = worklogs_calc['issue_project'].nunique()
    info['#users'] = worklogs_calc['user'].nunique()
    info = pd.Series(info) 
    print('------- Worklogs -------')
    print(info)

    return worklogs_calc, issues, projects, info


def calculate_users_interval(worklogs_calc, interval=None):
    """
    Calculates users features in a particular period of time.

    Parameters
    ----------
    worklogs_calc : pandas.DataFrame
        Preprocessed worklogs including issues and projects features.
    interval : list or None (default)
        List containing two dates to define the period of time. If None,
        the complete available period is considered.

    Returns
    -------
    users : pandas.DataFrame
        Large set of features extracted from worklogs by employee (index).

    See Also
    --------
    conventions
    """

    # interval 
    worklogs_interval = [worklogs_calc['date'].min(), worklogs_calc['date'].max()]
    if interval is None:
        interval = worklogs_interval
    else:
        interval = pd.to_datetime(interval)
        interval = [max(worklogs_interval[0], interval[0]), 
                    min(worklogs_interval[1], interval[1])]
    # filter dates
    worklogs_calc = worklogs_calc[(worklogs_calc['date'] >= interval[0]) &
                                  (worklogs_calc['date'] <= interval[1])]
    # set issues status
    worklogs_calc['issue_is_closed'] = worklogs_calc['issue_max_date'] <= interval[1]
    
    # extract users
    userscols = [x for x in worklogs_calc.columns
                 if 'issue' not in x and 'project_' not in x and x not in ['user', 'date']]
    group_user = worklogs_calc.groupby(['user'])
    users = group_user.sum()[userscols]
    # first day
    users['min_date'] = group_user.min()['date']
    # last day
    users['max_date'] = group_user.max()['date']
    # number of logs
    users['#logs'] = group_user.count()['#hours']
    # number of issues
    users['#issues'] = group_user.nunique()['issue']

    # user by date
    users_by_date = pd.pivot_table(worklogs_calc, 
                                   values='#hours',
                                   index=['user'],
                                   columns=['date'],
                                   aggfunc=np.sum) 
    # hours per user and day
    users['#daily_hours'] = users_by_date.mean(axis=1).round(0).clip(upper=8)
    # user duration in logs
    users['duration'] = (users['max_date'] - users['min_date']).dt.days + 1

    # expected working hours in period
    days = pd.bdate_range(start=interval[0], end=interval[1])
    days = pd.Series(1, index=days)
    users['#hours_total'] = [len(days.loc[users.loc[x, 'min_date']:users.loc[x, 'max_date']])
                             for x in users.index]
    users['#hours_total'] = users['#hours_total'] * users['#daily_hours']

    # leading issues
    group_issue_leader = worklogs_calc.groupby(['issue_leader'])
    group_issue_leader_issue = worklogs_calc.groupby(['issue_leader', 'issue']).last().groupby('issue_leader')
    # leading issues time
    users['leading_volume'] = group_issue_leader.sum()['#hours'].fillna(0)
    # needed help in leading issues
    users['helped_time'] = users['leading_volume'] - users['leading_time']
    # number of leading issues
    users['#leading_issues'] = group_issue_leader.nunique()['issue']
    # duration of leading issues
    users['leading_duration'] = group_issue_leader_issue.mean()['issue_duration'] * users['#daily_hours'] / 8
    
    # leading closed issues
    closed_issues = worklogs_calc[worklogs_calc['issue_is_closed']].index
    group_issue_leader_closed = worklogs_calc.loc[closed_issues].groupby(['issue_leader'])
    group_issue_leader_issue_closed = worklogs_calc.loc[closed_issues].groupby(['issue_leader', 'issue']).last().groupby('issue_leader')
    # leading closed issues time
    users['leading_closed_volume'] = group_issue_leader_closed.sum()['#hours'].fillna(0)
    # number of leading closed issues
    users['#leading_closed_issues'] = group_issue_leader_closed.nunique()['issue']
    # duration of leading closed issues
    users['leading_closed_duration'] = group_issue_leader_issue_closed.mean()['issue_duration'] * users['#daily_hours'] / 8
    
    # period by user to properly compute share calculations
    users_interval = [worklogs_calc[(worklogs_calc['date'] >= users.loc[user, 'min_date']) & 
                                (worklogs_calc['date'] <= users.loc[user, 'max_date'])].index 
                      for user in users.index]    
    
    # user as reporter
    reporting = worklogs_calc.groupby('issue_reporter').sum()['#hours']
    reporting = reporting.rename('reporting')
    # issues time as reporter
    users['reporting_volume'] = users.join(reporting)['reporting'].fillna(0)
    # share as reporter
    users['reporting_total_interval'] = [worklogs_calc.loc[x][~worklogs_calc.loc[x]['issue_reporter'].isna()]['#hours'].sum() 
                                         for x in users_interval]
    users['%reporting_volume'] = users['reporting_volume'] / users['reporting_total_interval']

    # number of helped users
    collaborated = (worklogs_calc['user'] != worklogs_calc['issue_leader']) & ~worklogs_calc['issue_leader'].isna()
    users['#helped_users'] = worklogs_calc[collaborated][['user', 'issue_leader']].groupby('user').nunique()
    users['#helped_users'] = users['#helped_users'].fillna(0)
    users['#users_total_interval'] = [worklogs_calc.loc[x]['user'].nunique() for x in users_interval]

    # users by project
    users_by_project = pd.pivot_table(worklogs_calc, 
                                      values='#hours', 
                                      index=['user'], 
                                      columns=['issue_project'], 
                                      aggfunc=np.sum)
    users_by_project = users_by_project.fillna(0)
    # dedication to projects std (in user interval)    
    projects_interval = [list(set(worklogs_calc.loc[x]['issue_project'].values)) for x in users_interval]
    users['projects_std'] = [users_by_project.loc[user, projects_interval[i]].std()  
                             for i, user in enumerate(users_by_project.index)]
    users['projects_std'] = users['projects_std'] / users['#hours']
    # shared by project (in user interval)
    dates_interval = [list(set(worklogs_calc.loc[x, 'date'])) for x in users_interval] 
    dates_by_project = pd.pivot_table(worklogs_calc, 
                                      values='#hours', 
                                      index=['date'], 
                                      columns=['issue_project'], 
                                      aggfunc=np.sum)
    project_contribution =  [users_by_project.loc[user] / dates_by_project.loc[dates].sum()
                             for user, dates in zip(users.index, dates_interval)]    
    users['#leading_projects'] = [(x > Calculate.PROJECTS_LEADER_SHARE_LIMIT).sum() for x in project_contribution]
    users['#leading_projects'] = users['#leading_projects'].fillna(0)
    users['%leading_projects'] = [users.loc[user, '#leading_projects'] / len(projects_interval[i])
                                  for i, user in enumerate(users.index)]    
    # dedication to projects
    rename_by_project = {col: 'project_' + col + '_time' for col in users_by_project.columns}
    users_by_project = users_by_project.rename(rename_by_project, axis=1)
    users_by_project = users_by_project
    users = users.join(users_by_project)
    
    # users by issue type
    users_by_type = pd.pivot_table(worklogs_calc, 
                                   values='#hours', 
                                   index=['user'], 
                                   columns=['issue_type'], 
                                   aggfunc=np.sum)
    users_by_type = users_by_type.fillna(0)
    # dedication to issues types std (in user interval)
    types_interval = [list(set(worklogs_calc.loc[x]['issue_type'].values))
                      for x in users_interval]
    users['types_std'] = [users_by_type.loc[user, types_interval[i]].std()  
                          for i, user in enumerate(users_by_type.index)]
    users['types_std'] = users['types_std'] / users['#hours']
    # share of bugs
    users['bugs_total_interval'] = [worklogs_calc.loc[x]['bug_time'].sum()
                                    for x in users_interval]
    users['%bug_time'] = users['bug_time'] / users['bugs_total_interval']
    # dedication to issues types
    rename_by_type = {col: 'type_' + col + '_time' for col in users_by_type.columns}
    users_by_type = users_by_type.rename(rename_by_type, axis=1)
    users_by_type = users_by_type
    users = users.join(users_by_type)    
    
    # ignore if #hours is too small
    ignore = users[users['#hours'] < Calculate.USERS_MIN_YEARLY_HOURS].index
    users = users.drop(ignore)
    
    return users


def calculate_metrics(users):
    """
    Calculates employee performance metrics (KPIs).

    Parameters
    ----------
    users : pandas.DataFrame
        Features extracted from worklogs by employee (index).

    Returns
    -------
    metrics : pandas.DataFrame
        KPIs derived from users by employee (index): velocity, concentration,
        engagement, independence, learning, versatility, heterogeneity,
        complexity, collaboration, sociability, participation, connection,
        management, guidance, responsibility.

    See Also
    --------
    calculate_users_interval, calculate_performance
    """
    velocity = users['#leading_closed_issues'] / (users['leading_closed_volume'] / 8)

    concentration = 1 / users['leading_closed_duration']
    
    engagement = users['#hours'] / users['#hours_total'] 
    
    independence = users['leading_time'] / users['leading_volume']
    
    learning = users['learning_time'] / users['#hours']
    
    versatility = 1 - users['projects_std']

    heterogeneity = 1 - users['types_std'] 
    
    complexity = users['%bug_time']
    
    collaboration = users['collaboration_time'] / users['#hours']
    
    sociability = users['#helped_users']  / (users['#users_total_interval'] - 1)

    participation = users['participation_time'] / users['#hours']

    connection = users['meeting_time'] / users['#hours']

    management = users['managing_time'] / users['#hours']

    guidance = users['%reporting_volume']    

    responsibility = users['%leading_projects']
    
    # metrics dataframe
    metrics = [velocity, concentration, engagement, independence]
    metrics += [learning, versatility, heterogeneity, complexity]
    metrics += [collaboration, sociability, participation, connection]
    metrics += [management, guidance, responsibility]
    
    keys = ['velocity', 'concentration', 'engagement', 'independence']
    keys += ['learning', 'versatility', 'heterogeneity', 'complexity']
    keys += ['collaboration', 'sociability', 'participation', 'connection']
    keys += ['management', 'guidance', 'responsibility']
    
    metrics = pd.concat(metrics, axis=1, keys=keys)    
    
    return metrics


def get_metrics_dict(final=True):
    """
    Returns the KPIs dictionary organized by dimension.

    Parameters
    ----------
    final : bool
        It indicates if including the complete set (False) or only the final
        selection of KPIs (True, default).

    Returns
    -------
    metrics_dict : dict
        Keys are the 4 dimensions and values the list of KPIs corresponding to
        the dimension.

    """
    metrics_dict = {'productivity': ['velocity', 'engagement', 'independence',],
                    'adaptability': ['learning', 'versatility', 'complexity',],
                    'teamwork': ['sociability', 'participation', 'connection',],
                    'mentoring': ['management', 'guidance', 'responsibility', ]
                   }
    if not final:
        metrics_dict['productivity'] = metrics_dict['productivity'] + ['concentration']
        metrics_dict['adaptability'] = metrics_dict['adaptability'] + ['heterogeneity']
        metrics_dict['teamwork'] = metrics_dict['teamwork'] + ['collaboration']
        
    return metrics_dict


def calculate_performance(metrics, limit=1):
    """
    Calculates employee performance aggregated metrics (KPIs).

    Parameters
    ----------
    metrics : pandas.DataFrame
        KPIs derived from users by employee (index): velocity, concentration,
        engagement, independence, learning, versatility, heterogeneity,
        complexity, collaboration, sociability, participation, connection,
        management, guidance, responsibility.

    Returns
    -------
    metrics : pandas.DataFrame
        Standardized input KPIs, aggregated KPIs by dimension and final
        performance KPI (mean).

    See Also
    --------
    calculate_metrics
    """
    metrics_dict = get_metrics_dict()
    
    metrics = (metrics - metrics.mean()) / metrics.std()
    metrics = metrics.clip(lower=-limit, upper=limit) 
    metrics = (metrics + limit) / (2 * limit)
    
    perf = {category: metrics[cols].mean(axis=1) for category, cols in metrics_dict.items()}
    perf = pd.DataFrame(perf)
    perf['performance'] = perf.mean(axis=1)
    
    return pd.concat([metrics, perf], axis=1)


def extract_issues(worklogs):
    """
    Extracts issues dataset from worklogs and adds useful features.

    Parameters
    ----------
    worklogs : pandas.DataFrame
        Preprocessed worklogs.

    Returns
    -------
    issues : pandas.DataFrame
        Features extracted from worklogs by issue (index).

    See Also
    --------
    calculate_worklogs, extract_projects, conventions.py
    """
    issue_cols = ['issue', 'summary', 'type', 'status', 
                  'estimate', 'reporter', 'project']
    issues = worklogs[issue_cols].groupby('issue').last()
    
    estimate = worklogs[['issue', 'estimate']].groupby('issue').max()['estimate']
    issues['estimate'] = estimate
    
    issues_by_user = pd.pivot_table(worklogs, 
                                    values='#hours', 
                                    index=['issue'], 
                                    columns=['user'], 
                                    aggfunc=np.sum)

    leader = issues_by_user.idxmax(axis=1)
    leader_share = issues_by_user.max(axis=1) / issues_by_user.sum(axis=1)
    issues['leader'] = [leader.loc[x] if leader_share.loc[x] > Calculate.ISSUES_LEADER_SHARE_LIMIT 
                        else None for x in leader.index]
    issues['%leader_share'] = leader_share

    issues['#participants'] = (issues_by_user > 0).sum(axis=1)
    issues['#hours'] = issues_by_user.sum(axis=1)
    issues['%share'] = issues['#hours'] / issues['#hours'].sum()
    
    issues['min_date'] = worklogs[['issue', 'date']].groupby('issue').min()
    issues['max_date'] = worklogs[['issue', 'date']].groupby('issue').max()
    issues['duration'] = (issues['max_date'] - issues['min_date']).dt.days + 1
    
    issues['is_bug'] = issues['type'] == 'bug'
    
    summaries = list(issues['summary'].values)
    is_meeting = []
    is_learning = []
    is_management = []
    for summary in summaries:
        meet = sum([meet_word in summary for meet_word in Calculate.SUMMARY_MEETING_WORDS])
        is_meeting.append(bool(meet))
        
        learn = sum([meet_word in summary for meet_word in Calculate.SUMMARY_LEARNING_WORDS])
        is_learning.append(bool(learn))
        
        management = sum([meet_word in summary for meet_word in Calculate.SUMMARY_MANAGEMENT_WORDS])
        is_management.append(bool(management))
        
    issues['is_meeting'] = is_meeting
    issues['is_learning'] = is_learning
    issues['is_management'] = is_management
    
    return issues


def extract_projects(worklogs, issues):
    """
    Extracts projects dataset from worklogs and adds useful features.

    Parameters
    ----------
    worklogs : pandas.DataFrame
       Preprocessed worklogs.

    Returns
    -------
    projects : pandas.DataFrame
       Features extracted from worklogs by project (index).

    See Also
    --------
    calculate_worklogs, extract_issues, conventions.py
    """
    projects = issues.groupby('project').count()[['summary']]
    projects = projects.rename({'summary': '#issues'}, axis=1)
    
    projects_by_user = pd.pivot_table(worklogs, 
                                      values='#hours', 
                                      index=['project'], 
                                      columns=['user'], 
                                      aggfunc=np.sum)
    
    leader = projects_by_user.idxmax(axis=1)
    leader_share = projects_by_user.max(axis=1) / projects_by_user.sum(axis=1)    
    projects['leader'] = [leader.loc[x] if leader_share.loc[x] > Calculate.PROJECTS_LEADER_SHARE_LIMIT 
                          else None for x in leader.index]
    projects['%leader_share'] = leader_share

    projects['#participants'] = (projects_by_user > 0).sum(axis=1)
    projects['#hours'] = projects_by_user.sum(axis=1)
    projects['%share'] = projects['#hours'] / projects['#hours'].sum()
    
    return projects
