#!/bin/bash

# Exit on error
set -e

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${YELLOW}=== Setting up Django File Share Application ===${NC}"

# Create and activate virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo -e "${GREEN}Creating virtual environment...${NC}"
    python -m venv venv
    source venv/Scripts/activate
    
    # Upgrade pip
    echo -e "${GREEN}Upgrading pip...${NC}"
    pip install --upgrade pip
    
    # Install dependencies
    echo -e "${GREEN}Installing dependencies...${NC}"
    pip install -r requirements.txt
else
    echo -e "${GREEN}Activating virtual environment...${NC}"
    source venv/Scripts/activate
fi

# Create .env file if it doesn't exist
if [ ! -f ".env" ]; then
    echo -e "${GREEN}Creating .env file...${NC}"
    cat > .env <<EOL
# Django Settings
DEBUG=True
SECRET_KEY=$(python -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())')
ALLOWED_HOSTS=localhost,127.0.0.1

# Database
DB_NAME=db.sqlite3
DB_USER=
DB_PASSWORD=
DB_HOST=localhost
DB_PORT=

# Email Settings (for password reset, etc.)
EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend
EMAIL_HOST=localhost
EMAIL_PORT=25
EMAIL_USE_TLS=False
DEFAULT_FROM_EMAIL=webmaster@localhost
EOL
    echo -e "${GREEN}Created .env file with a random SECRET_KEY${NC}"
fi

# Load environment variables
echo -e "${GREEN}Loading environment variables...${NC}
set -a
source .env
set +a

# Apply database migrations
echo -e "${GREEN}Applying database migrations...${NC}
python manage.py migrate

# Create superuser if it doesn't exist
if [ "$1" = "--create-superuser" ] || [ "$1" = "-c" ]; then
    echo -e "${GREEN}Creating superuser...${NC}"
    python manage.py createsuperuserwithprofile --username=admin --email=admin@example.com --password=admin123 --noinput
    echo -e "${GREEN}Superuser created with username 'admin' and password 'admin123'${NC}
    echo -e "${YELLOW}WARNING: Please change the default password immediately!${NC}"
fi

# Collect static files
echo -e "${GREEN}Collecting static files...${NC}
python manage.py collectstatic --noinput

echo -e "${GREEN}Setup complete!${NC}"
echo -e "${YELLOW}To start the development server, run:${NC}"
echo -e "  source venv/Scripts/activate && python manage.py runserver"
echo -e "\n${YELLOW}Then open http://127.0.0.1:8000 in your browser.${NC}"
