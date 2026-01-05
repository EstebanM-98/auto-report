# Auto Report Generator

An automated tool to generate monthly Excel activity reports based on Git commit history. It leverages **DeepSeek** or **Ollama (Local LLM)** to process technical commit messages into professional timesheet entries, distributing them intelligently to strictly align with working hours and holidays.

## Features

- **Commit Analysis**: Fetches history from multiple local Git repositories.
- **AI Processing**: Uses LLMs (DeepSeek or Ollama) to convert technical commits into professional task descriptions.
- **Smart Distribution**: 
  - Fills every business day of the target month.
  - **Strict Compliance**: Ensures exactly 8 hours per day, with individual tasks constrained between **0.5 to 3 hours**.
  - Handles gaps by automatically generating relevant technical maintenance tasks.
- **Excel Generation**: Outputs to a standardized template (`Seguimiento de actividades 2026.xlsx`).
- **Language Support**: Configurable output language (English/Spanish).

## Requirements

- Python 3.10+
- **Ollama** (for free local usage) OR an **DeepSeek API Key**.
- Recommended Model: `llama3.2` (Lightweight, 3B parameters).

## Installation

1. **Clone the repository**:
   ```bash
   git clone <repo-url>
   cd auto-report
   ```

2. **Set up Virtual Environment**:
   ```bash
   python -m venv venv
   # Windows
   venv\Scripts\activate
   # Mac/Linux
   source venv/bin/activate
   ```

3. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Configuration**:
   - Edit `src/config/settings.py`:
     - `REPO_LIST`: Add absolute paths to your local repositories.
     - `DEFAULT_CLIENT_PROJECT`: Name of the client/project.
     - `LANGUAGE`: `"es"` for Spanish (default), `"en"` for English.
     - `USE_OLLAMA`: Set to `True` for local LLM.
     - `OLLAMA_MODEL`: Default is `"llama3.2"`.

## Usage

### 1. Setup Ollama (If using local LLM)
Ensure Ollama is installed and running:
```bash
ollama pull llama3.2
ollama serve
```

### 2. Generate Report
Run the main script specifying the target month and year:

```bash
# Example: Generate report for January 2026
python -m src.main --month 1 --year 2026
```

### Options
- `--dry-run`: Preview tasks in console without writing to Excel.
- `--repo "PATH"`: Temporarily add a repository for this run.

## Logs
Detailed logs of LLM interactions (Inputs/Outputs) are saved in the `logs/` directory for debugging and transparency.

## Project Structure
- `src/core/`: Main logic (Git Client, LLM Processor, Distributor, Excel Manager).
- `src/config/`: Configuration settings.
- `src/utils/`: Date and holiday utilities.
- `src/static/`: Excel templates.

## Author
Developed for automated consultancy reporting.
