# 🛡️ SAFE-SQL v1.0

**Privacy-Preserving & Energy-Aware SQL Execution Engine**

SAFE-SQL is an advanced command-line SQL tool built atop PostgreSQL that integrates:

✔ Differential Privacy  
✔ Carbon Emission Tracking  
✔ Developer-grade CLI  
✔ Autocomplete & Command History  
✔ Execution Metrics & Diagnostics

It is designed for both academic and real-world usage — not just as a database client, but as a **privacy-aware, sustainability-aware SQL engine.**

---

## 🚀 Key Features

### 🌟 Product-Grade CLI

SAFE-SQL provides a professional terminal interface with:

- Branded ASCII banner at startup
- Colored prompts and styled output
- SQL autocomplete for keywords + table names
- Arrow key history navigation
- Animated execution spinner
- Execution time & emissions panel

### 🛡 Differential Privacy

Using a Laplace mechanism, SAFE-SQL applies noise to numeric query results, protecting sensitive data while still returning meaningful answers.

Example:

```sql
SELECT COUNT(*) FROM users;

returns a privatized result instead of exact counts.

🌍 Energy Awareness (CodeCarbon)

Every query measures and reports the estimated carbon emissions (in kg CO₂) using CodeCarbon, adding sustainability insights to query execution.

🧪 Real-Time Diagnostics

On launch, SAFE-SQL performs startup checks for:

Database connectivity

Differential privacy readiness

Energy tracker readiness

🧩 System Architecture
User SQL Input (prompt_toolkit)
        ↓
Spinner UI + Autocomplete
        ↓
EcoScheduler (Energy Tracking Starts)
        ↓
DatabaseInterface (psycopg2 executes query)
        ↓
Differential Privacy Layer (noise applied to result)
        ↓
EcoScheduler (Energy Tracking Stops)
        ↓
Rich CLI Output (Styled table + metrics)
🛠 Installation

Clone the repo:

git clone https://github.com/IamRSHC/SAFE-SQL.git
cd SAFE-SQL

Create & activate a Python virtual environment:

python -m venv venv
venv\Scripts\activate   # Windows
source venv/bin/activate  # macOS/Linux

Install dependencies:

pip install -r requirements.txt

Ensure PostgreSQL is installed & running

Create the database used by SAFE-SQL:

CREATE DATABASE safe_sql_db;
▶️ Using SAFE-SQL

Start the application:

python -m backend.main

Example session:

SQL > SELECT * FROM student_health LIMIT 10;
SQL > SELECT COUNT(age) FROM student_health;
SQL > exit

You’ll see:

Styled table output

Execution Time

Epsilon (privacy parameter)

Emissions in kg CO₂

🧠 Built-In Commands

SAFE-SQL supports normal SQL.

In addition:

Arrow keys for history

Tab autocomplete for SQL syntax + table names

exit to quit

Future expansions planned (e.g., \tables, \schema)

📁 Project Structure
SAFE-SQL/
│  README.md
│  requirements.txt
│
├─ backend/
│   ├─ main.py                 # CLI Interface
│   ├─ db.py                   # Database execution layer
│   ├─ privacy.py              # Differential privacy logic
│   ├─ eco_scheduler.py        # CodeCarbon integration
│   └─ .safe_sql_history       # Command history (auto)
📌 Differential Privacy

SAFE-SQL applies noise to numeric results using the Laplace mechanism with a configurable epsilon.
This ensures results reveal trends while preserving individual privacy.

Example:

True count: 200
Privatized count: 198.7321 (approx)
📌 Energy Tracking (CodeCarbon)

Each query logs a measurement of estimated CO₂ emissions produced by CPU cycles during query execution.

Useful for:

Sustainability reporting

Comparing query costs

Green computing awareness
```
