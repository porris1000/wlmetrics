class Read:
    """
    Parameters to read the worklogs files.

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
    
    
class Report:
    """
    Parameters to create employees' reports.

    """
    IMAGES_FOLDER = '../img/'