# Application settings
APP_TITLE = "High-Performance Product API"
APP_VERSION = "1.0.0"
DEBUG = True
HOST = "0.0.0.0"
PORT = 8000

# Cache settings
CACHE_DEFAULT_TTL = 300      # seconds
CACHE_MAX_SIZE = 1000        # max items

# Rate limiter
RATE_LIMIT_REQUESTS = 100    # requests per window
RATE_LIMIT_WINDOW = 60       # seconds

# Data
PRODUCTS_COUNT = 500         # number of sample products
