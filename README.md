# Amazon Price Tracker

An automated web scraping tool that tracks Amazon product prices over time, stores the history in a PostgreSQL database, and generates visual price trend graphs. It is designed to run completely headlessly and automatically on an AWS EC2 instance.

## Features
* **Automated Scraping:** Uses Selenium WebDriver to reliably extract pricing data while bypassing basic bot detection.
* **Persistent Storage:** Saves daily price changes and timestamps to a PostgreSQL database.
* **Data Visualization:** Uses Pandas and Matplotlib to automatically generate a `prices.png` line graph showing price histories for tracked products.
* **Cloud Automation:** Configured to run daily in the background on an Amazon EC2 Linux instance using `cron`.

## Setup & Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/LiviuPtr/amazon_price_tracker.git
   cd amazon_price_tracker
   ```


2. Create a virtual environment and install dependencies:
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   ```

3. Set up your `.env` file with your database credentials:
   ```env
   db_host_url=your_db_host
   db_name_key=your_db_name
   db_user_key=your_db_user
   db_pass_key=your_password
   ```

## Usage
To run the scraper manually:
```bash
python3 main.py
```

**Automated Deployment (Linux/EC2):**
To run the script automatically every day at 8:00 AM, add the following to your `crontab`:
```bash
0 8 * * * cd /path/to/project && /path/to/.venv/bin/python3 main.py > /dev/null 2>&1
```