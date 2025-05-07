"""
Installed apps and middleware settings for OpenStax CMS.

This module contains the list of installed apps and middleware.
"""

# Installed apps
INSTALLED_APPS = [
    # Django core apps
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.postgres',
    'django.contrib.admin',
    'django.contrib.sitemaps',
    
    # Third-party apps
    'compressor',
    'taggit',
    'modelcluster',
    'rest_framework',
    'rest_framework.authtoken',
    'rest_auth',
    'django_crontab',
    'django_filters',
    'storages',
    'django_ses',
    'import_export',
    'rangefilter',
    'reversion',
    'wagtail_modeladmin',
    
    # Custom apps
    'accounts',
    'api',
    'pages',
    'books',
    'news',
    'snippets',
    'salesforce',
    'mail',
    'global_settings',
    'errata',
    'redirects',
    'oxauth',
    'webinars',
    'donations',
    'wagtailimportexport',
    'versions',
    'oxmenus',
    
    # Wagtail apps
    'wagtail',
    'wagtail.admin',
    'wagtail.documents',
    'wagtail.snippets',
    'wagtail.users',
    'wagtail.images',
    'wagtail.embeds',
    'wagtail.search',
    'wagtail.contrib.redirects',
    'wagtail.contrib.simple_translation',
    'wagtail.locales',
    'wagtail.contrib.forms',
    'wagtail.sites',
    'wagtail.api.v2',
    'wagtail.contrib.settings',
]

# Middleware
MIDDLEWARE = [
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'healthcheck.middleware.HealthCheckMiddleware',  # has to be before CommonMiddleware
    'openstax.middleware.CommonMiddlewareAppendSlashWithoutRedirect',
    'openstax.middleware.CommonMiddlewareOpenGraphRedirect',
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'wagtail.contrib.redirects.middleware.RedirectMiddleware',
    'django.middleware.cache.UpdateCacheMiddleware',
    'django.middleware.cache.FetchFromCacheMiddleware',
]

# Authentication backends
AUTHENTICATION_BACKENDS = (
    'django.contrib.auth.backends.ModelBackend',
)

# Templates
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'APP_DIRS': False,
        'OPTIONS': {
            'context_processors': [
                'django.contrib.auth.context_processors.auth',
                'django.template.context_processors.debug',
                'django.template.context_processors.i18n',
                'django.template.context_processors.media',
                'django.template.context_processors.static',
                'django.template.context_processors.tz',
                'django.contrib.messages.context_processors.messages',
                'django.template.context_processors.request',
            ],
            'loaders': [
                ('django.template.loaders.cached.Loader', [
                    'django.template.loaders.filesystem.Loader',
                    'django.template.loaders.app_directories.Loader',
                ]),
            ],
        },
    },
] 