import os

from .base import *    # NOQA


DEBUG = False

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',   # 数据库引擎
        'NAME': 'blog',                       # 数据库名称
        'USER': 'root',                      # 数据库登录用户名
        'PASSWORD': '123456',                # 密码
        'HOST': '127.0.0.1',                # 数据库主机IP，如保持默认，则为127.0.0.1
        'PORT': 3306,                           # 数据库端口号，如保持默认，则为3306
    }
}

INSTALLED_APPS += [
    'debug_toolbar',
    # 'raven.contrib.django.raven_compat',
]

MIDDLEWARE += [
    'debug_toolbar.middleware.DebugToolbarMiddleware',
]

INTERNAL_IPS = ['127.0.0.1']
