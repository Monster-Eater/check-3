"""Federal school book catalog for the Classes tab.

Book scans are not bundled: Federal Textbook Board/NBF retains the book
copyright. Each book record points students to NBF's official textbook
catalog/chapters, and to FBISE's current syllabus resources where applicable.
"""

NBF_CATALOG = 'https://www.nbf.org.pk/catalog'
NBF_CHAPTERS = 'https://www.nbf.org.pk/chapters-of-text-books'
FBISE_SYLLABUS = 'https://www.fbise.edu.pk/syllabus.php'
FBISE_SCHEME = 'https://www.fbise.edu.pk/Syllabus/Scheme_of_Studies_version1.pdf'
MOFEPT_CURRICULUM = 'https://www.mofept.gov.pk/Detail/NWJmMmM2YTQtM2YzYi00NjJkLTgzNDEtYzMxMTI4MTllY2Qw'


def _book(grade, subject, title=None, *, optional=False, medium='English/Urdu'):
    federal = grade >= 9
    return {
        'subject': subject,
        'title': title or f'{subject} — Class {grade}',
        'grade': grade,
        'publisher': 'National Book Foundation / Federal Textbook Board',
        'nature': 'Elective' if optional else 'Compulsory',
        'medium': medium,
        'textbook_url': NBF_CHAPTERS if not federal else NBF_CATALOG,
        'syllabus_url': FBISE_SYLLABUS if federal else MOFEPT_CURRICULUM,
        'scheme_url': FBISE_SCHEME,
    }


def _section(name, subjects, grade, optional=False):
    return {'name': name, 'books': [_book(grade, title, optional=optional) for title in subjects]}


PRIMARY = {
    1: ['Urdu-I', 'English-I', 'Mathematics-I', 'Islamiat-I / Religious Education-I',
        'Nazra Quran-I / Ethics-I', 'General Knowledge-I (English medium)', 'General Knowledge-I (Urdu medium)'],
    2: ['Urdu-II', 'English-II', 'Mathematics-II', 'Islamiat-II / Religious Education-II',
        'Nazra Quran-II / Ethics-II', 'General Knowledge-II (English medium)', 'General Knowledge-II (Urdu medium)'],
    3: ['Urdu-III', 'English-III', 'Mathematics-III', 'Islamiat-III / Religious Education-III',
        'Nazra Quran-III / Ethics-III', 'General Knowledge-III (English medium)', 'General Knowledge-III (Urdu medium)'],
    4: ['Urdu-IV', 'English-IV', 'Mathematics-IV', 'Islamiat-IV / Religious Education-IV',
        'Nazra Quran-IV / Ethics-IV', 'General Science-IV', 'Social Studies-IV (English medium)',
        'Social Studies-IV (Urdu medium)'],
    5: ['Urdu-V', 'English-V', 'Mathematics-V', 'Islamiat-V / Religious Education-V',
        'Nazra Quran-V / Ethics-V', 'General Science-V', 'Social Studies-V (English medium)',
        'Social Studies-V (Urdu medium)'],
}

MIDDLE = {
    6: ['Urdu-VI', 'English-VI', 'Mathematics-VI', 'Islamiat-VI / Religious Education-VI',
        'Translation of Holy Quran-VI / Ethics-VI', 'Science-VI', 'Geography-VI', 'History-VI',
        'Computer Science-VI', 'Arabic-VI', 'Home Economics-VI (English medium)',
        'Home Economics-VI (Urdu medium)', 'Drawing-VI'],
    7: ['Urdu-VII', 'English-VII', 'Mathematics-VII', 'Islamiat-VII / Religious Education-VII',
        'Translation of Holy Quran-VII / Ethics-VII', 'Science-VII', 'Geography-VII', 'History-VII',
        'Computer Science-VII', 'Arabic-VII', 'Home Economics-VII (English medium)',
        'Home Economics-VII (Urdu medium)', 'Drawing-VII'],
    8: ['Urdu-VIII', 'English-VIII', 'Mathematics-VIII', 'Islamiat-VIII / Religious Education-VIII',
        'Translation of Holy Quran-VIII / Ethics-VIII', 'Science-VIII', 'Geography-VIII', 'History-VIII',
        'Computer Science-VIII', 'Arabic-VIII', 'Home Economics-VIII (English medium)',
        'Home Economics-VIII (Urdu medium)', 'Drawing-VIII'],
}

# Current FBISE/NCC scheme families. Grade IX and X share a stream choice,
# while class-wise book records retain their own grade and official sources.
SSC_COMMON = [
    'English / Functional English', 'Urdu / Functional Urdu',
    'Islamiat / Religious Education (for minorities)',
    'Translation of Holy Quran / Ethics (for minorities)',
    'Regional Language (where applicable)',
]
SSC_ELECTIVES = [
    'Computer Science', 'Economics', 'Education', 'English Literature', 'Urdu Elective',
    'Islamic Studies', 'Islamic History', 'Geography', 'Health and Physical Education',
    'Home Economics', 'Art, Model Drawing and Fine Arts', 'Computer Graphics and Animation',
    'Entrepreneurship', 'Advertising', 'Food and Nutrition', 'Clothing and Textile',
    'Arabic', 'Chinese', 'Persian', 'French', 'Civics', 'Physiology and Hygiene',
]
MATRIC_TECH_TRADES = [
    'Fashion Designing', 'Graphic Designing and Media Production', 'Hospitality and Tourism Management',
    'HVACR', 'Industrial Electrician', 'IoT and Data Coding', 'Beautician and Cosmetology',
    'Professional Cooking and Chef', 'Plumbing and Solar Water Heating', 'Welding',
    'Wood Technology and Craftsmanship',
]
HSSC_ELECTIVES = [
    'Biology', 'Physics', 'Chemistry', 'Mathematics', 'Computer Science', 'Statistics',
    'Economics', 'Education', 'English Literature', 'Urdu Elective', 'Islamic Studies',
    'Islamic History', 'History of Muslim India', 'Islamic Culture', 'Sociology', 'Psychology',
    'Geography', 'Philosophy', 'Punjabi', 'Sindhi', 'Arabic', 'Chinese', 'French', 'Persian',
    'Computer Graphics and Animation', 'Entrepreneurship', 'Marketing', 'Event Management',
    'Human Resource Management', 'Computer Application', 'Automation and Robotics Technology',
    'Advertising', 'Health and Physical Education', 'Home Economics', 'Library Science',
]
HSSC_TRADES = [
    'Fashion Design and Construction', 'Graphic Design and Media Production',
    'Hospitality and Hotel Management', 'Tourism Management', 'IoT Advanced Solutions',
    'Cloud Computing Fundamentals', 'Beautician and Cosmetology', 'Professional Chef and Cooking',
    'HVACR', 'Industrial Electrician', 'Plumbing and Solar Water Heating',
    'Civil Construction and Technology',
]


def _class(grade, stage, sections):
    return {'grade': grade, 'name': f'Class {grade}', 'stage': stage, 'sections': sections}


def classes_catalog():
    classes = []
    for grade in range(1, 6):
        classes.append(_class(grade, 'Primary (Classes 1–5)', [
            _section('Federal compulsory books', PRIMARY[grade], grade),
        ]))
    for grade in range(6, 9):
        classes.append(_class(grade, 'Middle (Classes 6–8)', [
            _section('Federal compulsory books and available subjects', MIDDLE[grade], grade),
        ]))
    for grade in (9, 10):
        science = SSC_COMMON + ['Mathematics', 'Physics', 'Chemistry',
                                'Biology or Computer Science and Entrepreneurship']
        humanities = SSC_COMMON + ['Functional Mathematics', 'General Science'] + SSC_ELECTIVES
        technical = SSC_COMMON + ['Functional Mathematics', 'General Science'] + [f'{trade} (trade subjects)' for trade in MATRIC_TECH_TRADES] + SSC_ELECTIVES
        sections = [
            _section('Science Group', science, grade),
            _section('Humanities and Social Sciences', humanities, grade),
            _section('Matric-Tech and Technical Subjects', technical, grade),
        ]
        if grade == 10:
            sections.append(_section('Compulsory Pakistan Studies', ['Pakistan Studies-X'], grade))
        classes.append(_class(grade, 'Secondary (Classes 9–10)', sections))
    for grade in (11, 12):
        common = ['English / Functional English', 'Urdu / Functional Urdu',
                  'Islamiat / Religious Education (for minorities)',
                  'Translation of Holy Quran / Ethics (for minorities)']
        if grade == 12:
            common.append('Pakistan Studies')
        sections = [
            _section('Compulsory books', common, grade),
            _section('Pre-Medical', ['Biology', 'Physics', 'Chemistry'], grade),
            _section('Pre-Engineering', ['Mathematics', 'Physics', 'Chemistry'], grade),
            _section('General Science / Computer Science', ['Computer Science', 'Mathematics', 'Physics', 'Statistics', 'Economics'], grade),
            _section('Humanities and Social Sciences electives', HSSC_ELECTIVES, grade, optional=True),
            _section('Inter-Tech trade subjects', HSSC_TRADES, grade, optional=True),
        ]
        classes.append(_class(grade, 'Higher Secondary (Classes 11–12)', sections))
    return classes
