# jobPosting Structured Data → API Request Net-Empregos

This project automates the process of **extracting jobPosting structured data** (Schema.org format) from a website and **sending it as a job advertisement to the Net Empregos API**.  

It was built to simplify job distribution: instead of manually posting jobs, you can map structured data directly into the Net Empregos system via an automated script.

---

## 🚀 Features

- Parses **jobPosting structured data (JSON-LD / microdata)** from webpages.  
- Maps extracted fields into the **Net Empregos API** format.  
- Submits job offers automatically via HTTP requests.  
- Logging included for debugging and monitoring requests.  

---

## 🛠️ Technologies Used

- **Python 3**  
- `requests` – for API calls  
- `xml.etree.ElementTree` – handling structured data if XML is used  
- `dotenv` – environment variable management  
- `logging` – request/error logging  

---

## File Structure

- [main.py](https://github.com/srdobolo/API-Request-Net-Empregos/blob/main/main.py): Entry point of the application.
- [data_cleaning.py](https://github.com/srdobolo/API-Request-Net-Empregos/blob/main/data_cleaning.py): Functions to sanitize and prepare job data.
- [Remove_Request.py](https://github.com/srdobolo/API-Request-Net-Empregos/blob/main/Remove_Request.py): Handles the removal of job postings (if implemented).
- [mapping.json](https://github.com/srdobolo/API-Request-Net-Empregos/blob/main/mapping.json): JSON file mapping internal job fields to Net-Empregos format.
- [requirements.txt](https://github.com/srdobolo/API-Request-Net-Empregos/blob/main/requirements.txt): Python dependencies.
- [requirements_linux.txt](https://github.com/srdobolo/API-Request-Net-Empregos/blob/main/requirements_linux.txt): Dependencies tailored for Linux.
- [Net-Empregos Interface.doc.pdf](https://github.com/srdobolo/API-Request-Net-Empregos/blob/main/Net-Empregos%20Interface.doc.pdf): Documentation for the Net-Empregos interface.

## Installation

1. **Clone the repository**:

   ```bash
   git clone https://github.com/srdobolo/API-Request-Net-Empregos.git
   cd API-Request-Net-Empregos

2. **Create a virtual environment (optional but recommended)**:

   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate

3. **Install dependencies**:

- For general use:

   ```bash
   pip install -r requirements.txt

- For Linux systems:

   ```bash
   pip install -r requirements_linux.txt

## Configuration

1. **Set the API access key**:

You can either:

- Set it in the shell:

   ```bash
   export API_ACCESS_KEY='your_api_key_here'

- Or create a .env file:

   ```bash
   echo "API_ACCESS_KEY=your_api_key_here" > .env

2.**Configure mapping.json**:

This file maps your internal job fields to the format expected by Net-Empregos.
Ensure it's correctly set up before running the script.

## Usage

- To run the main script:

   ```bash
   python main.py

The script will:

- Read job data
- Clean and format it
- Map fields via mapping.json
- Submit job listings to Net-Empregos

---

## 🔄 Automation with GitHub Actions

This project is fully automated using **GitHub Actions**:

```bash
.github/workflows/actions.yml
```

- The script runs automatically on a defined schedule.

```bash
on:
  schedule:
    - cron: '30 11 * * *'  # 12:30 local (UTC+1)
    - cron: '30 18 * * *'  # 19:30 local (UTC+1) on weekdays}
```

- Jobs are fetched from [Recruityard](https://www.recruityard.com/find-jobs-all/) and posted to **Net Empregos** without manual intervention.  
- Logs are available in the GitHub Actions console for easy monitoring.  
- API keys and sensitive data are managed securely with **GitHub Secrets**.  

This means you don’t need to run the script locally — GitHub handles the **CI/CD (Continuous Integration / Continuous Deployment)** pipeline for you.

---

## ⚠️ Limitations

This script is designed and tested primarily with the **Recruityard job board**, and it works reliably with structured data in that format.  
However, **not all jobPosting structured data is the same**. Different websites can represent the schema in different ways, which may cause issues.

### Current Assumptions

- `identifier` is always an object with `{ "value": "..." }` (sometimes it is just a string or inside `@id`).
- `industry`, `employmentType`, `jobLocation` and other fields are always present and consistently structured.
- Each job page contains a **single JobPosting** inside a `<script type="application/ld+json">`.
- `description` is in HTML and cleaned using `simplify_html`.

### Possible Issues on Other Websites

- `JobPosting` may appear inside a list (`@graph`) or an array of objects.
- Some fields may be strings, objects, or arrays — the current code does not handle all variations.
- Some pages embed **multiple JobPosting objects** in a single JSON-LD block.
- Missing optional fields can lead to errors or incorrect mapping.

---

## 💡 Suggested Improvements

To make this project work with a wider variety of job boards:

- Add a flexible `extract_job_posting()` function to handle lists, arrays, and `@graph`.
- Implement fallbacks for fields (`identifier`, `industry`, etc.) whether they are strings, dicts, or arrays.
- Support multiple job postings per page instead of assuming only one.
- Improve logging (e.g., save failed payloads to CSV/JSON for analysis).
- Optional: switch to asynchronous requests to speed up large batches.

---

## Troubleshooting

- Error: API_ACCESS_KEY is not set in the environment or .env file.
→ Make sure the key is set either in the shell or a .env file in the project root.

- Process completed with exit code 1
→ This indicates an error during execution. Check console output and ensure configurations are correct.

## License

This project is licensed under the MIT License.
