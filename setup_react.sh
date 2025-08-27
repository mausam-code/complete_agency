#!/bin/bash

# J.K. OVERSEAS PVT.LTD. React Frontend Setup Script

echo "🚀 Setting up React Frontend for J.K. OVERSEAS PVT.LTD. Management System"
echo "=================================================================="

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
    echo "❌ Node.js is not installed. Please install Node.js first."
    echo "Visit: https://nodejs.org/"
    exit 1
fi

# Check if npm is installed
if ! command -v npm &> /dev/null; then
    echo "❌ npm is not installed. Please install npm first."
    exit 1
fi

echo "✅ Node.js version: $(node --version)"
echo "✅ npm version: $(npm --version)"

# Navigate to frontend directory
cd frontend

echo ""
echo "📦 Installing React dependencies..."
echo "=================================="

# Install dependencies
npm install

echo ""
echo "🔧 Setting up development environment..."
echo "======================================="

# Create additional directories if they don't exist
mkdir -p src/components/{auth,common,dashboard,users,projects,tasks,attendance,hr}
mkdir -p src/hooks
mkdir -p src/utils
mkdir -p public

echo ""
echo "✅ React Frontend Setup Complete!"
echo "================================"
echo ""
echo "🎯 Next Steps:"
echo "1. Start the Django API server:"
echo "   python3 manage.py runserver"
echo ""
echo "2. Start the React development server:"
echo "   cd frontend && npm start"
echo ""
echo "3. Access the application:"
echo "   - React Frontend: http://localhost:3000"
echo "   - Django API: http://localhost:8000/api/docs/"
echo ""
echo "🔑 Demo Accounts:"
echo "- Super Admin: superadmin / admin123"
echo "- Admin: admin / admin123"
echo "- Employee: employee1 / emp123"
echo ""
echo "📚 Documentation:"
echo "- API Docs: http://localhost:8000/api/docs/"
echo "- Setup Guide: ./SETUP_GUIDE.md"
echo ""
echo "Happy coding! 🎉"
