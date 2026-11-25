LIVE = 'live'
COMING_SOON = 'coming_soon'
NEW_EDITION_AVAILABLE = 'new_edition_available'
DEPRECATED = 'deprecated'
RETIRED = 'retired'
UNLISTED = 'unlisted'
BOOK_STATES = (
    (LIVE, 'Live'),
    (COMING_SOON, 'Coming Soon'),
    (NEW_EDITION_AVAILABLE, 'New Edition Forthcoming (Show new edition correction schedule)'),
    (DEPRECATED, 'Deprecated (Disallow errata submissions and show deprecated schedule)'),
    (RETIRED, 'Retired (Remove from website)'),
    (UNLISTED, 'Unlisted (Not included in books sent to site)')
)

YELLOW = 'yellow'
LIGHT_BLUE = 'light_blue'
DARK_BLUE = 'dark_blue'
MIDNIGHT = 'midnight'
GREEN = 'green'
WHITE = 'white'
GREY = 'grey'
RED = 'red'
WHITE_RED = 'white_red'
WHITE_BLUE = 'white_blue'
GREEN_WHITE = 'green_white'
YELLOW_WHITE = 'yellow_white'
GREY_WHITE = 'grey_white'
WHITE_GREY = 'white_grey'
WHITE_ORANGE = 'white_orange'
BOOK_COVER_TEXT_COLOR = (
    (YELLOW, 'Yellow'),
    (LIGHT_BLUE, 'Light Blue'),
    (DARK_BLUE, 'Dark Blue'),
    (MIDNIGHT, 'Midnight'),
    (GREEN, 'Green'),
    (WHITE, 'White'),
    (GREY, 'Grey'),
    (RED, 'Red'),
    (WHITE_RED, 'White/Red'),
    (WHITE_BLUE, 'White/Blue'),
    (GREEN_WHITE, 'Green/White'),
    (YELLOW_WHITE, 'Yellow/White'),
    (GREY_WHITE, 'Grey/White'),
    (WHITE_GREY, 'White/Grey'),
    (WHITE_ORANGE, 'White/Orange'),
)

BLUE = 'blue'
MIDNIGHT = 'midnight'
DEEP_GREEN = 'deep-green'
GOLD = 'gold'
GRAY = 'gray'
GREEN = 'green'
LIGHT_BLUE = 'light-blue'
LIGHT_GRAY = 'light-gray'
MEDIUM_BLUE = 'medium-blue'
ORANGE = 'orange'
RED = 'red'
YELLOW = 'yellow'
RAISE_GREEN = 'raise-green'
COVER_COLORS = (
    (BLUE, 'Blue'),
    (MIDNIGHT, 'Midnight'),
    (DEEP_GREEN, 'Deep Green'),
    (GOLD, 'Gold'),
    (GRAY, 'Gray'),
    (GREEN, 'Green'),
    (LIGHT_BLUE, 'Light Blue'),
    (LIGHT_GRAY, 'Light Gray'),
    (MEDIUM_BLUE, 'Medium Blue'),
    (ORANGE, 'Orange'),
    (RED, 'Red'),
    (YELLOW, 'Yellow'),
    (RAISE_GREEN, 'Raise Green'),
)

MATH = 'Math'
SOCIAL_STUDIES = 'Social Studies'
SCIENCE = 'Science'
ENGLISH = 'English Language Areas & Reading'
CAREER_TECHNICAL = 'Career and Technical Education'
COLLEGE_READINESS = 'College Readiness'
FINE_ARTS = 'Fine Arts'
HEALTH = 'Health Education'
LANGUAGES = 'Languages other than English'
PHYSICAL_ED = 'Physical Education'
TECHNOLOGY_APPLICATIONS = 'Technology Applications'
OTHER = 'Other'
NONE = 'None'

K12_CATEGORIES = (
    (MATH, 'Math'),
    (SOCIAL_STUDIES, 'Social Studies'),
    (SCIENCE, 'Science'),
    (ENGLISH, 'English Language Areas & Reading'),
    (CAREER_TECHNICAL, 'Career and Technical Education'),
    (COLLEGE_READINESS, 'College Readiness'),
    (FINE_ARTS, 'Fine Arts'),
    (HEALTH, 'Health Education'),
    (LANGUAGES, 'Languages other than English'),
    (PHYSICAL_ED, 'Physical Education'),
    (TECHNOLOGY_APPLICATIONS, 'Technology Applications'),
    (OTHER, 'Other'),
    (NONE, 'None'),
)

# Accessibility remediation status, published on the Accessibility Hub. Blank
# means "not tracked" and keeps the row off the hub table entirely — the honest
# default for records nobody has assessed yet.
REMEDIATION_FIXED = 'fixed'
REMEDIATION_IN_PROGRESS = 'in_progress'
REMEDIATION_DEPRECATED = 'deprecated'
REMEDIATION_REMOVED = 'removed'
REMEDIATION_NA = 'na'
REMEDIATION_STATUSES = (
    (REMEDIATION_FIXED, 'Fixed (remediated)'),
    (REMEDIATION_IN_PROGRESS, 'In Progress (being remediated)'),
    (REMEDIATION_DEPRECATED, 'Deprecated (temporarily removed)'),
    (REMEDIATION_REMOVED, 'Removed (will not return)'),
    (REMEDIATION_NA, 'N/A (already accessible)'),
)
# Statuses the hub's "outstanding items" table shows. Fixed and N/A both mean
# "nothing to do", so only these read as outstanding.
REMEDIATION_OUTSTANDING = (
    REMEDIATION_IN_PROGRESS, REMEDIATION_DEPRECATED, REMEDIATION_REMOVED,
)

CC_BY_LICENSE_NAME = 'Creative Commons Attribution License'
CC_BY_LICENSE_VERSION = '4.0'
CC_BY_LICENSE_URL = 'https://creativecommons.org/licenses/by/4.0/'
CC_NC_SA_LICENSE_NAME = 'Creative Commons Attribution-NonCommercial-ShareAlike License'
CC_NC_SA_LICENSE_VERSION = '4.0'
CC_NC_SA_LICENSE_URL = 'https://creativecommons.org/licenses/by-nc-sa/4.0/'
