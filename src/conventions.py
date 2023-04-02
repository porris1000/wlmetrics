class Read:
    """
    Parameters to read the worklogs files.
    
    WORKLOG_FOLDER : folder from which time log files downloaded from Jira are
    read.
    WORKLOG_SHEET_NAME : name of the sheet in the file containing the time
    logs.
    DATES_SHEET_NAME : name of the sheet in the file containing the summary of
    time logs dates.
    RENAME_STATUS : dictionary to unify the names of issue status fields.
    DTYPES_FIELDS : dictionary to define the variable type of each field.

    """
    WORKLOG_FOLDER = '../data/timeUsers/'
    WORKLOG_SHEET_NAME = 'Worklogs'  
    DATES_SHEET_NAME = 'People'

    RENAME_STATUS = {
        'Issue tatus': 'Issue Status',
        'Issue Ttus': 'Issue Status'
    }

    DTYPES_FIELDS = {
        'Issue Key': "string",
        'Issue summary': "string",
        'Hours': "float",
        'Work date': "datetime64",
        'Username': "string",
        'Activity Name': "string",
        'Component': "string",
        'All Components': "string",
        'Version Name': "string",
        'Issue Type': "string",
        'Issue Status': "string",
        'Project Key': "string",
        'Epic': "string",
        'Epic Link': "string",
        'Work Description': "string",
        'Parent Key': "string",
        'Reporter': "string",
        'External Hours': "float",
        'Billed Hours': "float",
        'Issue Original Estimate': "float",
        'Issue Remaining Estimate': "float",
        'Full name': "string",
        'Project Name': "string",
        'Customer Reference': "string",
        'Project-Nr. (billable)': "string"
    }

    
class Preprocess:
    """
    Parameters to preprocess the worklogs files.
    
    USERS_RENAME : dictionary that allows you to rename users. It is useful if
    you need to unify two employees, in case the same person is registered
    with two names, for example, "rosario" and "charo".
    PROJECTS_RENAME : dictionary that allows you to rename projects. It is
    useful if you want to consider two projects as a single major project.
    TYPES_RENAME : dictionary that allows you to rename task types. It is
    useful if you want to consider two types as one.
    USERS_TO_DROP : users to be ignored in the study.
    PROJECTS_TO_DROP : projects to be ignored in the study.

    """
    USERS_RENAME = {}
    PROJECTS_RENAME = {
        'kiss': 'kis',
        'enexsm': 'enexsc',
        'enexss': 'enexsc',
        'juststa': 'justt',
        'justvdb': 'justvi'
    }
    TYPES_RENAME = {
        'fehler': 'bug'
    }
    
    USERS_TO_DROP = ['it', 'laura', 'monica']
    PROJECTS_TO_DROP = []
        
    
class Calculate:
    """
    Parameters to calculate employees' performance KPIs..
    
    ISSUES_LEADER_SHARE_LIMIT : percentage of dedication above which the issue
    is considered to be assigned to a particular employee. It must be greater
    than 0.5 to ensure that the task has a single assignee.
    PROJECTS_LEADER_SHARE_LIMIT : percentage of dedication from which the
    employee is considered to lead a project. In contrast to the issues, the
    project can have more than one leader.
    USERS_MIN_YEARLY_HOURS : minimum recorded time required to analyze
    employee performance. If it is less, it is ignored in the study.
    SUMMARY_MEETING_WORDS : list of words or word roots for the identification
    of issues related to meetings.
    SUMMARY_LEARNING_WORDS : list of words or word roots for the identification
    of issues related to learning and innovation.
    SUMMARY_MANAGEMENT_WORDS : list of words or word roots for the identification
    of issues related to work and team management.
    AGGREGATION_STD_LIMIT : number of standard deviations to shorten the
    standardized metrics.
    AGGREGATION_WEIGHTS :dictionary of weights by performance dimension to
    perform the aggregation into a single metric. The dictionary keys should
    be the 4 calculated dimensions (productivity, adaptability, teamwork,
    mentoring) and the values to their corresponding weight.
    
    """
    
    ISSUES_LEADER_SHARE_LIMIT = 0.7
    PROJECTS_LEADER_SHARE_LIMIT = 0.5
    
    USERS_MIN_YEARLY_HOURS = 3 * 22 * 8 # 3 months

    SUMMARY_MEETING_WORDS = ['meet', 'conversation', 'team building']
    SUMMARY_LEARNING_WORDS = ['learn', 'research', 'study', 'course']
    SUMMARY_MANAGEMENT_WORDS = ['organiz', 'coordinat', 'interview', 'train', 'education']
    
    
    SUMMARY_MEETING_WORDS = [x.lower() for x in SUMMARY_MEETING_WORDS]
    SUMMARY_LEARNING_WORDS = [x.lower() for x in SUMMARY_LEARNING_WORDS]
    SUMMARY_MANAGEMENT_WORDS = [x.lower() for x in SUMMARY_MANAGEMENT_WORDS]
    
    AGGREGATION_STD_LIMIT = 1
    AGGREGATION_WEIGHTS = {'productivity': 0.25,
                           'adaptability': 0.25,
                           'teamwork': 0.25,
                           'mentoring': 0.25
                          }
    
    
class Report:
    """
    Parameters to create employees' reports.
    
    IMAGES_FOLDER : folder in which employee reports are saved.

    """
    IMAGES_FOLDER = '../img/'