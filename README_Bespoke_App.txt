# Bespoke App

## Overview
Bespoke App is a custom-built solution designed with a focus on minimal UI, maximum performance, and robust version control. This project is built with modular components and adheres to strict testing and documentation standards.

---

## Features
- Clean, responsive, and accessible UI.
- Modular and testable component architecture.
- Optimized for speed and efficiency with minimal dependencies.
- Full version history with stable releases.

---

## Ground Rules
This project follows a strict set of ground rules to ensure consistency, quality, and clarity. See the **Bespoke App Ground Rules** for details:
- No unsolicited code changes or corrections.
- All logic and features must be tested before deployment.
- Clear documentation and structured code sections are mandatory.

---

## Installation
1. Clone the repository:
   ```bash
   git clone <repo-url>
   ```
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Start the development server locally:
   ```bash
   streamlit run app/main.py
   ```

---

## Deployment Workflow
- **All deployments on Render use `app/main.py` as the entry point.**
- If a new version is developed (e.g., `main_v26.py`), update the `Procfile` to:
  ```
  web: streamlit run app/main_v26.py
  ```
- Alternatively, rename the tested version to `main.py` before pushing changes.
- Commit changes to GitHub and Render will auto-deploy.

---

## Render Deployment Notes
- Render automatically reads the `Procfile` to determine the start command.
- The current Procfile contains:
  ```
  web: streamlit run app/main.py
  ```
- You **do not need to specify a start command manually** in the Render dashboard. If you prefer, you can enter `streamlit run app/main.py` as the start command.

---

## Usage
- Access the app locally via `http://localhost:8501` (Streamlit default).
- Follow the versioned changelog to stay updated on new features.

---

## Changelog
- **V25:** Latest stable version with core features.
- **V26 (in progress):** Upcoming features under testing.

---

## Contributing
- Discuss all changes before coding.
- Follow the section header convention:
  ```js
  // ==== SECTION NAME ==== //
  ```
- Submit changes to the staging branch for review and testing.

---

## Testing
- Run tests before any deployment:
   ```bash
   pytest
   ```
- All features must pass both logic and functional tests before merging.

---

## License
This project is proprietary and maintained under strict version control.
