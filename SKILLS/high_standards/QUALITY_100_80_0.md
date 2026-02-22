
### `skills/high_standards/QUALITY_100_80_0.md`
```md
# 🧪 Coverage100_80_0

**Source:** QUALITY_AND_TESTING_POLICY.md

## Layer Mapping for Flask

| Layer | Coverage | Files |
|-------|----------|-------|
| **CORE (100%)** | RBAC, repositories | `backend/repositories/`, backend/app.py (decorators) |
| **GLOBAL (80%)** | Flask routes, services | `backend/routes/`, `backend/app.py` |
| **INFRA (0%)** | Static templates, config | `frontend/templates/`, `frontend/static/` |

## pytest-cov Commands
```bash
# CORE only
export PYTHONPATH=$PYTHONPATH:. && pytest tests/unit/ --cov=backend/repositories --cov-fail-under=100

# GLOBAL  
export PYTHONPATH=$PYTHONPATH:. && pytest tests/integration/ --cov=backend/routes --cov-fail-under=80
