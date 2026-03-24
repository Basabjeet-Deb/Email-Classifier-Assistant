# Backend Restructuring Plan

## Current Structure (Technical Layers)
```
backend/
├── api/              # All routes together
├── models/           # All ML models
├── services/         # All business logic
├── utils/            # All utilities
├── caching/          # Cache logic
└── metrics/          # Metrics logic
```

## New Structure (Feature-Based / Domain-Driven)
```
backend/
├── core/                          # Core infrastructure
│   ├── config.py                 # Configuration
│   ├── database.py               # Database operations
│   ├── cache.py                  # Caching layer
│   └── dependencies.py           # FastAPI dependencies
│
├── features/
│   ├── auth/                     # Authentication domain
│   │   ├── routes.py            # Auth endpoints
│   │   ├── service.py           # OAuth logic
│   │   └── models.py            # Auth data models
│   │
│   ├── email/                    # Email management domain
│   │   ├── routes.py            # Email CRUD endpoints
│   │   ├── service.py           # Gmail API integration
│   │   ├── processor.py         # Email preprocessing
│   │   └── models.py            # Email data models
│   │
│   ├── classification/           # ML Classification domain
│   │   ├── routes.py            # Classification endpoints
│   │   ├── service.py           # Hybrid classification logic
│   │   ├── models/              # ML models
│   │   │   ├── tfidf_classifier.py
│   │   │   ├── keyword_classifier.py
│   │   │   └── zero_shot_classifier.py
│   │   ├── preprocessor.py      # Text preprocessing
│   │   └── schemas.py           # Classification schemas
│   │
│   ├── feedback/                 # Feedback & Learning domain
│   │   ├── routes.py            # Feedback endpoints
│   │   ├── service.py           # Self-learning logic
│   │   ├── storage.py           # Feedback persistence
│   │   └── retrainer.py         # Model retraining
│   │
│   └── analytics/                # Analytics domain
│       ├── routes.py            # Analytics endpoints
│       ├── service.py           # Analytics computation
│       ├── tracker.py           # Metrics tracking
│       └── schemas.py           # Analytics schemas
│
├── shared/                       # Shared utilities
│   ├── exceptions.py            # Custom exceptions
│   ├── logging.py               # Logging setup
│   └── utils.py                 # Common utilities
│
└── api/                          # API layer (thin)
    ├── __init__.py
    └── router.py                # Main router aggregator
```

## Benefits of New Structure

### 1. **Scalability**
- Easy to add new features (e.g., `features/user/`, `features/notifications/`)
- Each feature is self-contained
- Clear boundaries between domains

### 2. **Maintainability**
- Related code stays together
- Easy to find and modify feature-specific code
- Reduced cognitive load

### 3. **Team Collaboration**
- Different developers can work on different features
- Minimal merge conflicts
- Clear ownership of features

### 4. **Testing**
- Feature-specific tests in same directory
- Easy to mock dependencies
- Better test organization

### 5. **Microservices Ready**
- Each feature can become a microservice
- Clear API boundaries
- Independent deployment possible

## Migration Steps

1. Create new directory structure
2. Move files to appropriate feature folders
3. Update imports across the codebase
4. Update API router to aggregate feature routes
5. Test all endpoints
6. Update documentation

## File Mapping

### Auth Feature
- `services/gmail_service.py` → `features/auth/service.py`
- New: `features/auth/routes.py` (extract from api/routes.py)

### Email Feature
- `utils/email_processor.py` → `features/email/processor.py`
- New: `features/email/service.py` (Gmail operations)
- New: `features/email/routes.py` (scan, delete, archive)

### Classification Feature
- `models/*` → `features/classification/models/`
- `services/classification_service.py` → `features/classification/service.py`
- `utils/robust_preprocessor.py` → `features/classification/preprocessor.py`

### Feedback Feature
- `services/self_learning_service.py` → `features/feedback/service.py`
- New: `features/feedback/routes.py`
- New: `features/feedback/storage.py`

### Analytics Feature
- `metrics/tracker.py` → `features/analytics/tracker.py`
- New: `features/analytics/service.py`
- New: `features/analytics/routes.py`

### Core
- `config.py` → `core/config.py`
- `database.py` → `core/database.py` (move from root)
- `caching/lru_cache.py` → `core/cache.py`
