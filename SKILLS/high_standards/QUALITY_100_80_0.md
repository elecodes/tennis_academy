
### `skills/high_standards/QUALITY_100_80_0.md`
```md
# 🧪 Coverage100_80_0

**Source:** QUALITY_AND_TESTING_POLICY.md

## Layer Mapping for Flask

| Layer | Coverage | Files |
|-------|----------|-------|
| **CORE (100%)** | RBAC, repositories | `repositories/`, RBAC decorators |
| **GLOBAL (80%)** | Flask routes, services | `routes/`, `app.py` |
| **INFRA (0%)** | Static templates, config | `templates/`, `static/` |

## pytest-cov Commands
```bash
# CORE only
pytest tests/unit/ --cov=repositories --cov-fail-under=100

# GLOBAL  
pytest tests/integration/ --cov=routes --cov-fail-under=80
