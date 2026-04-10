#!/bin/bash

# Backend
cd ./backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver 8000

# Frontend
cd ./frontend
npm install
npm run dev