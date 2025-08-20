📦 Kwork Fresh Wants Bot

A Telegram bot with a user-friendly interface for parsing the latest projects from the freelance marketplace Kwork
.
It helps freelancers stay up to date with new projects in selected categories and get instant notifications in Telegram.

✨ Features

🔎 Fetch the latest projects from Kwork

🗂 Interactive category selection via Telegram inline menu

⚙️ Manage parsing directly from the bot (start/stop)

⏱ Set custom parsing frequency

💬 Receive project notifications in real time

🧩 Clear layered architecture (Presentation, Business, Infrastructure, Domain)

🛠 Tech Stack

🐍 Python 3.13

🤖 Aiogram — Telegram bot framework

🏗 Pydantic — data & config validation

📦 Poetry — dependency management

🧪 Pytest — tests

🧩 Layered architecture (modular design for scalability & maintainability)

🚀 Installation
1. Clone the repository
git clone https://github.com/username/kwork-fresh-wants.git
cd kwork-fresh-wants

2. Install dependencies with Poetry
poetry install

3. Configure environment

Create a .env file:

BOT_TOKEN=your_telegram_bot_token

4. Run the bot
poetry run python src/main.py

📂 Project Structure
src/
├── bot/                  # Presentation layer (Telegram interface)
│   ├── handlers.py       # Aiogram handlers
│   ├── keyboards.py      # Inline/reply keyboards
│   ├── middlewares.py    # Middlewares
│   ├── states.py         # FSM states
│   ├── texts.py          # Static bot texts
│   └── services/         # Bot-level services (menus, state mgmt, parsing trigger)
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

🧪 Tests

Run tests with:

poetry run pytest

📜 License

This project is created for educational purposes.
Feel free to use, modify, and improve 🚀
