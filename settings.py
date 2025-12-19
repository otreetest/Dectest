from os import environ

# 1. 核心配置：只保留一个 SESSION_CONFIGS
SESSION_CONFIGS = [
    dict(
        name='your_experiment',
        display_name="Your Experiment",
        num_demo_participants=30,
        app_sequence=['pre', 'main', 'end', 'end2'],
    ),
]

# 2. 默认设置
SESSION_CONFIG_DEFAULTS = dict(
    real_world_currency_per_point=1.00, 
    participation_fee=0.00, 
    doc=""
)

# 3. 参与者字段（存 Prolific ID）
PARTICIPANT_FIELDS = ['prolific_id']
SESSION_FIELDS = []

# 4. 基础设置
LANGUAGE_CODE = 'en'
REAL_WORLD_CURRENCY_CODE = 'USD'
USE_POINTS = False

# 5. 管理员与安全
ADMIN_USERNAME = 'admin'
ADMIN_PASSWORD = environ.get('OTREE_ADMIN_PASSWORD')
SECRET_KEY = '7321273217604'
DEBUG = False
PRODUCTION = True

# 6. 房间设置
ROOMS = [
    dict(
        name='prolific_room',
        display_name='Prolific Experiment Room Employee',
    ),
]
DEMO_PAGE_INTRO_HTML = """ """

# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.postgresql',
#         'NAME': 'your_db_name',
#         'USER': 'your_user',
#         'PASSWORD': '20220602',
#         'HOST': 'localhost',
#         'PORT': '4023',
#     }
# }