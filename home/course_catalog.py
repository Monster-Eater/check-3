"""Degree catalog and source links for the Flutter Courses tab.

Semester entries are taken from the official scheme linked on each program.
Elective courses can vary by campus, cohort, and student selection; those are
marked as electives rather than being presented as a fixed mandatory list.
"""

def _items(*titles):
    return [
        ({'title': item[0], 'code': item[1], 'credits': item[2], **({'topics': item[3]} if len(item) > 3 else {})}
         if isinstance(item, tuple) else {'title': item})
        for item in titles
    ]


PROGRAMS = [
    {
        'group': 'Computing & Information Technology', 'name': 'BS Computer Science',
        'university': 'University of the Punjab', 'session': 'Fall 2025 onwards',
        'source': 'https://pu.edu.pk/home/bos2_pro/267/160',
        'semesters': [
            {'number': 1, 'courses': _items('Functional English', 'Discrete Structures', 'Applied Physics', 'Probability & Statistics', 'Applications of Information and Communication Technologies', 'Math Deficiency I')},
            {'number': 2, 'courses': _items('Programming Fundamentals', 'Math Deficiency II', 'Programming Fundamentals Lab', 'Digital Logic Design', 'Digital Logic Design Lab', 'Linear Algebra', 'Expository Writing', 'Islamic Studies')},
            {'number': 3, 'courses': _items('Pakistan Studies', 'Object Oriented Programming', 'Object Oriented Programming Lab', 'Database Systems', 'Database Systems Lab', 'Computer Organization & Assembly Language', 'Calculus & Analytical Geometry', 'Introduction to Management', 'Fehm-e-Quran I')},
            {'number': 4, 'courses': _items('Software Engineering', 'Data Structures', 'Data Structures Lab', 'Computer Networks', 'Information Security', 'Advanced Database Management Systems', 'Fehm-e-Quran II')},
            {'number': 5, 'courses': _items('Artificial Intelligence', 'Artificial Intelligence Lab', 'Analysis of Algorithms', 'Theory of Automata and Formal Languages', 'Human Computer Interaction', 'Human Computer Interaction Lab', 'Computer Architecture', 'Computer Architecture Lab', 'Web Technologies', 'Web Technologies Lab', 'Tarjuma-e-Quran')},
            {'number': 6, 'courses': _items('Interdisciplinary elective', 'Interdisciplinary elective', 'Major elective', 'Major elective', 'Major elective', 'Tarjuma-e-Quran')},
            {'number': 7, 'courses': _items('Fieldwork / Internship', 'Major elective', 'Major elective', 'Major elective', 'Major elective', 'Tarjuma-e-Quran')},
            {'number': 8, 'courses': _items('Capstone Project', 'Major elective', 'Major elective', 'Major elective', 'Major elective', 'Tarjuma-e-Quran')},
        ],
    },
    {
        'group': 'Computing & Information Technology', 'name': 'BS Computer Science',
        'university': 'COMSATS University Islamabad', 'session': 'Spring 2022 onwards; verify campus offering',
        'source': 'https://lahore.comsats.edu.pk/cs/Files/BSCS-structure-SP22-Onwards.pdf',
        'semesters': [
            {'number': 1, 'courses': _items('Introduction to ICT', 'English Comprehension and Composition', 'Islamic Studies', 'Pakistan Studies', 'Applied Physics for Engineers', 'Mathematics I')},
            {'number': 2, 'courses': _items('Programming Fundamentals', 'Report Writing Skills', 'Digital Logic Design', 'Discrete Structures', 'Calculus I', 'University Elective 1')},
            {'number': 3, 'courses': _items('Object Oriented Programming', 'Software Engineering Concepts', 'Linear Algebra', 'Calculus and Analytic Geometry', 'University Elective 2')},
            {'number': 4, 'courses': _items('Data Structures and Algorithms', 'Computer Networks', 'Computer Organization and Assembly Language', 'Communication Skills', 'Computer Science Supporting Course 1')},
            {'number': 5, 'courses': _items('Database Systems', 'Principles of Operating Systems', 'Professional Practices', 'Statistics and Probability Theory', 'Computer Science Supporting Course 2', 'Computer Science Elective 1')},
            {'number': 6, 'courses': _items('Theory of Automata', 'Design and Analysis of Algorithms', 'Parallel and Distributed Computing', 'Information Security', 'Computer Science Electives 2 and 3')},
            {'number': 7, 'courses': _items('Compiler Construction', 'Artificial Intelligence', 'Senior Design Project I', 'Computer Science Supporting Course 3', 'Computer Science Elective 4')},
            {'number': 8, 'courses': _items('Senior Design Project II', 'University Electives 3 and 4', 'Computer Science Elective 5')},
        ],
    },
    {
        'group': 'Computing & Information Technology', 'name': 'BS Software Engineering',
        'university': 'COMSATS University Islamabad', 'session': 'Spring 2022 onwards; verify campus offering',
        'source': 'https://lahore.comsats.edu.pk/cs/Files/BSSE-structure-SP22-Onwards.pdf',
        'semesters': [
            {'number': 1, 'courses': _items('Introduction to ICT', 'English Comprehension and Composition', 'Islamic Studies', 'Pakistan Studies', 'Applied Physics for Engineers', 'Mathematics I')},
            {'number': 2, 'courses': _items('Programming Fundamentals', 'Report Writing Skills', 'Software Engineering Concepts', 'Discrete Structures', 'Calculus I', 'University Elective 1')},
            {'number': 3, 'courses': _items('Object Oriented Programming', 'Software Quality Engineering', 'Linear Algebra', 'Calculus and Analytic Geometry', 'University Elective 2')},
            {'number': 4, 'courses': _items('Data Structures and Algorithms', 'Computer Networks', 'Software Design and Architecture', 'Communication Skills', 'Statistics and Probability Theory')},
            {'number': 5, 'courses': _items('Database Systems', 'Principles of Operating Systems', 'Professional Practices', 'Software Requirement Engineering', 'Software Engineering Supporting Course 1', 'Software Engineering Elective 1')},
            {'number': 6, 'courses': _items('Software Construction and Development', 'Software Re-Engineering', 'Web Technologies', 'Information Security', 'Software Engineering Electives 2 and 3')},
            {'number': 7, 'courses': _items('Human Computer Interaction', 'Software Project Management', 'Senior Design Project I', 'Software Engineering Supporting Course 2', 'Software Engineering Elective 4')},
            {'number': 8, 'courses': _items('Senior Design Project II', 'University Electives 3 and 4', 'Software Engineering Supporting Course 3', 'Computer Science Elective 5')},
        ],
    },
    {
        'group': 'Computing & Information Technology', 'name': 'BS Software Engineering',
        'university': 'University of the Punjab', 'session': 'Current scheme on official program page',
        'source': 'https://pu.edu.pk/home/puac/bs/266/168',
        'semesters': [
            {'number': 1, 'courses': _items('Functional English', 'Programming Fundamentals Lab', 'Programming Fundamentals', 'Digital Logic Design', 'Digital Logic Design Lab', 'Discrete Structures', 'Applications of Information & Communication Technologies', 'Math Deficiency I')},
            {'number': 2, 'courses': _items('Ideology and Constitution of Pakistan', 'Object Oriented Programming Lab', 'Object Oriented Programming', 'Computer Organization and Assembly Language', 'Probability and Statistics', 'Expository Writing', 'Islamic Studies / Ethics', 'Math Deficiency II', 'Computer Organization and Assembly Language Lab')},
            {'number': 3, 'courses': _items('Software Engineering', 'Database Systems', 'Database Systems Lab', 'Data Structures', 'Data Structures Lab', 'Civics and Community Management', 'Applied Physics', 'Applied Physics Lab', 'Professional Practices', 'Fehm-e-Quran I')},
            {'number': 4, 'courses': _items('Calculus and Analytical Geometry', 'Artificial Intelligence', 'Operating Systems', 'Analysis of Algorithms', 'Software Requirement Engineering', 'Linear Algebra', 'Fehm-e-Quran II')},
            {'number': 5, 'courses': _items('Computer Networks', 'Computer Networks Lab', 'Software Design & Architecture', 'Web Technologies', 'Web Technologies Lab', 'Data Science', 'Data Science Lab', 'Multivariable Calculus', 'Introduction to Management', 'Tarjuma-e-Quran')},
            {'number': 6, 'courses': _items('Interdisciplinary elective 1', 'Interdisciplinary elective 2', 'Major elective 1', 'Major elective 2', 'Major elective 3', 'Tarjuma-e-Quran')},
            {'number': 7, 'courses': _items('Fieldwork / Internship', 'Major elective 4', 'Major elective 5', 'Major elective 6', 'Major elective 7', 'Tarjuma-e-Quran')},
            {'number': 8, 'courses': _items('Capstone Project', 'Major elective 8', 'Major elective 9', 'Major elective 10', 'Major elective 11', 'Tarjuma-e-Quran')},
        ],
    },
    {
        'group': 'Computing & Information Technology', 'name': 'BS Information Technology',
        'university': 'University of the Punjab', 'session': 'Official program scheme',
        'source': 'https://pu.edu.pk/home/bos2_pro/268/154', 'semesters': [
            {'number': 1, 'courses': _items(('Functional English', 'GENG-101', 3), ('Islamic Studies / Ethics', 'GISL-101 / GETH-101', 2), ('Digital Logic Design', 'CC-110', 2), ('Digital Logic Design Lab', 'CC-110L', 1), ('Applied Physics', 'GE-169', 3), ('Math Deficiency I', 'MD-001', 3), ('Applications of ICT', 'GE-160', 2), ('Applications of ICT Lab', 'GE-160L', 1), ('Pakistan Studies (Fall 2025 onwards; Fall 2024 cohort had Ideology and Constitution)', 'GPST-201 / GICP-1', 2))},
            {'number': 2, 'courses': _items(('Programming Fundamentals Lab', 'CC-112L', 1), ('Programming Fundamentals', 'CC-112', 3), ('Expository Writing', 'GENG-201', 3), ('Math Deficiency II', 'MD-002', 3), ('Computer Networks', 'CC-214', 2), ('Discrete Structures', 'GE-167', 3), ('Introduction to Marketing', 'UE-272', 3), ('Computer Networks Lab', 'CC-214L', 1))},
            {'number': 3, 'courses': _items(('Computer Organization and Assembly Language', 'CC-210', 2), ('Computer Organization and Assembly Language Lab', 'CC-210L', 1), ('Object Oriented Programming', 'CC-211', 3), ('Object Oriented Programming Lab', 'CC-211L', 1), ('Software Engineering', 'CC-212', 3), ('Database Systems', 'CC-215', 3), ('Database Systems Lab', 'CC-215L', 1), ('Calculus & Analytical Geometry', 'GE-162', 3), ('Pakistan Studies (Fall 2024 cohort only)', 'GPST-201', 2), ('Fehm-e-Quran I (Fall 2025 onwards)', 'HQ-003N', 1))},
            {'number': 4, 'courses': _items(('Data Structures', 'CC-213', 3), ('Data Structures Lab', 'CC-213L', 1), ('Operating Systems', 'CC-311', 2), ('Information Security', 'CC-312', 3), ('Introduction to Management', 'GE-192', 2), ('Probability and Statistics', 'MS-251', 3), ('Multivariable Calculus', 'MS-253', 3), ('Operating Systems Lab', 'CC-311L', 1), ('Fehm-e-Quran II (Fall 2025 onwards)', 'HQ-004N', 1))},
            {'number': 5, 'courses': _items(('Artificial Intelligence', 'CC-310', 2), ('Artificial Intelligence Lab', 'CC-310L', 1), ('Analysis of Algorithms', 'CC-313', 3), ('Parallel & Distributed Computing', 'DC-328', 2), ('Parallel & Distributed Computing Lab', 'DC-328L', 1), ('Web Technologies', 'DI-322', 2), ('Web Technologies Lab', 'DI-322L', 1), ('Linear Algebra', 'MS-252', 3), ('Professional Practices', 'GE-262', 2), ('Tarjuma-e-Quran', 'HQ-005', 0))},
            {'number': 6, 'courses': _items(('Interdisciplinary course 1', 'Interdisciplinary', 3), ('Interdisciplinary course 2', 'Interdisciplinary', 3), ('Major course 1', 'Major elective', 3), ('Major course 2', 'Major elective', 3), ('Major course 3', 'Major elective', 3), ('Tarjuma-e-Quran', 'HQ-006', 1))},
            {'number': 7, 'courses': _items(('Fieldwork / Internship', 'Major', 3), ('Major course 4', 'Major elective', 3), ('Major course 5', 'Major elective', 3), ('Major course 6', 'Major elective', 3), ('Major course 7', 'Major elective', 3), ('Tarjuma-e-Quran', 'HQ-007', 0))},
            {'number': 8, 'courses': _items(('Capstone Project', 'Major', 3), ('Major course 8', 'Major elective', 3), ('Major course 9', 'Major elective', 3), ('Major course 10', 'Major elective', 3), ('Major course 11', 'Major elective', 3), ('Tarjuma-e-Quran', 'HQ-008', 1))},
        ],
    },
    {
        'group': 'Computing & Information Technology', 'name': 'BS Data Science',
        'university': 'University of the Punjab', 'session': 'Official program scheme',
        'source': 'https://pu.edu.pk/home/bos2_pro/269/170', 'semesters': [
            {'number': 1, 'courses': _items(('Functional English', 'GENG-101', 3), ('Islamic Studies / Ethics', 'GISL-101 / GETH-101', 2), ('Ideology and Constitution of Pakistan', 'GICP-101', 2), ('Programming Fundamentals Lab', 'CC-112L', 1), ('Programming Fundamentals', 'CC-112', 3), ('Applications of ICT', 'GE-160A', 3), ('Math Deficiency I', 'MD-001', 0))},
            {'number': 2, 'courses': _items(('Digital Logic Design', 'CC-110', 2), ('Digital Logic Design Lab', 'CC-110L', 1), ('Object Oriented Programming', 'CC-211N', 3), ('Object Oriented Programming Lab', 'CC-211L', 1), ('Applied Physics', 'GE-169', 3), ('Expository Writing', 'GENG-201', 3), ('Probability and Statistics', 'MS-251N1', 3), ('Math Deficiency II', 'MD-002N', 0))},
            {'number': 3, 'courses': _items(('Computer Organization and Assembly Language Programming', 'CC-210', 2), ('Computer Organization and Assembly Language Programming Lab', 'CC-210L', 1), ('Data Structures', 'CC-213', 3), ('Data Structures Lab', 'CC-213L', 1), ('Introduction to Data Science', 'DD-221', 2), ('Introduction to Data Science Lab', 'DD-221L', 1), ('Calculus and Analytical Geometry', 'GE-162', 3), ('Discrete Structures', 'GE-167', 3), ('Linear Algebra', 'MS-252', 3), ('Pakistan Studies', 'GPST-201', 2), ('Fehm-e-Quran I', 'HQ-003N', 1))},
            {'number': 4, 'courses': _items(('General Social Science', 'GEN(SS)', 3), ('Quantitative Reasoning II', 'GQR-201', 3), ('Major course 1', 'Major elective', 3), ('Major course 2', 'Major elective', 3), ('Major course 3', 'Major elective', 3), ('Fehm-e-Quran II', 'HQ-004N', 1))},
            {'number': 5, 'courses': _items(('Interdisciplinary course 1', 'Interdisciplinary', 3), ('Interdisciplinary course 2', 'Interdisciplinary', 3), ('Major course 4', 'Major elective', 3), ('Major course 5', 'Major elective', 3), ('Major course 6', 'Major elective', 3), ('Tarjuma-e-Quran', 'HQ-005', 0))},
            {'number': 6, 'courses': _items(('Interdisciplinary course 3', 'Interdisciplinary', 3), ('Interdisciplinary course 4', 'Interdisciplinary', 3), ('Major course 7', 'Major elective', 3), ('Major course 8', 'Major elective', 3), ('Major course 9', 'Major elective', 3), ('Tarjuma-e-Quran', 'HQ-006', 1))},
            {'number': 7, 'courses': _items(('Fieldwork / Internship', 'Major', 3), ('Major course 10', 'Major elective', 3), ('Major course 11', 'Major elective', 3), ('Major course 12', 'Major elective', 3), ('Major course 13', 'Major elective', 3), ('Tarjuma-e-Quran', 'HQ-007', 0))},
            {'number': 8, 'courses': _items(('Capstone Project', 'Major', 3), ('Major course 14', 'Major elective', 3), ('Major course 15', 'Major elective', 3), ('Major course 16', 'Major elective', 3), ('Major course 17', 'Major elective', 3), ('Tarjuma-e-Quran', 'HQ-008', 1))},
        ],
    },
    {
        'group': 'Computing & Information Technology', 'name': 'BS Cyber Security',
        'university': 'Air University, Karachi Campus', 'session': 'Official scheme published by the university',
        'source': 'https://khi.au.edu.pk/Pages/Faculties/FCAI/documents/BSCYS_programDescription.pdf', 'semesters': [
            {'number': 1, 'courses': _items(('Functional English', 'EL170', 3), ('Introduction to Cyber Security', 'CY102', 2), ('Introduction to Cyber Security Lab', 'CY102L', 1), ('Applications of ICT', 'CS181', 2), ('Applications of ICT Lab', 'CS181L', 1), ('Programming Fundamentals', 'CS111', 3), ('Programming Fundamentals Lab', 'CS111L', 1), ('Islamic Studies and Ethics', 'HU124', 2), ('Discrete Structures', 'MA216', 3), ('Foundational Mathematics (premedical students; non-credit)', 'MA114', 0))},
            {'number': 2, 'courses': _items(('Introduction to Software Engineering', 'SE101', 3), ('Object Oriented Programming', 'CS112', 3), ('Object Oriented Programming Lab', 'CS112L', 1), ('Digital Logic Design', 'EE123', 2), ('Digital Logic Design Lab', 'EE123L', 1), ('Applied Physics', 'PH111', 2), ('Applied Physics Lab', 'PH111L', 1), ('Linear Algebra', 'MA201', 3), ('Pre-Calculus (premedical students; non-credit)', 'MA118', 0))},
            {'number': 3, 'courses': _items(('Information Assurance', 'CY371', 3), ('Computer Networks', 'CS260', 2), ('Computer Networks Lab', 'CS260L', 1), ('Data Structures', 'CS216', 3), ('Data Structures Lab', 'CS216L', 1), ('Calculus and Analytical Geometry', 'MA110', 3), ('Computer Organization and Assembly Language', 'CS226', 2), ('Computer Organization and Assembly Language Lab', 'CS226L', 1), ('Social Science Elective', 'SSXXX', 2))},
            {'number': 4, 'courses': _items(('Operating Systems', 'CS325', 2), ('Operating Systems Lab', 'CS325L', 1), ('Secure Software Design and Development', 'CY256', 2), ('Secure Software Design and Development Lab', 'CY256L', 1), ('Network Security', 'CY223', 3), ('Network Security Lab', 'CY223L', 1), ('Cyber Security Elective I', 'CYXXX', 2), ('Cyber Security Elective I Lab', 'CYXXXL', 1), ('Multivariable Calculus', 'MA105', 3))},
            {'label': 'Summer Internship', 'number': 4, 'courses': _items(('Internship (6–8 weeks)', 'CY490', 3))},
            {'number': 5, 'courses': _items(('Digital Forensics', 'CY334', 2), ('Digital Forensics Lab', 'CY334L', 1), ('Parallel and Distributed Computing', 'CS426', 2), ('Parallel and Distributed Computing Lab', 'CS426L', 1), ('Expository Writing', 'EL271', 3), ('Artificial Intelligence', 'CS344', 2), ('Artificial Intelligence Lab', 'CS344L', 1), ('Cyber Security Elective II', 'CYXXX', 2), ('Cyber Security Elective II Lab', 'CYXXXL', 1), ('Civics and Community Engagement', 'HU411', 2))},
            {'number': 6, 'courses': _items(('Database Systems', 'CS130', 3), ('Database Systems Lab', 'CS130L', 1), ('Cyber Security Elective III', 'CYXXX', 2), ('Cyber Security Elective III Lab', 'CYXXXL', 1), ('Cyber Security Elective IV', 'CYXXX', 2), ('Cyber Security Elective IV Lab', 'CYXXXL', 1), ('Technical and Business Writing', 'EL400', 3), ('Entrepreneurship', 'BA353', 2), ('Final Year Project I', 'CY491', 1))},
            {'number': 7, 'courses': _items(('Probability and Statistics', 'MA301', 3), ('Supporting Elective', 'XXXXX', 3), ('Design and Analysis of Algorithms', 'CS332', 3), ('Cyber Security Elective V', 'CYXXX', 2), ('Cyber Security Elective V Lab', 'CYXXXL', 1), ('Cyber Security Elective VI', 'CYXXX', 2), ('Cyber Security Elective VI Lab', 'CYXXXL', 1), ('Final Year Project II', 'CY492', 2))},
            {'number': 8, 'courses': _items(('Professional Practices', 'CS470', 2), ('Cyber Security Elective VII', 'CYXXX', 2), ('Cyber Security Elective VII Lab', 'CYXXXL', 1), ('Ideology and Constitution of Pakistan', 'HU405', 2), ('Information Security', 'CS215', 2), ('Information Security Lab', 'CS215L', 1), ('Final Year Project III', 'CY493', 3))},
        ],
    },
    {
        'group': 'Engineering & Life Sciences', 'name': 'BSc Electrical Engineering',
        'university': 'University of Engineering and Technology Lahore', 'session': '2024 onwards',
        'source': 'https://nwl.uet.edu.pk/wp-content/uploads/2024/11/EE-Curriculum-2024.pdf',
        'semesters': [
            {'number': 1, 'courses': _items('Mechanics and Wave Motion', 'Electric Circuits', 'Workshop Practice', 'Islamic Studies / Ethics I', 'Calculus and Analytic Geometry', 'Introduction of Computer Programming for Data Science')},
            {'number': 2, 'courses': _items('Electricity and Magnetism', 'Differential Equations', 'Circuit Analysis and Design', 'Programming Fundamentals', 'Communication Skills', 'Translation of the Holy Quran I')},
            {'number': 3, 'courses': _items('Electric Machinery Fundamentals', 'Electronic Devices and Circuits', 'Civics and Community Engagement', 'Linear Algebra', 'Data Structures and Algorithms', 'Numerical Analysis')},
            {'number': 4, 'courses': _items('Digital Systems', 'Signals and Systems', 'Applied Probability', 'Technical Writing & Presentation Skills', 'Anthropology / Psychology / Social Work elective', 'Translation of the Holy Quran II', 'Occupational Health and Safety')},
            {'number': 5, 'courses': _items('Core Breadth Elective 1', 'Electromagnetics and its Applications', 'Principles of Management', 'Microprocessor Systems', 'Artificial Intelligence')},
            {'number': 6, 'courses': _items('Core Breadth Elective 2', 'Core Depth Elective 1', 'Analog & Digital Communications', 'Control Systems', 'Embedded Systems Laboratory', 'Translation of the Holy Quran III')},
            {'number': 7, 'courses': _items('Core Depth Electives 2 and 3', 'Ideology and Constitution of Pakistan / Ethics II', 'Project Phase I', 'Internship')},
            {'number': 8, 'courses': _items('Core Depth Electives 4 and 5', 'Entrepreneurship', 'Project Phase II', 'Translation of the Holy Quran IV')},
        ],
    },
    {
        'group': 'Engineering & Life Sciences', 'name': 'BS Biotechnology', 'university': 'University of the Punjab', 'session': 'Official program scheme',
        'source': 'https://pu.edu.pk/home/puac/bs/246/108', 'semesters': [
            {'number': 1, 'courses': _items(('Botany (Theory + Practical)', 'NBOT-110', 3), ('Functional English', 'GENG-101', 3), ('Civics and Community Engagement', 'GCCE-101', 2), ('Islamic Studies / Ethics', 'GISL-101 / GETH-101', 2), ('Elements of Biotechnology', 'BT-101', 3), ('Cell Biology (Theory + Practical)', 'BCBT-101', 3))},
            {'number': 2, 'courses': _items(('Introduction to the Topics of The Qur’an', 'AISL-100', 2), ('Quantitative Reasoning I', 'GQR-101', 3), ('Entrepreneurship', 'GENT-101', 2), ('Ideology and Constitution of Pakistan', 'GICP-101', 2), ('Biochemistry I', 'BT-102', 3), ('Principles of Genetics', 'BCBT-102', 3), ('Biosafety, Biosecurity & Bioethics', 'BT-104', 2))},
            {'number': 3, 'courses': _items(('Applications of ICT', 'GICT-201', 3), ('Expository Writing', 'GENG-201', 3), ('Agriculture Biotechnology', 'BT-201', 3), ('Microbiology', 'BCBT-203', 2), ('Molecular Biology', 'BCBT-201', 3), ('Pakistan Studies', 'GPST-201', 2), ('Microbiology Lab', 'BCBT-203L', 1), ('Fehm-e-Quran I', 'HQ-003N', 1))},
            {'number': 4, 'courses': _items(('General Social Science', 'GEN(SS)', 2), ('Quantitative Reasoning II', 'GQR-201', 3), ('Industrial Biotechnology', 'BT-206', 3), ('Health Biotechnology', 'BT-204', 3), ('Recombinant DNA Technology', 'BT-202', 3), ('Internship', 'BT-200', 3), ('Fehm-e-Quran II', 'HQ-004N', 1))},
            {'number': 5, 'courses': _items(('Bioinformatics', 'BCBT-303', 3), ('Ecology and Biodiversity', 'Interdisciplinary', 3), ('Biostatistics', 'BCBT-301', 3), ('Biochemistry II', 'BT-305', 3), ('Analytical Chemistry & Instrumentation', 'BT-301', 3), ('Tarjuma-e-Quran', 'HQ-005', 0))},
            {'number': 6, 'courses': _items(('Biophysics', 'Interdisciplinary', 3), ('Principles of Biochemical Engineering', 'BT-306', 3), ('Methods in Molecular Biology', 'BT-304', 3), ('Immunology', 'BCBT-302', 3), ('Genomics & Proteomics', 'BT-302', 3), ('Tarjuma-e-Quran', 'HQ-006', 1))},
            {'number': 7, 'courses': _items(('Environmental Biotechnology', 'BT-407', 3), ('Artificial Intelligence in Biotechnology', 'BT-405', 2), ('Scientific Inquiry and Research Methods', 'BCBT-401', 3), ('Microbial Biotechnology', 'BT-401', 3), ('Capstone', 'BT-480', 3), ('Elective Course I', 'Major elective', 3), ('Tarjuma-e-Quran', 'HQ-007', 0))},
            {'number': 8, 'courses': _items(('Nanobiotechnology', 'BT-404', 3), ('Food Biotechnology', 'BT-402', 3), ('Elective Course II', 'Major elective', 3), ('Elective Course III', 'Major elective', 3), ('Elective Course IV', 'Major elective', 3), ('Tarjuma-e-Quran', 'HQ-008', 1))},
        ],
    },
    {
        'group': 'Engineering & Life Sciences', 'name': 'BS Biochemistry', 'university': 'University of the Punjab', 'session': 'Official program scheme',
        'source': 'https://pu.edu.pk/home/puac/bs/246/112', 'semesters': [
            {'number': 1, 'courses': _items(('General Natural Science', 'GEN(NS)', 3), ('Functional English', 'GENG-101', 3), ('Civics and Community Engagement', 'GCCE-101', 2), ('Islamic Studies / Ethics', 'GISL-101 / GETH-101', 2), ('Cell Biology', 'BCBT-101', 3), ('Introduction to Biochemistry', 'BC-101', 3))},
            {'number': 2, 'courses': _items(('General Arts & Humanities', 'GEN(AH)', 2), ('Quantitative Reasoning I', 'GQR-101', 3), ('Entrepreneurship', 'GENT-101', 2), ('Ideology and Constitution of Pakistan', 'GICP-101', 2), ('Principles of Genetics', 'BCBT-102', 3), ('Elements of Biotechnology', 'BT-101', 3))},
            {'number': 3, 'courses': _items(('Applications of ICT', 'GICT-201', 3), ('Expository Writing', 'GENG-201', 3), ('Nutritional Biochemistry', 'BC-203', 2), ('Microbiology', 'BCBT-203', 2), ('Carbohydrates and Lipids', 'BC-201', 2), ('Organic Chemistry', 'Interdisciplinary', 3), ('Pakistan Studies', 'GPST-201', 2), ('Carbohydrates and Lipids Lab', 'BC-201L', 1), ('Nutritional Biochemistry Lab', 'BC-203L', 1), ('Microbiology Lab', 'BCBT-203L', 1), ('Fehm-e-Quran I', 'HQ-003N', 1))},
            {'number': 4, 'courses': _items(('General Social Science', 'GEN(SS)', 2), ('Quantitative Reasoning II', 'GQR-201', 3), ('Molecular Biology', 'BCBT-201', 3), ('Enzymology', 'BC-204', 3), ('Proteins and Nucleic Acids', 'BC-202', 3), ('Fehm-e-Quran II', 'HQ-004N', 1))},
            {'number': 5, 'courses': _items(('Human Physiology', 'BC-303', 3), ('Clinical Biochemistry', 'BC-301', 3), ('Biostatistics', 'BCBT-301', 3), ('Methods in Molecular Biology', 'BC-307', 3), ('Analytical Chemistry', 'Interdisciplinary', 3), ('Tarjuma-e-Quran', 'HQ-005', 0), ('Metabolism I', 'BC-305', 2))},
            {'number': 6, 'courses': _items(('Industrial Biochemistry', 'BC-306', 3), ('Inorganic Chemistry', 'Interdisciplinary', 3), ('Bioenergetics', 'BC-304', 3), ('Metabolism II', 'BC-302', 2), ('Immunology', 'BCBT-302', 3), ('Tarjuma-e-Quran', 'HQ-006', 1), ('Plant Biochemistry', 'BC-308', 3))},
            {'number': 7, 'courses': _items(('Capstone', 'BC-480', 3), ('Biomembranes and Cell Signaling', 'BC-405', 3), ('Scientific Inquiry & Research Methods', 'BCBT-401', 3), ('Biochemical Techniques', 'BC-403', 3), ('Environmental Biochemistry', 'BC-401', 3), ('Tarjuma-e-Quran', 'HQ-007', 0), ('Elective Course I', 'Major elective', 3))},
            {'number': 8, 'courses': _items(('Capstone Project', 'BSBC-', 0), ('Biosafety, Biosecurity & Bioethics', 'BC-402', 2), ('Elective Course II', 'Major elective', 3), ('Elective Course III', 'Major elective', 3), ('Elective Course IV', 'Major elective', 3), ('Tarjuma-e-Quran', 'HQ-008', 1), ('Internship', 'BC-400', 3))},
        ],
    },
    {
        'group': 'Engineering & Life Sciences', 'name': 'BS Botany', 'university': 'University of the Punjab', 'session': 'Official program scheme',
        'source': 'https://pu.edu.pk/home/bos2_pro/197/105', 'semesters': [
            {'number': 1, 'courses': _items(('Functional English', 'GENG-101', 3), ('Civics and Community Engagement', 'GCCE-101', 2), ('Islamic Studies / Ethics', 'GISL-101 / GETH-101', 2), ('Diversity of Plants (Theory)', 'BOT-112', 2), ('Cell Biology (Theory)', 'BOT-110', 2), ('General Zoology', 'NB-107', 3), ('Cell Biology (Lab)', 'BOT-110L', 1), ('Diversity of Plants (Lab)', 'BOT-112L', 1))},
            {'number': 2, 'courses': _items(('Basic Arabic Language', 'AARB-122', 2), ('Quantitative Reasoning I', 'GQR-101', 3), ('Entrepreneurship', 'GENT-101', 2), ('Ideology and Constitution of Pakistan', 'GICP-101', 2), ('Fundamentals of Genetics and Evolution (Theory)', 'BOT-118', 2), ('Fundamentals of Plant Taxonomy (Theory)', 'BOT-114', 2), ('Fundamentals of Genetics and Evolution (Lab)', 'BOT-118L', 1), ('Fundamentals of Plant Taxonomy (Lab)', 'BOT-114L', 1), ('Biodiversity and Conservation (Theory)', 'BOT-116', 2), ('Biodiversity and Conservation (Lab)', 'BOT-116L', 1))},
            {'number': 3, 'courses': _items(('Applications of ICT', 'GICT-201', 3), ('Expository Writing', 'GENG-201', 3), ('Pakistan Studies', 'GPST-201', 2), ('Phycology & Bryology (Theory)', 'BOT-201', 2), ('Phycology & Bryology (Lab)', 'BOT-201L', 1), ('Mycology (Theory)', 'BOT-203', 2), ('Mycology (Lab)', 'BOT-203L', 1), ('Plant Anatomy and Embryology (Theory)', 'BOT-205', 2), ('Plant Anatomy and Embryology (Lab)', 'BOT-205L', 1), ('Fehm-e-Quran I', 'HQ-003N', 1))},
            {'number': 4, 'courses': _items(('General Social Science', 'GEN(SS)', 2), ('Phytogeography (Theory)', 'BOT-207', 2), ('Phytogeography (Lab)', 'BOT-207L', 1), ('Principles of Plant Ecology (Theory)', 'BOT-209', 2), ('Principles of Plant Ecology (Lab)', 'BOT-209L', 1), ('Principles of Plant Biochemistry (Theory)', 'BOT-211', 2), ('Principles of Plant Biochemistry (Lab)', 'BOT-211L', 1), ('Principles of Plant Physiology (Theory)', 'BOT-213', 2), ('Principles of Plant Physiology (Lab)', 'BOT-213L', 1), ('Quantitative Reasoning II', 'GQR-201', 3), ('Fehm-e-Quran II', 'HQ-004N', 1))},
            {'number': 5, 'courses': _items(('Advanced Plant Ecology (Theory)', 'BOT-301', 2), ('Advanced Plant Ecology (Lab)', 'BOT-301L', 1), ('Advanced Plant Biochemistry (Theory)', 'BOT-303', 2), ('Advanced Plant Biochemistry (Lab)', 'BOT-303L', 1), ('Advanced Plant Physiology (Theory)', 'BOT-305', 2), ('Advanced Plant Physiology (Lab)', 'BOT-305L', 1), ('Plant Microbe Interactions (Theory)', 'BOT-307', 2), ('Plant Microbe Interactions (Lab)', 'BOT-307L', 1), ('Pteridophytes and Gymnosperms (Theory)', 'BOT-309', 2), ('Pteridophytes and Gymnosperms (Lab)', 'BOT-309L', 1), ('Biostatistics (Theory)', 'BOT-311', 2), ('Biostatistics (Lab)', 'BOT-311L', 1), ('Tarjuma-e-Quran', 'HQ-005', 0))},
            {'number': 6, 'courses': _items(('Systematics of Angiosperms (Theory)', 'BOT-313', 2), ('Systematics of Angiosperms (Lab)', 'BOT-313L', 1), ('Plant Pathology (Theory)', 'BOT-315', 2), ('Plant Pathology (Lab)', 'BOT-315L', 1), ('Molecular Genetics (Theory)', 'BOT-317', 2), ('Molecular Genetics (Lab)', 'BOT-317L', 1), ('Sustainable Development Goals', 'BOT-319', 3), ('Artificial Intelligence in Botany', 'BOT-320', 3), ('Tarjuma-e-Quran', 'HQ-006', 1))},
            {'number': 7, 'courses': _items(('Analytical Techniques in Botany (Theory)', 'BOT-401', 2), ('Analytical Techniques in Botany (Lab)', 'BOT-401L', 1), ('Major course (title not specified on official scheme)', 'BOT-403', 2), ('Major course lab (title not specified on official scheme)', 'BOT-403L', 1), ('Forensic Botany (Theory)', 'BOT-405', 2), ('Forensic Botany (Lab)', 'BOT-405L', 1), ('Scientific Inquiry and Research Methods (Theory)', 'BOT-407', 2), ('Scientific Inquiry and Research Methods (Lab)', 'BOT-407L', 1), ('Tarjuma-e-Quran', 'HQ-007', 0))},
            {'number': 8, 'courses': _items(('Plant Biotechnology (Theory)', 'BOT-409', 2), ('Plant Biotechnology (Lab)', 'BOT-409L', 1), ('Economic and Industrial Botany', 'BOT-411', 3), ('Evolutionary Trends in Plants (Theory)', 'BOT-413', 2), ('Evolutionary Trends in Plants (Lab)', 'BOT-413L', 1), ('Capstone Project', 'BOT-415', 3), ('Comprehensive Viva-Voce', 'BOT-417 / BOT-419', 1), ('Tarjuma-e-Quran', 'HQ-008', 1))},
        ],
    },
    {
        'group': 'Engineering & Life Sciences', 'name': 'BS Chemistry', 'university': 'University of the Punjab', 'session': 'Official program scheme',
        'source': 'https://pu.edu.pk/home/bos2_pro/237/140', 'semesters': [
            {'number': 1, 'courses': _items(('Functional English', 'GENG-101', 3), ('Civics and Community Engagement', 'GCCE-101', 2), ('Islamic Studies / Ethics', 'GISL-101 / GETH-101', 2), ('Fundamental Concepts of Chemical Bonding', 'CHEM-116', 2), ('Physical Chemistry I', 'CHEM-101', 2), ('Science Wonders Around Us', 'NSW-106', 3), ('Fundamental Concepts of Chemical Bonding Lab', 'CHEM-117', 1), ('Physical Chemistry I Lab', 'CHEM-102', 1))},
            {'number': 2, 'courses': _items(('World History', 'AHIS-122', 2), ('Quantitative Reasoning I', 'GQR-101', 3), ('Entrepreneurship', 'GENT-101', 2), ('Ideology and Constitution of Pakistan', 'GICP-101', 2), ('Basic Organic Chemistry', 'CHEM-131', 2), ('Physical Chemistry II: Thermodynamics', 'CHEM-103', 3), ('Organic Chemistry Lab', 'CHEM-132', 1))},
            {'number': 3, 'courses': _items(('Applications of ICT', 'GICT-201', 3), ('Pakistan Studies', 'GPST-201', 2), ('Expository Writing', 'GENG-201', 3), ('Metallurgical Aspects of Inorganic Compounds', 'CHEM-216', 3), ('Reaction Mechanism', 'CHEM-231', 3), ('Choose one: Analytical Chemistry + lab (CHEM-246/CHEM246L); Water Treatment and Cleansers + lab (CHEM-261/CHEM261L); Introductory Biochemistry + lab (CHEM-276/CHEM276L); Green Chemistry + lab (CHEM-291/CHEM291L)'), ('Fehm-e-Quran I', 'HQ-003N', 1))},
            {'number': 4, 'courses': _items(('General Social Science', 'GEN(SS)', 2), ('Quantitative Reasoning II', 'GQR-201', 3), ('Chemical Kinetics', 'CHEM-201', 2), ('Physical Chemistry Lab', 'CHEM-202', 1), ('Chemistry of F-Block Elements', 'CHEM-217', 2), ('Inorganic Chemistry Lab', 'CHEM-218', 1), ('Stereochemistry', 'CHEM-232', 2), ('Organic Chemistry Lab', 'CHEM-233', 1), ('Fehm-e-Quran II', 'HQ-004N', 1))},
            {'number': 5, 'courses': _items(('Electrochemistry', 'CHEM-301', 2), ('Physical Chemistry Lab', 'CHEM-302', 1), ('UV & IR Spectroscopy', 'CHEM-331', 2), ('Organic Chemistry Lab', 'CHEM-332', 1), ('Choose one specialization option: Chromatographic Techniques-I + lab; Unit Operations and Basic Chemical Industries + lab; Carbohydrate + lab; Introduction to Green Solvents + lab'), ('Calculus I', 'MPHY-101', 3), ('Cell Biology + lab', 'ZOOL-103 / ZOOL-104', 3), ('Tarjuma-e-Quran', 'HQ-005', 0))},
            {'number': 6, 'courses': _items(('Introduction to Spectral and Separation Techniques', 'CHEM-350', 3), ('Analytical Separation Tools-I Lab', 'CHEM-348/349', 3), ('Coordination Chemistry Lab', 'CHEM-316/317', 3), ('Unit Processes and Raw Materials Lab', 'CHEM-363/364', 3), ('Allied Chemical Industries', 'CHEM-365', 3), ('Protein Lab', 'CHEM-378/379', 3), ('Immunology', 'CHEM-380', 3), ('Applications of Green Solvents Lab', 'CHEM-393/394', 3), ('Green Chemistry and Sustainable Development Goals', 'CHEM-395', 3), ('Waves and Optics', 'MPHY-112', 3), ('Fundamentals of Genetics and Evolution + lab', 'BOT-118 / BOT-119', 3), ('Tarjuma-e-Quran', 'HQ-006', 1))},
            {'number': 7, 'courses': _items(('Fieldwork / Internship', 'CHEM-400', 3), ('Choose one 12-credit specialization: Organic / Inorganic / Physical / Analytical / Applied / Bio Chemistry', 'Specialization', 12), ('Tarjuma-e-Quran', 'HQ-007', 0))},
            {'number': 8, 'courses': _items(('Capstone Project', 'CHEM-499', 3), ('Choose one 12-credit specialization: Analytical / Organic / Inorganic / Physical / Applied / Bio Chemistry', 'Specialization', 12), ('Tarjuma-e-Quran', 'HQ-008', 1))},
        ],
    },
    {
        'group': 'Social & Behavioral Sciences', 'name': 'BS Criminology', 'university': 'University of the Punjab', 'session': 'Official program scheme',
        'source': 'https://pu.edu.pk/home/bos2_pro/259/85', 'semesters': [
            {'number': 1, 'courses': _items(('General Natural Science', 'GEN(NS)', 3), ('Functional English', 'GENG-101', 3), ('Civics and Community Engagement', 'GCCE-101', 2), ('Islamic Studies / Ethics', 'GISL-101 / GETH-101', 2), ('Introduction to Sociology', 'CRM-106', 3), ('Introduction to Criminology & Security Studies', 'CRM-105', 3), ('Tarjuma-e-Quran', 'HQ-001', 0))},
            {'number': 2, 'courses': _items(('General Arts & Humanities', 'GEN(AH)', 2), ('Quantitative Reasoning I', 'GQR-101', 3), ('Entrepreneurship', 'GENT-101', 2), ('Ideology and Constitution of Pakistan', 'GICP-101', 2), ('Sociology of Deviance', 'CRM-113', 3), ('Social Problems of Pakistan', 'CRM-112', 3), ('Tarjuma-e-Quran', 'HQ-002', 1))},
            {'number': 3, 'courses': _items(('Applications of ICT', 'GICT-201', 3), ('Expository Writing', 'GENG-201', 3), ('Juvenile Delinquency', 'CRM-205', 3), ('Theoretical Perspectives on Crime and Criminals', 'CRM-204', 3), ('Mass Media & Crime', 'CRM-203', 3), ('Tarjuma-e-Quran', 'HQ-003', 0), ('Pakistan Studies', 'GPST-201', 2))},
            {'number': 4, 'courses': _items(('General Social Science', 'GEN(SS)', 2), ('Quantitative Reasoning II', 'GQR-201', 3), ('Applied Criminology', 'CRM-211', 3), ('Introduction to Social Research', 'CRM-210', 3), ('Criminal Psychology', 'CRM-209', 3), ('Tarjuma-e-Quran', 'HQ-004', 1))},
            {'number': 5, 'courses': _items(('Political Science', 'CRM-302', 3), ('Social Work', 'CRM-301', 3), ('Correctional Institutions (listed as “Correlational Institutions” on page)', 'CRM-305', 3), ('Quantitative Research Methods', 'CRM-304', 3), ('Criminal Justice System', 'CRM-303', 3), ('Tarjuma-e-Quran', 'HQ-005', 0))},
            {'number': 6, 'courses': _items(('Introduction to Law', 'CRM-308', 3), ('Introduction to Demography', 'CRM-307', 3), ('Forensic Criminology', 'CRM-311', 3), ('Islamic Perspective on Crime and Punishment', 'CRM-310', 3), ('Qualitative Research Methods', 'CRM-309', 3), ('Tarjuma-e-Quran', 'HQ-006', 1))},
            {'number': 7, 'courses': _items(('Fieldwork / Internship', 'CRM-401', 3), ('Procedure of Evidence in Criminal Law', 'CRM-406', 3), ('Peace & Conflict Resolution', 'CRM-405', 3), ('Crime & Security', 'CRM-404', 3), ('Victimology', 'CRM-403', 3), ('Tarjuma-e-Quran', 'HQ-007', 0), ('Capstone Project', 'CRM-402', 3))},
            {'number': 8, 'courses': _items(('Research Thesis', 'CRM-409', 6), ('Major course (title not specified on official scheme)', 'Unspecified', None), ('Violence & Terrorism', 'CRM-411', 3), ('Human Rights and Citizenship', 'CRM-410', 3), ('Community Justice & Crime Prevention', 'CRM-408', 3), ('Tarjuma-e-Quran', 'HQ-008', 1))},
        ],
    },
    {
        'group': 'Social & Behavioral Sciences', 'name': 'BS Communication Studies', 'university': 'University of the Punjab', 'session': 'Official program scheme',
        'source': 'https://pu.edu.pk/home/puac/bs/251/114', 'semesters': [
            {'number': 1, 'courses': _items(('Functional English', 'GENG-101', 3), ('Civics and Community Engagement', 'GCCE-101', 2), ('Islamic Studies / Ethics', 'GISL-101 / GETH-101', 2), ('Media History', 'BSCS-102', 3), ('Introduction to Media and Mass Communication', 'BSCS-101', 3), ('Introduction to Environmental Science', 'GIES-201', 3))},
            {'number': 2, 'courses': _items(('Fundamentals of Philosophy', 'AHPH-100', 2), ('Quantitative Reasoning I', 'GQR-101', 3), ('Entrepreneurship', 'GENT-101', 2), ('Ideology and Constitution of Pakistan', 'GICP-101', 2), ('Media Ethics and Laws', 'BSCS-104', 3), ('Communication Skills', 'BSCS-103', 3))},
            {'number': 3, 'courses': _items(('Applications of ICT', 'GICT-201', 3), ('Expository Writing', 'GENG-201', 3), ('Mobile Journalism', 'BSCS-203', 3), ('Visual Communication I', 'BSCS-202', 3), ('News Reporting (Research and Practice)', 'BSCS-201', 3), ('Pakistan Studies', 'GPST-201', 2), ('Fehm-e-Quran I', 'HQ-003N', 1))},
            {'number': 4, 'courses': _items(('General Social Science', 'GEN(SS)', 2), ('Quantitative Reasoning II', 'GQR-201', 3), ('Communication for Development', 'BSCS-206', 3), ('Visual Communication II', 'BSCS-205', 3), ('Creative Content Writing', 'BSCS-204', 3), ('Fehm-e-Quran II', 'HQ-004N', 1))},
            {'number': 5, 'courses': _items(('Origins of Democracy and Democratic Institutionalism: Philosophical Approaches', 'PS-111', 3), ('Introduction to Geopolitics: Global and Regional', 'PS-202', 3), ('Research Methods I', 'BSCS-303', 3), ('Theories of Communication I', 'BSCS-302', 3), ('International Communication', 'BSCS-301', 3), ('Tarjuma-e-Quran', 'HQ-005', 0))},
            {'number': 6, 'courses': _items(('Politics of Developing World: Concept and Methods', 'PS-201', 3), ('Voting Elections: Campaign and Media', 'PS-251', 3), ('Research Method II', 'BSCS-306', 3), ('Theories of Communication II', 'BSCS-305', 3), ('Professional Editing', 'BSCS-304', 3), ('Tarjuma-e-Quran', 'HQ-006', 1))},
            {'number': 7, 'courses': _items(('Fieldwork / Internship', 'FEI-401', 3), ('Media Seminar', 'BSCS-404', 3), ('Data Journalism', 'BSCS-403', 3), ('Entertainment Communication', 'BSCS-402', 3), ('Research Methods III (Tools and Analysis Skills)', 'BSCS-401', 3), ('Tarjuma-e-Quran', 'HQ-007', 0))},
            {'number': 8, 'courses': _items(('Capstone Project / Thesis', 'BSCS-405', 3), ('Major course (title not specified on official scheme)', 'Unspecified', 3), ('Writing for Research', 'BSCS-408', 3), ('Health Communication', 'BSCS-407', 3), ('Data Analysis Techniques', 'BSCS-406', 3), ('Tarjuma-e-Quran', 'HQ-008', 1))},
        ],
    },
    {
        'group': 'Social & Behavioral Sciences', 'name': 'BS Sociology', 'university': 'University of the Punjab', 'session': 'Official program scheme',
        'source': 'https://pu.edu.pk/home/puac/bs/259/68', 'semesters': [
            {'number': 1, 'courses': _items(('Functional English', 'GENG-101', 3), ('Civics and Community Engagement', 'GCCE-101', 2), ('Islamic Studies / Ethics', 'GISL-101 / GETH-101', 2), ('Cultural Anthropology', 'SOC-102', 3), ('Sociology I', 'SOC-101', 3), ('Fundamentals of Disaster Management', 'NDM-120', 3))},
            {'number': 2, 'courses': _items(('Logic and Critical Thinking', 'APHL-111', 2), ('Quantitative Reasoning I', 'GQR-101', 3), ('Entrepreneurship', 'GENT-101', 2), ('Ideology and Constitution of Pakistan', 'GICP-101', 2), ('Development of Social Thought', 'SOC-104', 3), ('Sociology II', 'SOC-103', 3))},
            {'number': 3, 'courses': _items(('Applications of ICT', 'GICT-201', 3), ('Expository Writing', 'GENG-201', 3), ('Social Psychology', 'SOC-203', 3), ('Classical Sociological Theory', 'SOC-202', 3), ('Pakistani Society & Culture', 'SOC-201', 3), ('Sociology of Education', 'SOC-204', 3), ('Pakistan Studies', 'GPST-201', 2), ('Fehm-e-Quran I', 'HQ-003N', 1))},
            {'number': 4, 'courses': _items(('General Social Science', 'GEN(SS)', 2), ('Quantitative Reasoning II', 'GQR-201', 3), ('Introduction to Social Research', 'SOC-207', 3), ('Contemporary Social Theory', 'SOC-206', 3), ('Sociology of Development', 'SOC-205', 3), ('Fehm-e-Quran II', 'HQ-004N', 1))},
            {'number': 5, 'courses': _items(('Social Work', 'SOC-305', 3), ('Gender Studies', 'SOC-304', 3), ('Social Statistics I', 'SOC-303', 3), ('Quantitative Research', 'SOC-302', 3), ('Sociology of Globalization', 'SOC-301', 3), ('Tarjuma-e-Quran', 'HQ-005', 0))},
            {'number': 6, 'courses': _items(('Introduction to Criminology', 'SOC-307', 3), ('Project Planning and Management', 'SOC-306', 3), ('Social Statistics II', 'SOC-311', 3), ('Urban Sociology', 'SOC-310', 3), ('Qualitative Research', 'SOC-309', 3), ('Tarjuma-e-Quran', 'HQ-006', 1), ('Political Science', 'SOC-308', 3))},
            {'number': 7, 'courses': _items(('Fieldwork / Internship', 'SOC-405', 3), ('Sociology of Law and Human Rights', 'SOC-404', 3), ('Sociology of Health & Illness', 'SOC-403', 3), ('Migration and Society', 'SOC-402', 3), ('Management of Resettlement & Rehabilitation', 'SOC-401', 3), ('Tarjuma-e-Quran', 'HQ-007', 0), ('Capstone Project', 'SOC-406', 3))},
            {'number': 8, 'courses': _items(('Major elective (title not specified on official scheme)', 'Unspecified', None), ('Major elective (title not specified on official scheme)', 'Unspecified', None), ('Thesis', 'SOC-409', 6), ('Governance & Social Policy', 'SOC-408', 3), ('Clinical Sociology', 'SOC-407', 3), ('Tarjuma-e-Quran', 'HQ-008', 1))},
        ],
    },
    {
        'group': 'Social & Behavioral Sciences', 'name': 'BS Applied Psychology', 'university': 'University of the Punjab', 'session': 'Official program scheme',
        'source': 'https://pu.edu.pk/home/puac/bs/221/137', 'semesters': [
            {'number': 1, 'courses': _items(('Functional English', 'GENG-101', 3), ('Civics and Community Engagement', 'GCCE-101', 2), ('Islamic Studies / Ethics', 'GISL-101 / GETH-101', 2), ('Applied Areas of Psychology', 'APSY-112', 2), ('Introduction to Psychology', 'APSY-111', 3), ('Practicals in Psychology', 'APSY-113', 1), ('What is Science?', 'NHPY-110', 3))},
            {'number': 2, 'courses': _items(('Fundamentals of Philosophy', 'AHPH-100', 2), ('Quantitative Reasoning I', 'GQR-101', 3), ('Entrepreneurship', 'GENT-101', 2), ('Ideology and Constitution of Pakistan', 'GICP-101', 2), ('Cognitive Psychology', 'APSY-122', 3), ('Legal & Ethical Issues in Psychology', 'APSY-121', 3))},
            {'number': 3, 'courses': _items(('Applications of ICT', 'GICT-201', 3), ('Expository Writing', 'GENG-201', 3), ('Cross Cultural Psychology', 'APSY-233', 3), ('Environmental Psychology', 'APSY-232', 3), ('Schools & Perspective in Psychology', 'APSY-231', 3), ('Pakistan Studies', 'GPST-201', 2), ('Fehm-e-Quran I', 'HQ-003N', 1))},
            {'number': 4, 'courses': _items(('General Social Science', 'GEN(SS)', 2), ('Quantitative Reasoning II', 'GQR-201', 3), ('Introduction to Social Psychology', 'APSY-243', 3), ('Health Psychology', 'APSY-242', 3), ('Gender Issues in Psychology', 'APSY-241', 3), ('Fehm-e-Quran II', 'HQ-004N', 1))},
            {'number': 5, 'courses': _items(('Psychological Assessment Practical', 'APSY-353', 1), ('Psychological Assessment', 'APSY-352', 3), ('Research Method I', 'APSY-351', 3), ('Statistics in Psychology', 'APSY-354', 3), ('Fields of Practice in Social Work', 'FSW-203', 3), ('Introduction to Public Relations', 'PRAD-105', 3), ('Tarjuma-e-Quran', 'HQ-005', 1))},
            {'number': 6, 'courses': _items(('Introduction to Human Resource Management', 'BBA-112', 3), ('Socio-Cultural Aspects of Gender', 'GS-104', 3), ('Psychopathology', 'APSY-363', 3), ('Quantitative Data Analysis', 'APSY-362', 3), ('Research Method II', 'APSY-361', 3), ('Tarjuma-e-Quran', 'HQ-006', 1))},
            {'number': 7, 'courses': _items(('Capstone Project', 'APSY-485', 3), ('Lab Experiments', 'APSY-474', 1), ('Biological Basis of Behavior', 'APSY-475', 3), ('Biological Basis of Behavior Practical', 'APSY-476', 1), ('Developmental Psychology', 'APSY-477', 3), ('Tarjuma-e-Quran', 'HQ-007', 0), ('Experimental Psychology', 'APSY-473', 2), ('Areas of Specialization I', 'APSY-472', 3), ('Field Work / Case Report / Internship I', 'APSY-471', 3))},
            {'number': 8, 'courses': _items(('Capstone Project', 'APSY-485', 3), ('Positive Psychology', 'APSY-484', 3), ('Peace Psychology', 'APSY-483', 3), ('Areas of Specialization II', 'APSY-482', 3), ('Field Work / Case Report / Internship II', 'APSY-481', 3), ('Tarjuma-e-Quran', 'HQ-008', 1))},
        ],
    },
]


# Short, paraphrased topic outlines from official university course documents.
# Other entries retain the program's source page until its subject outline is
# added here; the app makes that official source accessible from the subject.
OFFICIAL_OUTLINES = {
    'GENG-101': {
        'url': 'https://pu.edu.pk/document/merit/exam/GENG-101%20Functional%20English.pdf',
        'topics': ['Vocabulary and word formation', 'Grammar and sentence construction', 'Pronunciation and sound production', 'Reading comprehension and interpretation', 'Purpose, audience, tone, and context', 'Listening and reading strategies', 'Clear and inclusive communication', 'Presentations and public speaking', 'Professional emails, reports, and letters'],
    },
    'CC-112': {
        'url': 'https://pu.edu.pk/document/merit/exam/1738648017BS%20Computer%20Science%20CC-112.pdf',
        'topics': ['Problem-solving steps, algorithms, pseudocode, and flowcharts', 'C program structure, data types, variables, input, and output', 'Operators, expressions, decisions, and loops', 'Functions, scope, recursion, and argument passing', 'Arrays, multidimensional data, pointers, strings, and character handling', 'Structures, unions, enums, and bit operations', 'Sequential and random-access files', 'Preprocessor, command-line arguments, and multi-file programs', 'Dynamic memory, linked lists, algorithm efficiency, and sorting'],
    },
    'MD-002': {
        'url': 'https://pu.edu.pk/document/merit/exam/1738647612BS%20Computer%20Science%202nd%20Semester%20MD-002.pdf',
        'topics': ['Complex-number operations and polar form', 'Sequences, arithmetic and geometric series', 'Permutations, combinations, probability, and binomial theorem', 'Limits and continuity', 'Rates of change and differentiation rules', 'Derivative applications: extrema and curve behavior', 'Area, definite and indefinite integrals, and substitution'],
    },
    'GE-167': {
        'url': 'https://pu.edu.pk/document/merit/exam/1728544664GE-167.pdf',
        'topics': ['Propositional and predicate logic', 'Proof strategies and mathematical induction', 'Sets, functions, mappings, and relations', 'Counting, permutations, combinations, and probability', 'Divisibility, primes, and modular arithmetic', 'Recurrence relations and sequences', 'Graph theory, paths, coloring, and trees'],
    },
    'GE-169': {
        'url': 'https://pu.edu.pk/document/merit/exam/1728544802GE-169.pdf',
        'topics': ['Electric charge, electric force, and electric fields', 'Electric flux and Gauss law applications', 'Electric potential, current, resistance, and Ohm law', 'Magnetic force, magnetic fields, and Ampere law', 'Electromagnetic induction and Faraday law', 'Wave optics: reflection, refraction, interference, and diffraction', 'Polarization of electromagnetic waves'],
    },
    'CC-211': {
        'url': 'https://pu.edu.pk/document/merit/exam/1751539215CC-211.pdf',
        'topics': ['Object-oriented analysis and design fundamentals', 'Classes, objects, encapsulation, constructors, and destructors', 'Function and class templates, arrays, vectors, and const members', 'Composition, aggregation, friend and static members', 'Copy constructors and operator overloading', 'Streams, serialization, and file input/output', 'Inheritance, polymorphism, and virtual functions', 'Exception handling and generic programming', 'Standard-library containers, iterators, and lambda expressions'],
    },
    'CC-212': {
        'url': 'https://pu.edu.pk/document/merit/exam/1770889102CC-212%20Software%20Engineering.pdf',
        'topics': ['Software engineering foundations and process models', 'Agile development methods', 'Project management and requirements engineering', 'System analysis and context, interaction, structure, and behavior models', 'Data, architecture, component, and interface design', 'Object-oriented analysis, UML, and use cases', 'Software testing and quality assurance', 'Design patterns, software evolution, and configuration management', 'Process improvement'],
    },
    'CC-213': {
        'url': 'https://pu.edu.pk/document/merit/exam/1770889119CC-213%20Data%20Structures.pdf',
        'topics': ['Algorithm properties, performance, and Big-O analysis', 'Abstract data types, arrays, and sparse matrices', 'Stacks, queues, recursion, and divide-and-conquer', 'Dynamic allocation and linked-list variants', 'Trees, binary-search trees, balanced trees, and heaps', 'Searching, indexing, and hashing', 'Sorting methods', 'Graph representations, traversals, spanning trees, and shortest paths'],
    },
    'CC-214': {
        'url': 'https://pu.edu.pk/document/merit/exam/1770889167CC-214%20Computer%20Networks.pdf',
        'topics': ['Networking concepts, protocol architecture, and topologies', 'Physical and data-link layers and media-access methods', 'Circuit and packet switching; LAN and wireless networks', 'MAC addressing and networking devices', 'IPv4, IPv6, addressing, subnetting, and CIDR', 'Routing protocols and transport services', 'Ports, sockets, connection setup, flow, and congestion control', 'Application protocols and practical network configuration'],
    },
    'CC-215': {
        'url': 'https://pu.edu.pk/document/merit/exam/1751541151CC-215.pdf',
        'topics': ['Database systems and file-system limitations', 'Relational models, tables, keys, schemas, and integrity rules', 'Relational algebra and joins', 'Entity-relationship modeling', 'Functional dependencies and normalization', 'SQL definition, manipulation, control, joins, subqueries, and aggregation', 'Procedural SQL, triggers, and stored procedures', 'Database design lifecycle', 'Transactions, concurrency, recovery, distributed databases, and NoSQL'],
    },
    'CC-312': {
        'url': 'https://pu.edu.pk/document/merit/exam/1770889186CC-312%20Information%20Security.pdf',
        'topics': ['Information-security foundations and secure design', 'Symmetric and public-key cryptography, hashes, signatures, and key management', 'Authentication and access control', 'Software vulnerabilities, protections, and malware', 'Database and network security, firewalls, and intrusion detection', 'Security policies, risk assessment, and incident response', 'Cybercrime, legal and ethical practice, privacy, and anonymity'],
    },
}


def grouped_catalog():
    groups = []
    by_name = {}
    for program in PROGRAMS:
        group_name = program['group']
        if group_name not in by_name:
            group = {'name': group_name, 'courses': []}
            groups.append(group)
            by_name[group_name] = group
        course = {key: value for key, value in program.items() if key != 'group'}
        for semester in course.get('semesters', []):
            for subject in semester.get('courses', []):
                outline = OFFICIAL_OUTLINES.get(subject.get('code', ''))
                if outline:
                    subject.setdefault('topics', outline['topics'])
                subject['outline_url'] = outline['url'] if outline else course.get('source', '')
        by_name[group_name]['courses'].append(course)
    return groups
