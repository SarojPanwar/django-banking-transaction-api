# Django Banking Transaction API

A REST API built with Django REST Framework for managing bank accounts and transactions.

## Features
- User Registration and Login with Token Authentication
- Create and view bank accounts
- Deposit, Withdrawal and Transfer operations
- Transaction history with filtering

## Tech Stack
- Python
- Django
- Django REST Framework
- SQLite

## Setup Instructions
1. Clone the repo
2. Create virtual environment `python -m venv venv`
3. Activate it `venv\Scripts\activate`
4. Install dependencies `pip install -r requirements.txt`
5. Create `.env` file with `SECRET_KEY` and `DEBUG`
6. Run migrations `python manage.py migrate`
7. Run server `python manage.py runserver`

## API Endpoints
| Method | Endpoint | Description |
|---|---|---|
| POST | /api/register/ | Register new user |
| POST | /api/login/ | Login and get token |
| GET | /api/account/ | View account details |
| POST | /api/account/deposit/ | Deposit money |
| POST | /api/account/withdraw/ | Withdraw money |
| POST | /api/account/transfer/ | Transfer money |
| GET | /api/account/transactions/ | Transaction history |