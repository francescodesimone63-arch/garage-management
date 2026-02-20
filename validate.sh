#!/bin/bash

# ============================================================================
# Script di validazione backend e frontend
# Esegue test e diagnostica per identificare rapidamente i problemi
# ============================================================================

set -e

WORKSPACE="/Users/francescodesimone/Sviluppo Python/garage-management"
BACKEND_DIR="$WORKSPACE/backend"
FRONTEND_DIR="$WORKSPACE/frontend"

# Colori per output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}╔════════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║         🔍 Garage Management System - Debug Validator         ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════════════╝${NC}"
echo ""

# ============================================================================
# 1. BACKEND CHECKS
# ============================================================================

echo -e "${BLUE}[1/5]${NC} Checking Backend Installation..."
cd "$BACKEND_DIR"

if [ ! -d "venv" ]; then
    echo -e "${RED}❌ Virtual environment not found${NC}"
    exit 1
fi

source venv/bin/activate

# Check Python version
PYTHON_VERSION=$(python3 --version 2>&1)
echo -e "${GREEN}✅ Python${NC} $PYTHON_VERSION"

# Check required packages
echo -e "${BLUE}Checking dependencies...${NC}"
python3 -c "
import sys
required_packages = ['fastapi', 'sqlalchemy', 'pydantic', 'uvicorn']
missing = []
for pkg in required_packages:
    try:
        __import__(pkg)
        print(f'  ✅ {pkg}')
    except ImportError:
        print(f'  ❌ {pkg}')
        missing.append(pkg)

if missing:
    print(f'\n❌ Missing packages: {missing}')
    sys.exit(1)
" || exit 1

# Check database
echo -e "${BLUE}Checking database...${NC}"
if [ ! -f "db.sqlite3" ]; then
    echo -e "${YELLOW}⚠️  Database not found - will be created on startup${NC}"
else
    echo -e "${GREEN}✅ Database exists${NC}"
fi

# Check logging middleware
echo -e "${BLUE}Checking middleware...${NC}"
if grep -q "DebugMiddleware" main.py; then
    echo -e "${GREEN}✅ Debug middleware configured${NC}"
else
    echo -e "${YELLOW}⚠️  Debug middleware not configured${NC}"
fi

# ============================================================================
# 2. FRONTEND CHECKS
# ============================================================================

echo ""
echo -e "${BLUE}[2/5]${NC} Checking Frontend Installation..."
cd "$FRONTEND_DIR"

if [ ! -d "node_modules" ]; then
    echo -e "${YELLOW}⚠️  node_modules not found - run npm install${NC}"
else
    echo -e "${GREEN}✅ Dependencies installed${NC}"
fi

# Check required files
FILES_TO_CHECK=(
    "src/utils/errorTracker.ts"
    "src/hooks/useErrorTracking.ts"
    "src/components/DebugDashboard.tsx"
    "src/lib/axios.ts"
)

echo -e "${BLUE}Checking files...${NC}"
for file in "${FILES_TO_CHECK[@]}"; do
    if [ -f "$file" ]; then
        echo -e "${GREEN}✅ $file${NC}"
    else
        echo -e "${RED}❌ Missing: $file${NC}"
    fi
done

# ============================================================================
# 3. SERVICE STATUS
# ============================================================================

echo ""
echo -e "${BLUE}[3/5]${NC} Checking Service Status..."

# Backend
if curl -s http://localhost:8000/docs > /dev/null 2>&1; then
    echo -e "${GREEN}✅ Backend running on http://localhost:8000${NC}"
else
    echo -e "${RED}❌ Backend not responding${NC}"
    echo -e "   → Run: cd $WORKSPACE && bash START.sh"
fi

# Frontend
if curl -s http://localhost:3000 > /dev/null 2>&1; then
    echo -e "${GREEN}✅ Frontend running on http://localhost:3000${NC}"
else
    echo -e "${RED}❌ Frontend not responding${NC}"
    echo -e "   → Run: cd $WORKSPACE && bash START.sh"
fi

# ============================================================================
# 4. CORS CHECK
# ============================================================================

echo ""
echo -e "${BLUE}[4/5]${NC} Checking CORS Configuration..."

CORS_CHECK=$(curl -s -i -X OPTIONS http://localhost:8000/api/v1/vehicles/ \
  -H "Origin: http://localhost:3000" \
  -H "Access-Control-Request-Method: POST" 2>&1)

if echo "$CORS_CHECK" | grep -q "access-control-allow-origin: http://localhost:3000"; then
    echo -e "${GREEN}✅ CORS properly configured${NC}"
else
    echo -e "${RED}❌ CORS not working${NC}"
    echo -e "   → Check backend main.py middleware order"
fi

# ============================================================================
# 5. API ENDPOINTS
# ============================================================================

echo ""
echo -e "${BLUE}[5/5]${NC} Checking API Endpoints..."

ENDPOINTS=(
    "/api/v1/health"
    "/api/v1/vehicles/"
    "/api/v1/customers/"
    "/api/v1/work-orders/"
)

echo -e "${BLUE}Testing endpoints...${NC}"
for endpoint in "${ENDPOINTS[@]}"; do
    STATUS=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8000$endpoint 2>/dev/null)
    
    if [ "$STATUS" == "200" ] || [ "$STATUS" == "401" ] || [ "$STATUS" == "403" ]; then
        echo -e "${GREEN}✅ $endpoint ($STATUS)${NC}"
    else
        echo -e "${RED}❌ $endpoint ($STATUS)${NC}"
    fi
done

# ============================================================================
# Summary
# ============================================================================

echo ""
echo -e "${BLUE}╔════════════════════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}✅ Validation Complete!${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════════════╝${NC}"

echo ""
echo -e "${YELLOW}Debug Features Enabled:${NC}"
echo "  🐛 Debug Dashboard: Press Ctrl+Shift+D in browser"
echo "  📊 Real-time error tracking in browser console"
echo "  📝 Backend logs in: $BACKEND_DIR/logs/"
echo "  💾 API request logging enabled"

echo ""
echo -e "${YELLOW}Next Steps:${NC}"
echo "  1. Open http://localhost:3000 in browser"
echo "  2. Press Ctrl+Shift+D to open Debug Dashboard"
echo "  3. Perform the action that causes errors"
echo "  4. Check errors in Debug Dashboard"
echo "  5. Check backend logs for detailed error info"
echo ""

deactivate
