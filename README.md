Getting Started

prerequisite
Python 3.10+
Git
(Optional but recommended) VS Code or any editor

Clone the repository
git clone https://github.com/Athan-K/CIS-5800-HR-System.git
cd CIS-5800-HR-System

Create and activate a virtual environment
- python -m venv venv
Windows:
- venv\Scripts\activate
macOS/Linux:
- source venv/bin/activate

Install dependencies
- pip install -r requirements.txt

Apply migrations
- python manage.py migrate

Create a superuser (for HR/admin)
- python manage.py createsuperuser
- Use an email like: admin@ethos.com
