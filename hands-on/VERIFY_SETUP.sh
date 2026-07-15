#!/bin/bash
# Setup Verification Script
# Run this to verify everything is installed and configured correctly

set -e

echo "================================"
echo "Setup Verification Checklist"
echo "================================"
echo ""

# Check 1: Python version
echo "✓ Checking Python version..."
python3 --version || { echo "✗ Python 3 not found"; exit 1; }
echo ""

# Check 2: Virtual environment
echo "✓ Checking virtual environment..."
if [ ! -d "venv" ]; then
    echo "✗ Virtual environment not found. Create it first:"
    echo "  python3 -m venv venv"
    exit 1
fi
echo "  venv directory found"
echo ""

# Check 3: Activate venv and check packages
echo "✓ Checking installed packages..."
source venv/bin/activate 2>/dev/null || { echo "✗ Failed to activate venv"; exit 1; }

packages=("anthropic" "fastapi" "uvicorn" "pandas" "sklearn" "joblib")
for package in "${packages[@]}"; do
    python -c "import ${package}" 2>/dev/null && echo "  ✓ ${package}" || { echo "  ✗ ${package} NOT installed"; }
done
echo ""

# Check 4: API Key
echo "✓ Checking API key..."
if [ -z "$ANTHROPIC_API_KEY" ]; then
    if [ -f ".env" ]; then
        echo "  .env file found but ANTHROPIC_API_KEY not in environment"
        echo "  Run: source .env  or  export ANTHROPIC_API_KEY=..."
    else
        echo "  ✗ ANTHROPIC_API_KEY not set and no .env file"
        echo "  Create .env file or run:"
        echo "    export ANTHROPIC_API_KEY='sk-ant-YOUR-KEY'"
    fi
else
    key_preview="${ANTHROPIC_API_KEY:0:10}...${ANTHROPIC_API_KEY: -5}"
    echo "  ✓ API key set: $key_preview"
fi
echo ""

# Check 5: Model files
echo "✓ Checking model files..."
if [ -f "models/prospect_model.joblib" ]; then
    echo "  ✓ models/prospect_model.joblib found"
else
    echo "  ✗ models/prospect_model.joblib not found"
    echo "  Run: python ml11_train_and_save_prospect_model.py"
fi

if [ -f "models/prospect_model.json" ]; then
    echo "  ✓ models/prospect_model.json found"
else
    echo "  ✗ models/prospect_model.json not found"
    echo "  Run: python ml11_train_and_save_prospect_model.py"
fi
echo ""

# Check 6: Required data files
echo "✓ Checking data files..."
if [ -f "data/leads.csv" ]; then
    echo "  ✓ data/leads.csv found"
else
    echo "  ✗ data/leads.csv not found"
fi
echo ""

# Check 7: Script files
echo "✓ Checking script files..."
scripts=("prompt01_hello_world.py" "prompt02_conversation.py" "prompt03_system_prompt.py" "prompt04_structured_output.py" "prompt05_temperature.py" "serve.py" "ml11_train_and_save_prospect_model.py")
for script in "${scripts[@]}"; do
    if [ -f "$script" ]; then
        echo "  ✓ $script"
    else
        echo "  ✗ $script NOT found"
    fi
done
echo ""

# Check 8: React files
echo "✓ Checking React files..."
react_files=("static/index.html" "static/step1.html" "static/step2.html" "static/step6.html")
for file in "${react_files[@]}"; do
    if [ -f "$file" ]; then
        echo "  ✓ $file"
    else
        echo "  ✗ $file NOT found"
    fi
done
echo ""

# Summary
echo "================================"
echo "Summary"
echo "================================"
echo ""
echo "Next steps:"
echo "1. Make sure all packages show ✓ above"
echo "2. If any packages failed, run:"
echo "   source venv/bin/activate"
echo "   pip install anthropic fastapi uvicorn pandas scikit-learn joblib"
echo ""
echo "3. Set your API key (if not set):"
echo "   export ANTHROPIC_API_KEY='sk-ant-YOUR-KEY'"
echo ""
echo "4. Train the model (if not found):"
echo "   source venv/bin/activate"
echo "   python ml11_train_and_save_prospect_model.py"
echo ""
echo "5. Start the server:"
echo "   source venv/bin/activate"
echo "   uvicorn serve:app --reload"
echo ""
echo "6. Open in browser:"
echo "   http://127.0.0.1:8000"
echo ""
echo "7. Run a prompt script (in another terminal):"
echo "   source venv/bin/activate"
echo "   python prompt01_hello_world.py"
echo ""
echo "================================"
