
### `skills/high_standards/SECURITY_DEVSECOPS.md`
```md
# 🔒 DevSecOpsFlask

**Source:** DEVSECOPS_AND_SECURITY.md → Flask adaptation

## Flask-Specific Rules

**Input Validation (Flask-WTF):**
```python
from flask_wtf import FlaskForm
class MessageForm(FlaskForm):
    subject = StringField(validators=[DataRequired(), Length(max=200)])
    content = TextAreaField(validators=[DataRequired(), Length(max=2000)])
Security Headers (Flask-Talisman):


from flask_talisman import Talisman
Talisman(app, 
    content_security_policy={
        'default-src': "'self'",
        'script-src': "'self' 'unsafe-inline'"
    })
Secret Scanning:
.gitignore → .env
pre-commit → git-secrets
CI → bandit app/