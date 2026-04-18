#!/bin/bash
# Initialize Git repository and push to GitHub
# Usage: ./scripts/init_git.sh

set -e

echo "=================================================="
echo "  Initialize Git Repository for Tooling RAG"
echo "=================================================="
echo ""

cd "$(dirname "$0")/.."

# Check if git is already initialized
if [ -d ".git" ]; then
    echo "⚠️  Git repository already exists."
    read -p "Do you want to reinitialize? (y/N): " confirm
    if [[ ! $confirm =~ ^[Yy]$ ]]; then
        echo "Cancelled."
        exit 0
    fi
fi

# Initialize git repo
echo "📦 Initializing Git repository..."
git init -b main

# Create .gitignore
cat > .gitignore << 'EOF'
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
venv/
ENV/
env/
.venv
*.egg-info/
dist/
build/
.eggs/

# IDE
.idea/
.vscode/
*.swp
*.swo
*~

# Testing
.pytest_cache/
.coverage
htmlcov/
.tox/
coverage.xml
*.cover
.hypothesis/

# Vector store (regenerate on startup)
vector_store/

# Data
data/raw/*
!data/raw/.gitkeep
data/processed/*
!data/processed/.gitkeep

# Logs
*.log
logs/

# OS
.DS_Store
Thumbs.db

# Environment
.env
.env.local
*.local

# Documentation build
docs/_build/
docs/.doctrees/
EOF

echo "✓ Created .gitignore"

# Add all files
echo "📝 Adding files..."
git add .

# Create initial commit
echo "💾 Creating initial commit..."
git commit -m "feat: Initial commit for Tooling RAG Knowledge Base

- DDD architecture with Domain, Application, Infrastructure, Interface layers
- CQRS pattern for separation of read/write operations
- Repository pattern for persistence abstraction
- FastAPI REST API with OpenAPI documentation
- ChromaDB vector storage for semantic search
- TDD unit tests for domain models
- Comprehensive type hints and docstrings
- Engineering standards: pyproject.toml, pytest, mypy, ruff configs

Tech Stack:
- Python 3.10+
- FastAPI + Uvicorn
- Pydantic v2
- ChromaDB
- sentence-transformers
- pytest for TDD"

# Show status
echo ""
echo "✅ Git repository initialized!"
echo ""
git status
echo ""

# Ask about remote
echo "=================================================="
echo "Next steps:"
echo "  1. Create repository on GitHub:"
echo "     https://github.com/new"
echo "     Repository name: tooling-rag"
echo ""
echo "  2. Add remote and push:"
echo "     git remote add origin git@github.com:nanfeng2021/tooling-rag.git"
echo "     git branch -M main"
echo "     git push -u origin main"
echo ""
echo "  3. Or use HTTPS:"
echo "     git remote add origin https://github.com/nanfeng2021/tooling-rag.git"
echo "     git push -u origin main"
echo "=================================================="
