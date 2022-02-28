import json
from django.core.management.base import BaseCommand
from pages.models import Subjects, Subject


class Command(BaseCommand):
    help="Populate subject pages after a deployment"

    def handle(self, *args, **options):
        subjects_page = Subjects.objects.first() # there's only one Subjects page, so this should be okay
        # math page ###
        math_page = Subject(
            title='Math',
            page_description="Simple to use, simple to adopt. Our online math textbooks are designed to meet the standard scope and sequence requirements of several math courses – and are 100% free. Complete with free resources for educators (like course cartridges, PowerPoints, instructor solution guides, and more), check out our books below to see if they’re right for your course.",
            blog_header=json.dumps([{"type": "content",
                 "value": {'heading': "Blogs about OpenStax math textbooks",
                           'blog_description': "Read up on best practices for using our free math textbooks and instructor resources in your course in these blog posts.",
                           'link_text': "View all blog posts",
                           'link_href': "https://openstax.org/blogs"
                           },
                 }
            ]),
            webinar_header=json.dumps([{"type": "content",
                 "value": {'heading': "Webinars about OpenStax math textbooks",
                           'webinar_description': "Learn how our free textbooks are made, straight from the experts. Get tips and tricks for using an OpenStax book from everyday educators.",
                           'link_text': "View all webinars",
                           'link_href': "https://openstax.org/webinars"
                           },
                 }
            ]),
            os_textbook_heading="Learn more about OpenStax Math textbooks",
            os_textbook_categories=json.dumps([
                {"type": "category", "value": [{"heading": "Placeholder category", "text": "Placeholder text"}]}
            ]),
            about_os=json.dumps([
                {"type": "content",
                 "value": {'heading': "About Openstax textbooks",
                           'os_text': "OpenStax is part of Rice University, a 501(c)(3) nonprofit charitable corporation. As an educational initiative, it's our mission to improve educational access and learning for everyone. We provide access to education for millions of learners by publishing high-quality, peer-reviewed, openly licensed college textbooks that are available free online. We currently offer nine free math textbooks, and our library is only growing: Algebra and Trigonometry; Calculus (Volumes 1, 2, and 3); College Algebra; College Algebra with Corequisite Support; Elementary Algebra 2e; Intermediate Algebra 2e; Introductory Statistics; Prealgebra 2e; and Precalculus.",
                           'link_text': 'Learn about OpenStax',
                           'link_href': 'https://openstax.org/about-us'
                          },
                }
            ]),
            info_boxes=json.dumps([
                {"type": "info_box","value": [{"heading": "Expert Authors", "text": "Our free, openly licensed math textbooks are written by professional content developers who are experts in their fields."},
                                              {"heading": "Standard Scope and Sequence", "text": "All of our math textbooks meet standard scope and sequence requirements, making them seamless to adopt for existing math courses."},
                                              {"heading": "Peer Reviewed", "text": "OpenStax’s free math textbooks undergo a rigorous peer review process. You can view the full list of contributors in the preface of our online and print textbooks."},
                                             ]
                 }
            ]),
            philanthropic_support="With philanthropic support, our books have been used in <strong>38,160<strong> classrooms, saving students <strong>$1,747,190,405<strong> since 2012. <a href='https://openstax.org/impact'>Learn more about our impact</a> and how you can help."

        )
        subjects_page.add_child(instance=math_page)
        revision = math_page.save_revision()
        revision.publish()
        math_page.save()

        # Science page ###
        science_page = Subject(
            title='Science',
            page_description="Simple to use, simple to adopt. Our online science textbooks are designed to meet the standard scope and sequence requirements of several science courses – and are 100% free. Complete with free resources for educators (like course cartridges, PowerPoints, test banks, and more), check out our books below to see if they’re right for your course.",
            tutor_ad=json.dumps([
                {"type": "content",
                 "value": {'heading': "INSTRUCTORS, TAKE YOUR COURSE ONLINE",
                           'ad_html': "Improve student engagement and learning with <a href='https://openstax.org/openstax-tutor'>OpenStax Tutor</a>. With enhanced digital reading assignments, personalized homework, thousands of assessments, and LMS integration, OpenStax Tutor is available for our Anatomy and Physiology, Biology 2e, and College Physics textbooks.",
                           'link_text': "Learn more",
                           'link_href': "https://openstax.org/tutor"
                           },
                 }
            ]),
            blog_header=json.dumps([{"type": "content",
                                     "value": {'heading': "Blogs about OpenStax science textbooks",
                                               'blog_description': "Read up on best practices for using our free science textbooks and instructor resources in your course in these blog posts.",
                                               'link_text': "View all blog posts",
                                               'link_href': "https://openstax.org/blogs"
                                               },
                                     }
                                    ]),
            webinar_header=json.dumps([{"type": "content",
                                        "value": {'heading': "Webinars about OpenStax science textbooks",
                                                  'webinar_description': "Learn how our free textbooks are made, straight from the experts. Get tips and tricks for using an OpenStax book from everyday educators.",
                                                  'link_text': "View all webinars",
                                                  'link_href': "https://openstax.org/webinars"
                                                  },
                                        }
                                       ]),
            os_textbook_heading="Learn more about OpenStax Science textbooks",
            os_textbook_categories=json.dumps([
                {"type": "category", "value": [{"heading": "Placeholder category", "text": "Placeholder text"}]}
            ]),
            about_os=json.dumps([
                {"type": "content",
                 "value": {'heading': "About Openstax textbooks",
                           'os_text': "OpenStax is part of Rice University, a 501(c)(3) nonprofit charitable corporation. As an educational initiative, it's our mission to improve educational access and learning for everyone. We provide access to education for millions of learners by publishing high-quality, peer-reviewed, openly licensed college textbooks that are available free online. We currently offer 10 free science textbooks, and our library is only growing: Anatomy and Physiology; Astronomy; Biology 2e; Chemistry 2e; Chemistry: Atoms First 2e; College Physics; Concepts of Biology; Microbiology; and University Physics (Volumes 1, 2, and 3).<br/><br/>We've also created <a href='https://openstax.org/openstax-tutor'>OpenStax Tutor</a>, a low-cost, research-based courseware that features digital reading, LMS integration, personalized homework, and more. OpenStax Tutor is currently available for our Anatomy and Physiology, Biology 2e, and College Physics texts.",
                           'link_text': 'Learn about OpenStax',
                           'link_href': 'https://openstax.org/about-us'
                           },
                 }
            ]),
            info_boxes=json.dumps([
                {"type": "info_box", "value": [{"heading": "Expert Authors",
                                               "text": "Our free, openly licensed science textbooks are written by professional content developers who are experts in their fields."},
                                               {"heading": "Standard Scope and Sequence",
                                               "text": "All of our science textbooks meet standard scope and sequence requirements, making them seamless to adopt for existing science courses."},
                                               {"heading": "Peer Reviewed",
                                               "text": "OpenStax’s free science textbooks undergo a rigorous peer review process. You can view the full list of contributors in the preface of our online and print textbooks"},
                                              ]
                 }
            ]),
            philanthropic_support="With philanthropic support, our books have been used in <strong>38,160<strong> classrooms, saving students <strong>$1,747,190,405<strong> since 2012. <a href='https://openstax.org/impact'>Learn more about our impact</a> and how you can help."

        )
        subjects_page.add_child(instance=science_page)
        revision = science_page.save_revision()
        revision.publish()
        science_page.save()

        # social science page ###
        social_science_page = Subject(
            title='Social Sciences',
            page_description="Simple to use, simple to adopt. Our online social sciences textbooks are designed to meet the standard scope and sequence requirements of several social sciences courses – and are 100% free. Complete with free resources for educators (like course cartridges, PowerPoints, test banks, and more), check out our books below to see if they’re right for your course.",
            tutor_ad=json.dumps([
                {"type": "content",
                 "value": {'heading': "INSTRUCTORS, TAKE YOUR COURSE ONLINE",
                           'ad_html': "Improve student engagement and learning with <a href='https://openstax.org/openstax-tutor'>OpenStax Tutor</a>. With enhanced digital reading assignments, personalized homework, thousands of assessments, and LMS integration, OpenStax Tutor is available for our Introduction to Sociology 3e and Psychology 2e textbooks.",
                           'link_text': "Learn more",
                           'link_href': "https://openstax.org/tutor"
                           },
                 }
            ]),
            blog_header=json.dumps([{"type": "content",
                                     "value": {'heading': "Blogs about OpenStax social sciences textbooks",
                                               'blog_description': "Read up on best practices for using our free social sciences textbooks and instructor resources in your course in these blog posts.",
                                               'link_text': "View all blog posts",
                                               'link_href': "https://openstax.org/blogs"
                                               },
                                     }
                                    ]),
            webinar_header=json.dumps([{"type": "content",
                                        "value": {'heading': "Webinars about OpenStax social sciences textbooks",
                                                  'webinar_description': "Learn how our free textbooks are made, straight from the experts. Get tips and tricks for using an OpenStax book from everyday educators.",
                                                  'link_text': "View all webinars",
                                                  'link_href': "https://openstax.org/webinars"
                                                  },
                                        }
                                       ]),
            os_textbook_heading="Learn more about OpenStax Social Sciences textbooks",
            os_textbook_categories=json.dumps([
                {"type": "category", "value": [{"heading": "Placeholder category", "text": "Placeholder text"}]}
            ]),
            about_os=json.dumps([
                {"type": "content",
                 "value": {'heading': "About Openstax textbooks",
                           'os_text': "OpenStax is part of Rice University, a 501(c)(3) nonprofit charitable corporation. As an educational initiative, it's our mission to improve educational access and learning for everyone. We provide access to education for millions of learners by publishing high-quality, peer-reviewed, openly licensed college textbooks that are available free online. We currently offer seven free social sciences textbooks, and our library is growing: American Government 3e; Introduction to Sociology 3e; Principles of Economics 2e; Principles of Macroeconomics 2e; Principles of Microeconomics 2e; Psychologia; and Psychology 2e. <br/><br/>We've also created <a href='https://openstax.org/openstax-tutor'>OpenStax Tutor</a>, a low-cost, research-based courseware that features digital reading, LMS integration, personalized homework, and more. OpenStax Tutor is currently available for our Introduction to Sociology 3e and Psychology 2e texts. ",
                           'link_text': 'Learn about OpenStax',
                           'link_href': 'https://openstax.org/about-us'
                           },
                 }
            ]),
            info_boxes=json.dumps([
                {"type": "info_box", "value": [{"heading": "Expert Authors",
                                               "text": "Our free, openly licensed social sciences textbooks are written by professional content developers who are experts in their fields."},
                                               {"heading": "Standard Scope and Sequence",
                                               "text": "All of our social sciences textbooks meet standard scope and sequence requirements, making them seamless to adopt for new and existing social sciences courses."},
                                               {"heading": "Peer Reviewed",
                                               "text": "OpenStax’s free social sciences textbooks undergo a rigorous peer review process. You can view the full list of contributors in the preface of our online and print textbooks."},
                                              ]
                 }
            ]),
            philanthropic_support="With philanthropic support, our books have been used in <strong>38,160<strong> classrooms, saving students <strong>$1,747,190,405<strong> since 2012. <a href='https://openstax.org/impact'>Learn more about our impact</a> and how you can help."

        )
        subjects_page.add_child(instance=social_science_page)
        revision = social_science_page.save_revision()
        revision.publish()
        social_science_page.save()

        # Humanities page ###
        humanities_page = Subject(
            title='Humanities',
            page_description="Simple to use, simple to adopt. Our online humanities textbooks are designed to meet the standard scope and sequence requirements of several humanities courses – and are 100% free. Complete with free resources for educators (like course cartridges, PowerPoints, instructor answer guides, and more), check out our books below to see if they’re right for your course.",
            tutor_ad=json.dumps([
                {"type": "content",
                 "value": {'heading': "INSTRUCTORS, TAKE YOUR COURSE ONLINE",
                           'ad_html': "Improve student engagement and learning with <a href='https://openstax.org/openstax-tutor'>OpenStax Tutor</a>. With enhanced digital reading assignments, personalized homework, thousands of assessments, and LMS integration, OpenStax Tutor is available for our Life, Liberty, and the Pursuit of Happiness and U.S. History textbooks.",
                           'link_text': "Learn more",
                           'link_href': "https://openstax.org/tutor"
                           },
                 }
            ]),
            blog_header=json.dumps([{"type": "content",
                                     "value": {'heading': "Blogs about OpenStax humanities textbooks",
                                               'blog_description': "Read up on best practices for using our free humanities textbooks and instructor resources in your course in these blog posts.",
                                               'link_text': "View all blog posts",
                                               'link_href': "https://openstax.org/blogs"
                                               },
                                     }
                                    ]),
            webinar_header=json.dumps([{"type": "content",
                                        "value": {'heading': "Webinars about OpenStax humanities textbooks",
                                                  'webinar_description': "Learn how our free textbooks are made, straight from the experts. Get tips and tricks for using an OpenStax book from everyday educators.",
                                                  'link_text': "View all webinars",
                                                  'link_href': "https://openstax.org/webinars"
                                                  },
                                        }
                                       ]),
            os_textbook_heading="Learn more about OpenStax Humanities textbooks",
            os_textbook_categories=json.dumps([
                {"type": "category", "value": [{"heading": "Placeholder category", "text": "Placeholder text"}]}
            ]),
            about_os=json.dumps([
                {"type": "content",
                 "value": {'heading': "About Openstax textbooks",
                           'os_text': "OpenStax is part of Rice University, a 501(c)(3) nonprofit charitable corporation. As an educational initiative, it's our mission to improve educational access and learning for everyone. We provide access to education for millions of learners by publishing high-quality, peer-reviewed, openly licensed college textbooks that are available free online. We currently offer three free humanities textbooks, and our library is only growing: Life, Liberty, and the Pursuit of Happiness, U.S. History, and Writing Guide with Handbook. <br/><br/>We've also created <a href='https://openstax.org/openstax-tutor'>OpenStax Tutor</a>, a low-cost, research-based courseware that features digital reading, LMS integration, personalized homework, and more. OpenStax Tutor is currently available for our Life, Liberty, and the Pursuit of Happiness and U.S. History texts.",
                           'link_text': 'Learn about OpenStax',
                           'link_href': 'https://openstax.org/about-us'
                           },
                 }
            ]),
            info_boxes=json.dumps([
                {"type": "info_box", "value": [{"heading": "Expert Authors",
                                               "text": "Our free, openly licensed humanities textbooks are written by professional content developers who are experts in their fields."},
                                               {"heading": "Standard Scope and Sequence",
                                               "text": "All of our humanities textbooks meet standard scope and sequence requirements, making them seamless to adopt for existing humanities courses."},
                                               {"heading": "Peer Reviewed",
                                               "text": "OpenStax’s free humanities textbooks undergo a rigorous peer review process. You can view the full list of contributors in the preface of our online and print textbooks."},
                                              ]
                 }
            ]),
            philanthropic_support="With philanthropic support, our books have been used in <strong>38,160<strong> classrooms, saving students <strong>$1,747,190,405<strong> since 2012. <a href='https://openstax.org/impact'>Learn more about our impact</a> and how you can help."

        )
        subjects_page.add_child(instance=humanities_page)
        revision = humanities_page.save_revision()
        revision.publish()
        humanities_page.save()

        # college success page ###
        college_success_page = Subject(
            title='College Success',
            page_description="Simple to use, simple to adopt. Our online College Success textbook is designed to meet the standard scope and sequence requirements of first-year experience courses – and is 100% free. Complete with free resources for educators (like course cartridges, PowerPoint slides, a test bank, and more), check out our book below to see if it’s right for your course.",
            blog_header=json.dumps([{"type": "content",
                                     "value": {'heading': "Blogs about OpenStax college success textbooks",
                                               'blog_description': "Read up on best practices for using our free College Success textbook and instructor resources in your course in these blog posts.",
                                               'link_text': "View all blog posts",
                                               'link_href': "https://openstax.org/blogs"
                                               },
                                     }
                                    ]),
            webinar_header=json.dumps([{"type": "content",
                                        "value": {'heading': "Webinars about OpenStax college success textbooks",
                                                  'webinar_description': "Learn how our free textbooks are made, straight from the experts. Get tips and tricks for using an OpenStax book from everyday educators.",
                                                  'link_text': "View all webinars",
                                                  'link_href': "https://openstax.org/webinars"
                                                  },
                                        }
                                       ]),
            os_textbook_heading="Learn more about OpenStax College Success textbooks",
            os_textbook_categories=json.dumps([
                {"type": "category", "value": [{"heading": "Placeholder category", "text": "Placeholder text"}]}
            ]),
            about_os=json.dumps([
                {"type": "content",
                 "value": {'heading': "About Openstax textbooks",
                           'os_text': "OpenStax is part of Rice University, a 501(c)(3) nonprofit charitable corporation. As an educational initiative, it's our mission to improve educational access and learning for everyone.. We provide access to education for millions of learners by publishing high-quality, peer-reviewed, openly licensed college textbooks that are available free online. We currently offer College Success for First Year Experience, Student Success, and College Transition courses.",
                           'link_text': 'Learn about OpenStax',
                           'link_href': 'https://openstax.org/about-us'
                           },
                 }
            ]),
            info_boxes=json.dumps([
                {"type": "info_box", "value": [{"heading": "Expert Authors",
                                               "text": "Our free, openly licensed College Success textbook is written by professional content developers who are experts in their fields."},
                                               {"heading": "Standard Scope and Sequence",
                                               "text": "Our College Success textbook meets standard scope and sequence requirements, making it seamless to adopt for new and existing First Year Experience, Student Success, and College Transition courses."},
                                               {"heading": "Peer Reviewed",
                                               "text": "OpenStax’s free College Success textbook undergoes a rigorous peer review process. You can view the full list of contributors in the preface of our online and print textbooks."},
                                              ]
                 }
            ]),
            philanthropic_support="With philanthropic support, our books have been used in <strong>38,160<strong> classrooms, saving students <strong>$1,747,190,405<strong> since 2012. <a href='https://openstax.org/impact'>Learn more about our impact</a> and how you can help."

        )
        subjects_page.add_child(instance=college_success_page)
        revision = college_success_page.save_revision()
        revision.publish()
        college_success_page.save()

        # high school page ###
        high_school_page = Subject(
            title='High School',
            page_description="Simple to use, simple to adopt. Our online high school textbooks are designed to meet the standard scope and sequence requirements of several high school and Advanced Placement courses® – and are 100% free. Complete with free resources for educators (like course cartridges, PowerPoints, test banks, and more), check out our books below to see if they’re right for your course.",
            tutor_ad=json.dumps([
                {"type": "content",
                 "value": {'heading': "INSTRUCTORS, TAKE YOUR COURSE ONLINE",
                           'ad_html': "Improve student engagement and learning with <a href='https://openstax.org/openstax-tutor'>OpenStax Tutor</a>. With enhanced digital reading assignments, personalized homework, thousands of assessments, and LMS integration, OpenStax Tutor is available for our AP® Physics Collection, Life, Liberty, and the Pursuit of Happiness, and Biology for AP® Courses textbooks",
                           'link_text': "Learn more",
                           'link_href': "https://openstax.org/tutor"
                           },
                 }
            ]),
            blog_header=json.dumps([{"type": "content",
                                     "value": {'heading': "Blogs about OpenStax high school textbooks",
                                               'blog_description': "Read up on best practices for using our free high school and Advanced Placement® textbooks and instructor resources in your course in these blog posts.",
                                               'link_text': "View all blog posts",
                                               'link_href': "https://openstax.org/blogs"
                                               },
                                     }
                                    ]),
            webinar_header=json.dumps([{"type": "content",
                                        "value": {'heading': "Webinars about OpenStax college success textbooks",
                                                  'webinar_description': "Learn how our free textbooks are made, straight from the experts. Get tips and tricks for using an OpenStax book from everyday educators.",
                                                  'link_text': "View all webinars",
                                                  'link_href': "https://openstax.org/webinars"
                                                  },
                                        }
                                       ]),
            os_textbook_heading="Learn more about OpenStax High School textbooks",
            os_textbook_categories=json.dumps([
                {"type": "category", "value": [{"heading": "Placeholder category", "text": "Placeholder text"}]}
            ]),
            about_os=json.dumps([
                {"type": "content",
                 "value": {'heading': "About Openstax textbooks",
                           'os_text': "OpenStax is part of Rice University, a 501(c)(3) nonprofit charitable corporation. As an educational initiative, it's our mission to improve educational access and learning for everyone. We provide access to education for millions of learners by publishing high-quality, peer-reviewed, openly licensed college textbooks that are available free online. We currently offer six free high school textbooks, and our library is only growing: The AP® Physics Collection; Biology for AP® Courses; High School Physics; Principles of Macroeconomics for AP® Courses 2e; Principles of Microeconomics for AP® Courses 2e; High School Statistics; and Life, Liberty, and the Pursuit of Happiness. <br/><br/>We've also created <a href='https://openstax.org/openstax-tutor'>OpenStax Tutor</a>, a low-cost, research-based courseware that features digital reading, LMS integration, personalized homework, and more. OpenStax Tutor is currently available for our AP® Physics Collection and Biology for AP® Courses texts.",
                           'link_text': 'Learn about OpenStax',
                           'link_href': 'https://openstax.org/about-us'
                           },
                 }
            ]),
            info_boxes=json.dumps([
                {"type": "info_box", "value": [{"heading": "Expert Authors",
                                               "text": "Our free, openly licensed high school and Advanced Placement® textbooks are written by professional content developers who are experts in their fields."},
                                               {"heading": "Standard Scope and Sequence",
                                               "text": "All of our high school and Advanced Placement® textbooks meet standard scope and sequence requirements, making them seamless to adopt for existing high school and Advanced Placement® courses."},
                                               {"heading": "Peer Reviewed",
                                               "text": "OpenStax’s free high school and Advanced Placement® textbooks undergo a rigorous peer review process. You can view the full list of contributors in the preface of our online and print textbooks."},
                                              ]
                 }
            ]),
            philanthropic_support="With philanthropic support, our books have been used in <strong>38,160<strong> classrooms, saving students <strong>$1,747,190,405<strong> since 2012. <a href='https://openstax.org/impact'>Learn more about our impact</a> and how you can help."

        )
        subjects_page.add_child(instance=high_school_page)
        revision = high_school_page.save_revision()
        revision.publish()
        high_school_page.save()

        # business ###
        business_page = Subject(
            title='Business',
            page_description="Simple to use, simple to adopt. Our online business textbooks are designed to meet the standard scope and sequence requirements of several business courses – and are 100% free. Complete with free resources for educators (like course cartridges, PowerPoints, test banks, and more), check out our books below to see if they’re right for your course.",
            tutor_ad=json.dumps([
                {"type": "content",
                 "value": {'heading': "INSTRUCTORS, TAKE YOUR COURSE ONLINE",
                           'ad_html': "Improve student engagement and learning with <a href='https://openstax.org/openstax-tutor'>OpenStax Tutor</a>. With enhanced digital reading assignments, personalized homework, thousands of assessments, and LMS integration, OpenStax Tutor is available for our Entrepreneurship textbook.",
                           'link_text': "Learn more",
                           'link_href': "https://openstax.org/tutor"
                           },
                 }
            ]),
            blog_header=json.dumps([{"type": "content",
                                     "value": {'heading': "Blogs about OpenStax high school textbooks",
                                               'blog_description': "Read up on best practices for using our free business textbooks and instructor resources in your course in these blog posts.",
                                               'link_text': "View all blog posts",
                                               'link_href': "https://openstax.org/blogs"
                                               },
                                     }
                                    ]),
            webinar_header=json.dumps([{"type": "content",
                                        "value": {'heading': "Webinars about OpenStax college success textbooks",
                                                  'webinar_description': "Learn how our free textbooks are made, straight from the experts. Get tips and tricks for using an OpenStax book from everyday educators.",
                                                  'link_text': "View all webinars",
                                                  'link_href': "https://openstax.org/webinars"
                                                  },
                                        }
                                       ]),
            os_textbook_heading = "Learn more about OpenStax Business textbooks",
            os_textbook_categories = json.dumps([
                {"type": "category", "value": [{"heading": "Placeholder category", "text": "Placeholder text"}]}
               ]),
            about_os=json.dumps([
                {"type": "content",
                 "value": {'heading': "About Openstax textbooks",
                           'os_text': "OpenStax is part of Rice University, a 501(c)(3) nonprofit charitable corporation. As an educational initiative, it's our mission to improve educational access and learning for everyone. We provide access to education for millions of learners by publishing high-quality, peer-reviewed, openly licensed college textbooks that are available free online. We currently offer several free business textbooks, and our library is only growing: Business Ethics, Business Law I Essentials, Entrepreneurship, Introduction to Business, Introduction to Intellectual Property, Introductory Business Statistics, Organizational Behavior, Principles of Accounting, Volume 1: Financial Accounting, Principles of Accounting, Volume 2: Managerial Accounting, and Principles of Management. <br/><br/>We've also created <a href='https://openstax.org/openstax-tutor'>OpenStax Tutor</a>, a low-cost, research-based courseware that features digital reading, LMS integration, personalized homework, and more. OpenStax Tutor is currently available for our Entrepreneurship text.",
                           'link_text': 'Learn about OpenStax',
                           'link_href': 'https://openstax.org/about-us'
                           },
                 }
            ]),
            info_boxes=json.dumps([
                {"type": "info_box", "value": [{"heading": "Expert Authors",
                                               "text": "Our free, openly licensed business textbooks are written by professional content developers who are experts in their fields."},
                                               {"heading": "Standard Scope and Sequence",
                                               "text": "All of our business textbooks meet standard scope and sequence requirements, making them seamless to adopt for new and existing business courses."},
                                               {"heading": "Peer Reviewed",
                                               "text": "OpenStax’s free business textbooks undergo a rigorous peer review process. You can view the full list of contributors in the preface of our online and print textbooks."},
                                              ]
                 }
            ]),
            philanthropic_support="With philanthropic support, our books have been used in <strong>38,160<strong> classrooms, saving students <strong>$1,747,190,405<strong> since 2012. <a href='https://openstax.org/impact'>Learn more about our impact</a> and how you can help."

        )
        subjects_page.add_child(instance=business_page)
        revision = business_page.save_revision()
        revision.publish()
        business_page.save()
