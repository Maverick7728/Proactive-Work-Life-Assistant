# Proactive Work-Life Assistant — Project Overview

## 🚀 Purpose
A smart virtual assistant that helps you manage work-life tasks such as scheduling meetings, booking restaurants, checking team availability, and automating emails. It integrates with Google Calendar, Gmail, and restaurant/location APIs to streamline your workflow.

## ✨ Main Features
- **Natural Language Understanding:** Accepts high-level goals in plain English.
- **Meeting Scheduling:** Finds common free slots and sends calendar invites.
- **Restaurant Booking:** Searches and suggests restaurants based on preferences.
- **Availability Checking:** Checks and displays team members' schedules.
- **Email Automation:** Sends professional emails and notifications.
- **Beautiful UI:** Modern Streamlit interface for easy interaction.

## 🏗️ High-Level Architecture
- **Frontend:** Streamlit app (`app.py`) for user interaction.
- **Core Logic:** Modular Python classes for assistant, goal parsing, planning, and execution (`src/core/`).
- **Services:** Integrations for AI, calendar, email, location, and restaurants (`src/services/`).
- **Config & Data:** All credentials and tokens in `config/`; user and restaurant data in `data/`.

## 🛠️ Local Setup (Development)
1. **Clone the repository:**
   ```bash
   git clone <repository-url>
   cd <project-folder>
   ```
2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```
3. **Configure environment:**
   - Copy `config/env_template.txt` to `config/.env` and fill in your API keys and credentials.
   - Place your Google Calendar token at `config/cal_token.json`.
4. **Run the app:**
   ```bash
   streamlit run app.py
   # or
   python run.py
   ```

## 📚 More Info
- See `README.md` and `API_SETUP.md` for detailed setup and usage instructions.
- Explore the `src/` directory for core logic and service integrations.

