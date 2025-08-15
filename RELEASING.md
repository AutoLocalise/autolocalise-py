# Release Process

Controlled release process with manual triggers for the AutoLocalise Python SDK.

## 🎯 **Publishing Options**

### **Option 1: Manual Workflow (Recommended)**

- Go to [Actions](https://github.com/AutoLocalise/autolocalise-py/actions)
- Click "Run workflow" on CI/CD
- Choose: **TestPyPI** (testing) or **PyPI** (production)

### **Option 2: GitHub Release (Auto-PyPI)**

- Create GitHub release → automatically publishes to both TestPyPI and PyPI

## 📋 **Step-by-Step Process**

### 1. Update Version

```bash
# Edit setup.py
vim setup.py
# Change: version="0.1.0" → version="0.2.0"

# Commit to main branch
git add setup.py
git commit -m "Bump version to 0.2.0"
git push origin main
```

### 2. Test Release (TestPyPI)

**Manual Trigger:**

1. Go to [Actions](https://github.com/AutoLocalise/autolocalise-py/actions)
2. Click "CI/CD" → "Run workflow"
3. Select: **TestPyPI (for testing)**
4. Click "Run workflow"

**What happens:**

- ✅ Runs all tests
- ✅ Builds package
- ✅ Publishes to TestPyPI

### 3. Test Installation

```bash
# Test from TestPyPI
pip install -i https://test.pypi.org/simple/ autolocalise==0.2.0

# Test functionality
python -c "from autolocalise import Translator; print('✅ Works!')"
```

### 4. Production Release (PyPI)

**Option A - Manual:**

1. Go to [Actions](https://github.com/AutoLocalise/autolocalise-py/actions)
2. Click "CI/CD" → "Run workflow"
3. Select: **PyPI (production release)**
4. ⚠️ **Must be on main branch**
5. Click "Run workflow"

**Option B - GitHub Release:**

1. Go to [Releases](https://github.com/AutoLocalise/autolocalise-py/releases)
2. Click "Create a new release"
3. Create new tag: `v0.2.0`
4. Add release notes
5. Click "Publish release"
6. Automatically publishes to both TestPyPI and PyPI

## 🔒 **Safety Features**

- **Tests always run first** - Publishing fails if tests fail
- **Main branch only** - PyPI publishing only allowed from main branch
- **Manual control** - No accidental releases from random pushes
- **TestPyPI first** - Always test before production

## 📊 **Publishing Flow**

```
Update Version → Manual Trigger → Tests → Build → TestPyPI → PyPI
                                    ↓
                              (Fails if tests fail)
```

## 🔧 **Version Numbering**

Use semantic versioning: `X.Y.Z`

- **X** (Major): Breaking changes
- **Y** (Minor): New features
- **Z** (Patch): Bug fixes

## 🚨 **Troubleshooting**

**Tests fail**: Fix issues and try again  
**Version exists**: Use different version number  
**PyPI fails**: Check workflow logs and credentials  
**Wrong branch**: PyPI only works from main branch
