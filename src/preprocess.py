import warnings
warnings.filterwarnings("ignore")
import pandas as pd
import os
import datetime

from conventions import Read, Preprocess

def read_worklogs_files():
    """
    Reads the worklogs files information and drops duplicates.

    Returns
    -------
    worklogs : pandas.DataFrame
        Raw information contained in the worklogs files.

    See Also
    --------
    conventions
    """
    folder = Read.WORKLOG_FOLDER
    content = os.listdir(folder)

    files = [os.path.join(folder, x) 
             for x in content if os.path.isfile(os.path.join(folder, x))]
    data = {file: pd.read_excel(file, sheet_name=[Read.WORKLOG_SHEET_NAME, Read.DATES_SHEET_NAME])
            for file in files}
    
    intervals = []
    for file in files:
        people = data[file][Read.DATES_SHEET_NAME]
        dates = [col for col in people.columns if type(col) == datetime.datetime]
        people_dates = pd.Series(dates, index=dates, name=file)
        intervals.append(people_dates)
    intervals = pd.concat(intervals, axis=1)    
    
    to_load = pd.concat([intervals.idxmin(), intervals.idxmax()], 
                        axis=1, keys=['min_date', 'max_date'])
    to_load = to_load.sort_values(by=['max_date', 'min_date'])

    to_drop = [1]
    while len(to_drop) > 0:
        to_load['new_max_date'] = (to_load['min_date'].shift(-1) - pd.DateOffset(days=1)).fillna(to_load['max_date'].max())
        to_load['overlap'] = to_load['max_date'] - to_load['new_max_date']
        to_load['to_load'] = (to_load['new_max_date'] - to_load['min_date']).dt.days + 1
        to_drop = to_load[to_load['to_load'] <= 0].index
        to_load = to_load.drop(to_drop)
        
    worklogs = []
    for file in to_load.index:
        worklog = data[file][Read.WORKLOG_SHEET_NAME]
        worklog = worklog[worklog['Work date'] >= to_load.loc[file, 'min_date']]
        worklog = worklog[worklog['Work date'] <= to_load.loc[file, 'new_max_date']]
        
        to_drop = [x for x in worklog.columns if 'Unnamed' in x]
        worklog = worklog.drop(to_drop, axis=1)
        
        worklog = worklog.rename(Read.RENAME_STATUS, axis=1)
        
        to_drop = worklog[worklog['Work date'].isna()].index
        worklog = worklog.drop(to_drop)
        
        worklogs.append(worklog)
        
    worklogs = pd.concat(worklogs)    
    
    worklogs = worklogs.reset_index(drop=True)
    dtypes_ = {key: value for key, value in Read.DTYPES_FIELDS.items() if key in worklogs.columns}
    worklogs = worklogs.astype(dtypes_)
    
    return worklogs
                
    
def preprocess_worklogs(worklog):
    """
    Preprocesses raw worklogs: drops irrelevant, renames columns, transforms
    strings, replaces values, transforms dates, orders rows.

    Parameters
    ----------
    worklogs : pandas.DataFrame
        Raw information contained in the worklogs files.

    Returns
    -------
    worklogs : pandas.DataFrame
        Preprocessed worklogs.

    See Also
    --------
    conventions
    """
    # filter
    to_keep = ['Issue Key', 'Issue summary', 'Issue Type', 'Issue Status', 
               'Issue Original Estimate', 'Reporter', 'Project Key', 
               'Username', 'Work date', 'Hours']
    worklog = worklog[to_keep]
    
    # rename columns
    rename = {'Issue Key': 'issue', 
              'Issue summary': 'summary', 
              'Issue Type': 'type', 
              'Issue Status': 'status',
              'Issue Original Estimate': 'estimate', 
              'Reporter': 'reporter', 
              'Project Key': 'project', 
              'Username': 'user', 
              'Work date': 'date', 
              'Hours': '#hours'}
    worklog = worklog.rename(rename, axis=1)
    
    # lower string
    string_cols = [key for key, value in Read.DTYPES_FIELDS.items()
                   if value == 'string' and key in to_keep]
    for col in string_cols:
        worklog[rename[col]] = worklog[rename[col]].str.lower()
    
    # replacement
    worklog['type'] = worklog['type'].replace(Preprocess.TYPES_RENAME)
    worklog['user'] = worklog['user'].replace(Preprocess.USERS_RENAME)
    worklog['project'] = worklog['project'].replace(Preprocess.PROJECTS_RENAME)
    
    # drop
    to_drop = [x for x in worklog.index if worklog.loc[x, 'user'] in Preprocess.USERS_TO_DROP]
    to_drop += [x for x in worklog.index if worklog.loc[x, 'user'] in Preprocess.PROJECTS_TO_DROP]
    worklog = worklog.drop(to_drop)
    
    # date format
    worklog['date'] = worklog['date'].dt.date
    
    # order
    worklog = worklog.sort_values(by=['date', 'issue', 'user'])
    worklog = worklog.reset_index(drop=True)
    
    return worklog


