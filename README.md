# 📦 Kwork Fresh Wants Bot  

A Telegram bot with a user-friendly interface for parsing the latest projects from the freelance marketplace [Kwork](https://kwork.ru).  
It helps freelancers stay up to date with new projects in selected categories and get instant notifications in Telegram.  

---

## ✨ Features  

- 🔎 Fetch **the latest projects** from Kwork  
- 🗂 Interactive **category selection** via Telegram inline menu  
- ⚙️ Manage parsing directly from the bot (**start/stop**)  
- ⏱ Set custom **parsing frequency**  
- 💬 Receive project notifications in real time  
- 🧩 Clear **layered architecture** (Presentation, Business, Infrastructure, Domain)  

---

## 🛠 Tech Stack  

- 🐍 **Python 3.13**  
- 🤖 **Aiogram** — Telegram bot framework  
- 🏗 **Pydantic** — data & config validation  
- 📦 **Poetry** — dependency management  
- 🧩 **Layered architecture** — modular, scalable, maintainable  

---

## 📸 Screenshots
 <img width="467" height="119" alt="image" src="https://github.com/user-attachments/assets/8a88072a-c96f-4a2a-b80b-b75deba6bb10" />
 <img width="374" height="147" alt="image" src="https://github.com/user-attachments/assets/6f93b9ed-381c-416e-b9ad-22f2fe1b65a1" />
 <img width="443" height="445" alt="image" src="https://github.com/user-attachments/assets/65b8ea88-b7af-452d-88b7-2641f007700e" />
<img width="478" height="697" alt="image" src="https://github.com/user-attachments/assets/2a5fb4d4-7bbf-405a-92d0-cef585a41b26" />

---

## 🚀 Installation  

### 1. Clone the repository  
```bash
git clone https://github.com/username/kwork-fresh-wants.git
cd kwork-fresh-wants/src
```

### 2. Install dependencies with Poetry 
```bash
poetry install
```

### 3. Configure environment
```bash
BOT_CONFIG__TOKEN=your_telegram_bot_token
# ...other params from .env.template
```

### 4. Run the bot
```bash
poetry run python main.py
```

## 📂 Project Structure
```bash
src/
├── bot/                  # Presentation layer (Telegram interface)
│   ├── handlers.py       # Aiogram handlers
│   ├── keyboards.py      # Inline/reply keyboards
│   ├── states.py         # FSM states
│   ├── texts.py          # Static bot texts
│   └── services/         # Bot-level services (menus, state managment, parsing trigger)
│
├── business/             # Business logic layer
│   ├── category_rules.py
│   ├── project_filter.py
│   └── models/           # Domain models (Pydantic)
│       ├── category.py
│       └── project.py
│
├── services/             # Infrastructure layer
│   ├── kwork_api_service.py   # API requests
│   ├── parser_service.py      # Parsing logic
│   ├── saver_service.py       # Persistence
│   └── storage_service.py     # Storage layer
│
├── config.py             # App configuration
├── main.py               # Entry point
├── categories.json       # Kwork categories
└── users.json            # User data
```
