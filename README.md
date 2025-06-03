# API-Request-Net-Empregos

This Python project automates job postings on [Net-Empregos](https://www.net-empregos.com/), a prominent job portal in Portugal.  
It streamlines the process of submitting job listings, ensuring efficiency and consistency.

## Features

- **Automated Job Posting**: Programmatically submit job listings to Net-Empregos.
- **Data Cleaning**: Sanitize and prepare job data for submission.
- **Configurable Mappings**: Use `mapping.json` to map internal job fields to Net-Empregos' expected format.
- **Error Handling**: Gracefully handle and log errors during the posting process.

## Prerequisites

- Python 3.8 or higher
- A Net-Empregos account with API access
- API access key set as an environment variable

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

2. **Configure mapping.json**:

This file maps your internal job fields to the format expected by Net-Empregos.
Ensure it's correctly set up before running the script.

## Usage

    - For general use:
   ```bash
   pip install -r requirements.txt

    - For Linux systems:
   ```bash
   pip install -r requirements_linux.txt