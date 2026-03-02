# Hybrid Pipeline

A hybrid image processing pipeline that interleaves YOLOv8, OpenCV, and SAM blocks into a single configurable workflow. Includes a FastAPI backend and a Vue 3 web interface for visual pipeline building and execution.

## Prerequisites

- Python 3.10+
- Node.js 18+ and pnpm (or npm)
- Git

## Project Structure

```
app/          # FastAPI backend (API server)
web/          # Vue 3 frontend (pipeline builder UI)
src/          # Core pipeline library (used by app/)
```

## Setup

### 1. Clone the repository

```bash
git clone https://github.com/ledinhtri97/improc-hybridization.git
cd improc-hybridization
```

### 2. Backend (app/)

Create a virtual environment and install dependencies:

**macOS / Linux**

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r app/requirements.txt
pip install -r src/requirements.txt
```

**Windows (PowerShell)**

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r app/requirements.txt
pip install -r src/requirements.txt
```

### 3. Frontend (web/)

```bash
cd web
pnpm install
```

If using npm instead of pnpm:

```bash
cd web
npm install
```

## Running the Application

Open two terminals from the project root.

### Terminal 1 -- Backend

**macOS / Linux**

```bash
source venv/bin/activate
cd app
python3 main.py
```

**Windows (PowerShell)**

```powershell
.\venv\Scripts\Activate.ps1
cd app
python main.py
```

The API will be available at `http://localhost:8000`. Interactive docs are at `http://localhost:8000/docs`.

### Terminal 2 -- Frontend

```bash
cd web
pnpm dev
```

Or with npm:

```bash
cd web
npm run dev
```

The UI will be available at `http://localhost:5173`.

## Usage

1. Open `http://localhost:5173` in a browser.
2. Click **Sample** in the Pipeline panel to load a default pipeline with a sample image, or build your own by clicking blocks from the left panel.
3. Upload an image using the file picker or paste an image URL and click **Load**.
4. Click **Execute Pipeline** to run the pipeline and view results.

## API Endpoints

| Method | Path                          | Description                        |
|--------|-------------------------------|------------------------------------|
| GET    | /api/blocks                   | List available processing blocks   |
| POST   | /api/pipeline/run             | Execute a pipeline with an image   |
| GET    | /api/pipeline/fetch-image?url=| Proxy-fetch an external image      |

## License

See repository for license details.
