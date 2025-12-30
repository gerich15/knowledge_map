knowledge_map/
├── docker-compose.yml
├── .env.example
├── requirements.txt
├── README.md
├── .gitignore
├── manage.py
├── config/
│   ├── __init__.py
│   ├── settings.py
│   ├── urls.py
│   ├── wsgi.py
│   └── asgi.py
├── core/
│   ├── __init__.py
│   ├── admin.py
│   ├── apps.py
│   ├── models.py
│   ├── tests.py
│   ├── views.py
│   ├── urls.py
│   └── management/
│       └── commands/
│           └── create_sample_data.py
├── api/
│   ├── __init__.py
│   ├── urls.py
│   ├── views.py
│   ├── serializers.py
│   ├── permissions.py
│   └── pagination.py
├── users/
│   ├── __init__.py
│   ├── admin.py
│   ├── apps.py
│   ├── models.py
│   ├── tests.py
│   ├── views.py
│   ├── urls.py
│   └── forms.py
├── branches/
│   ├── __init__.py
│   ├── admin.py
│   ├── apps.py
│   ├── models.py
│   ├── tests.py
│   ├── views.py
│   ├── urls.py
│   └── forms.py
├── posts/
│   ├── __init__.py
│   ├── admin.py
│   ├── apps.py
│   ├── models.py
│   ├── tests.py
│   ├── views.py
│   ├── urls.py
│   └── forms.py
├── subscriptions/
│   ├── __init__.py
│   ├── admin.py
│   ├── apps.py
│   ├── models.py
│   ├── tests.py
│   ├── views.py
│   └── urls.py
├── timeline/
│   ├── __init__.py
│   ├── admin.py
│   ├── apps.py
│   ├── models.py
│   ├── tests.py
│   ├── views.py
│   └── urls.py
├── templates/
│   ├── base.html
│   ├── dashboard.html
│   ├── profile.html
│   ├── branch_detail.html
│   ├── post_form.html
│   ├── branches/
│   │   ├── branch_list.html
│   │   └── branch_form.html
│   ├── posts/
│   │   ├── post_list.html
│   │   └── post_detail.html
│   ├── users/
│   │   ├── login.html
│   │   ├── register.html
│   │   └── profile_edit.html
│   └── includes/
│       ├── header.html
│       ├── footer.html
│       ├── posts_list.html
│       ├── timeline.html
│       └── notifications.html
└── static/
    ├── css/
    │   └── custom.css
    ├── js/
    │   └── alpine-init.js
    └── images/