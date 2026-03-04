# improc-hybridization

> A hybrid image-processing pipeline that **decomposes** YOLOv8, OpenCV, and SAM into fine-grained decision blocks, **connects** them with lightweight glue adapters, and **interleaves** them into a single configurable workflow — proving that blocks from different AI tools can be mixed freely rather than chained tool-by-tool.

---

## Architecture at a Glance

```
┌──────────────────────────────────────────────────────────────────┐
│  web/          Vue 3 + Vite frontend                             │
│  ┌──────────┐  ┌────────────────┐  ┌────────────────┐            │
│  │BlockList │→ │ PipelineCanvas │→│  ResultsPanel   │            │
│  └──────────┘  └────────────────┘  └────────────────┘            │
│ drag & drop block builder  ·  reorder  ·  execute                │
├──────────────────────────────────────────────────────────────────┤
│  app/          FastAPI backend                                   │
│  GET /api/blocks          — introspect available blocks          │
│  POST /api/pipeline/run   — execute pipeline with image          │
│  GET /api/pipeline/fetch-image — proxy external images           │
├──────────────────────────────────────────────────────────────────┤
│  src/          Core pipeline library                             │
│  blocks/       7 decomposed decision blocks (YOLO · OpenCV · SAM)│
│  glue/         4 adapter blocks (format · crop · prompt · viz)   │
│  pipeline/     Sequential runner with shared-state threading     │
└──────────────────────────────────────────────────────────────────┘
```

---

## Table of Contents

1. [Tool Decomposition](#1-tool-decomposition)
2. [Glue Blocks](#2-glue-blocks)
3. [The Hybridized Pipeline](#3-the-hybridized-pipeline)
4. [Project Structure](#project-structure)
5. [Quick Start](#quick-start)
6. [API Reference](#api-reference)
7. [License](#license)

---

## 1. Tool Decomposition

Each monolithic AI tool was **broken apart** into small, single-responsibility *decision blocks* that share one strict contract:

```python
class Block(ABC):
    def __call__(self, data: dict) -> dict: ...
```

Every block receives a pipeline-state dictionary, reads only the keys it needs, and returns a new dictionary with its outputs added. No hidden state, no implicit mutation.

### 1.1 YOLO Blocks (`src/blocks/yolo/`)

A typical `model.predict()` call bundles inference, score filtering, and NMS into one opaque step. Here that is split into three independently reorderable blocks:

| Block | What it does | Key inputs | Key outputs |
|---|---|---|---|
| **`YOLODetect`** | Runs YOLOv8 forward pass and exposes raw intermediates | `image` | `raw_boxes`, `raw_scores`, `raw_classes` |
| **`ConfidenceFilter`** | Keeps detections above a score threshold | `raw_boxes`, `raw_scores`, `raw_classes` | `boxes`, `scores`, `classes` |
| **`ClassFilter`** | Keeps only detections belonging to an allowed set of class IDs | `boxes`, `scores`, `classes` | `boxes`, `scores`, `classes` (filtered) |

> **Why decompose?** — Because `ClassFilter` can now appear *after* OpenCV geometric filters. In a monolithic YOLO call you cannot insert external logic between confidence thresholding and class filtering.

### 1.2 OpenCV Blocks (`src/blocks/opencv/`)

Deterministic, rule-based blocks that apply classical computer-vision logic to intermediate results produced by *any* upstream block:

| Block | What it does | Key inputs | Key outputs |
|---|---|---|---|
| **`BoxAreaFilter`** | Discards bounding boxes whose pixel area is below a threshold | `boxes`, `scores`, `classes` | `boxes`, `scores`, `classes` (pruned) |
| **`AspectRatioFilter`** | Discards boxes with degenerate width / height ratios | `boxes`, `scores`, `classes` | `boxes`, `scores`, `classes` (pruned) |
| **`EdgeDensityScorer`** | Computes Canny edge density on each cropped region (post-crop analysis) | `crops` | `edge_densities` |

### 1.3 SAM Block (`src/blocks/sam/`)

| Block | What it does | Key inputs | Key outputs |
|---|---|---|---|
| **`SAMSegment`** | Generates segmentation masks for each crop via Segment Anything (ultralytics) | `crops`, optional `point_prompts` | `masks` |

SAM is reduced to *only* mask generation. Prompt derivation is delegated to a glue block, keeping the SAM block focused and composable.

---

## 2. Glue Blocks

Blocks from different tool ecosystems speak different data languages - YOLO produces `(N, 4)` bounding boxes while SAM expects point prompts relative to a crop. **Glue blocks** are lightweight adapters that reshape, convert, or visualize data to bridge these gaps. They follow the exact same `Block` interface.

```
src/glue/
├── crop_regions.py         # detection boxes  →  image patches
├── box_to_point_prompt.py  # YOLO box centers →  SAM point prompts
├── normalize_boxes.py      # absolute pixels  →  [0, 1] coordinates
└── visualize.py            # pipeline state   →  annotated image (base64)
```

| Glue Block | Bridges | Key inputs → Key outputs |
|---|---|---|
| **`CropRegions`** | Whole-image detection → per-region analysis | `image` + `boxes` → `crops` |
| **`BoxToPointPrompt`** | YOLO geometry → SAM prompting interface | `boxes` → `point_prompts` |
| **`NormalizeBoxes`** | Absolute pixel coords → normalized `[0, 1]` coords | `image` + `boxes` → `boxes_normalized` |
| **`VisualizeResults`** | Pipeline state → human-readable output | `image` + `boxes` + `masks` → `output_base64` |

### Why separate glue blocks?

Without them you would hard-code format conversion inside the tool blocks themselves, coupling YOLO to SAM's API or OpenCV to YOLO's coordinate system. By externalizing these transformations:

- **Tool blocks stay pure** — `YOLODetect` knows nothing about SAM or crops.
- **Glue is optional and swappable** — you can skip `NormalizeBoxes` if downstream blocks work with absolute coordinates, or replace `BoxToPointPrompt` with a different prompting strategy.
- **The pipeline stays reconfigurable** — the user can drag-and-drop blocks in any sensible order via the web UI.

---

## 3. The Hybridized Pipeline

### 3.1 The Runner

`src/pipeline/runner.py` implements a simple sequential executor:

```python
class Pipeline:
    def run(self, data: dict) -> dict:
        for block in self.blocks:
            data = block(data)   # pass the shared state forward
        return data
```

A single **shared-state dictionary** is threaded through every block. Each block reads what it needs and writes what it produces — no DAG scheduler, no message bus. The architecture is deliberately minimal because the innovation is in the *block ordering*, not the execution engine.

### 3.2 Interleaved Block Ordering

The default pipeline demonstrates **true hybridization** — blocks from different tools are interleaved wherever it makes architectural sense:

```
Step  Block                Tool      Phase
────  ───────────────────  ────────  ──────────────────────
 1    YOLODetect           YOLO      Raw detection
 2    ConfidenceFilter     YOLO      Score thresholding
 3    BoxAreaFilter        OpenCV    Geometric area pruning    ← OpenCV between YOLO steps
 4    AspectRatioFilter    OpenCV    Shape-based pruning
 5    ClassFilter          YOLO      Class refilter            ← YOLO again, after OpenCV!
 6    CropRegions          Glue      Extract image patches
 7    BoxToPointPrompt     Glue      Derive SAM prompts
 8    EdgeDensityScorer    OpenCV    Edge analysis on crops    ← OpenCV after glue
 9    SAMSegment           SAM       Mask generation
10    VisualizeResults     Glue      Render final output
```

```
Tool trace:  YOLO → YOLO → OpenCV → OpenCV → YOLO → Glue → Glue → OpenCV → SAM → Glue
                                ▲                ▲                      ▲
                          interleaved       interleaved            interleaved
```

> **This is NOT** the naive sequential approach `All-YOLO → All-OpenCV → All-SAM`. The key architectural point is that OpenCV geometric filters sit *between* YOLO's confidence filter and class filter, and another OpenCV block (edge density) runs *after* the glue cropping step but *before* SAM segmentation.

### 3.3 Data Flow Through the Pipeline

```
image
  │
  ▼
┌─────────────┐  raw_boxes, raw_scores, raw_classes
│ YOLODetect  │──────────────────────────────────────┐
└─────────────┘                                      │
  ▼                                                  │
┌──────────────────┐  boxes, scores, classes         │
│ ConfidenceFilter │──────────────────────┐          │
└──────────────────┘                      │          │
  ▼                                       │          │
┌────────────────┐  boxes (pruned)        │          │
│ BoxAreaFilter  │────────────┐           │          │
└────────────────┘            │           │          │
  ▼                           │           │          │
┌────────────────────┐        │           │          │
│ AspectRatioFilter  │────────┘           │          │
└────────────────────┘                    │          │
  ▼                                       │          │
┌──────────────┐  boxes (class-filtered)  │          │
│ ClassFilter  │──────────────────────────┘          │
└──────────────┘                                     │
  ▼                                                  │
┌──────────────┐  crops                              │
│ CropRegions  │──────────────────────┐              │
└──────────────┘                      │              │
  ▼                                   │              │
┌───────────────────┐  point_prompts  │              │
│ BoxToPointPrompt  │──────────┐      │              │
└───────────────────┘          │      │              │
  ▼                            │      │              │
┌─────────────────────┐        │      │              │
│ EdgeDensityScorer   │ edge_densities│              │
└─────────────────────┘        │      │              │
  ▼                            │      │              │
┌──────────────┐  masks        │      │              │
│  SAMSegment  │───────────────┘      │              │
└──────────────┘                      │              │
  ▼                                   │              │
┌────────────────────┐                │              │
│ VisualizeResults   │  output_base64 │              │
└────────────────────┘────────────────┘──────────────┘
```

### 3.4 Web UI — Visual Pipeline Builder

The Vue 3 frontend (`web/`) makes the hybridized pipeline tangible:

- **Block palette** (left panel) — lists all available blocks grouped by category (YOLO / OpenCV / SAM / Glue), fetched dynamically from the `/api/blocks` introspection endpoint.
- **Pipeline canvas** (center) — drag-and-drop block ordering with inline parameter editing. Users can reorder blocks to create different hybridization strategies.
- **Results panel** (right) — upload or paste an image URL, execute the pipeline, and view annotated results (bounding boxes + SAM masks overlaid).
- **Sample loader** — one-click loads a pre-configured hybrid pipeline with a sample image for instant demonstration.

---

## Project Structure

```
improc-hybridization/
│
├── src/                          # Core pipeline library
│   ├── blocks/
│   │   ├── base.py               # Block ABC — the universal contract
│   │   ├── yolo/
│   │   │   ├── detect.py         # YOLODetect — raw inference
│   │   │   ├── confidence_filter.py  # ConfidenceFilter — score threshold
│   │   │   └── class_filter.py   # ClassFilter — class ID filter
│   │   ├── opencv/
│   │   │   ├── box_area_filter.py    # BoxAreaFilter — area pruning
│   │   │   ├── aspect_ratio_filter.py # AspectRatioFilter — shape pruning
│   │   │   └── edge_density.py   # EdgeDensityScorer — Canny analysis
│   │   └── sam/
│   │       └── segment.py        # SAMSegment — mask generation
│   ├── glue/
│   │   ├── crop_regions.py       # CropRegions — box → image patches
│   │   ├── box_to_point_prompt.py # BoxToPointPrompt — box → SAM prompt
│   │   ├── normalize_boxes.py    # NormalizeBoxes — pixel → [0,1]
│   │   └── visualize.py          # VisualizeResults — render output
│   ├── pipeline/
│   │   └── runner.py             # Pipeline — sequential block executor
│   ├── run_pipeline.py           # CLI demo script
│   └── requirements.txt
│
├── app/                          # FastAPI backend
│   ├── main.py                   # App entry point + CORS config
│   ├── models.py                 # Pydantic request / response schemas
│   ├── api/
│   │   ├── blocks.py             # GET /api/blocks — block introspection
│   │   └── pipeline.py           # POST /api/pipeline/run — execution
│   ├── services/
│   │   ├── block_introspector.py # Schema extraction for all blocks
│   │   └── pipeline_runner.py    # Dynamic block instantiation + execution
│   └── requirements.txt
│
└── web/                          # Vue 3 frontend
    ├── src/
    │   ├── App.vue               # Root layout
    │   ├── components/
    │   │   ├── BlockList.vue     # Available blocks palette
    │   │   ├── BlockItem.vue     # Individual block card
    │   │   ├── PipelineCanvas.vue # Drag-and-drop pipeline builder
    │   │   └── ResultsPanel.vue  # Image upload + result display
    │   └── composables/
    │       └── usePipeline.js    # Shared reactive state + API calls
    └── package.json
```

---

## Quick Start

### Prerequisites

- Python 3.10+
- Node.js 18+ and pnpm (or npm)

### 1. Clone

```bash
git clone https://github.com/ledinhtri97/improc-hybridization.git
cd improc-hybridization
```

### 2. Backend

```bash
python3 -m venv venv
source venv/bin/activate          # Windows: .\venv\Scripts\Activate.ps1
pip install -r app/requirements.txt
pip install -r src/requirements.txt
```

### 3. Frontend

```bash
cd web
pnpm install                      # or: npm install
```

### 4. Run

**Terminal 1 — API server:**

```bash
source venv/bin/activate
cd app
python3 main.py                   # → http://localhost:8000
```

**Terminal 2 — Dev server:**

```bash
cd web
pnpm dev                          # → http://localhost:5173
```

### 5. Use

1. Open `http://localhost:5173`.
2. Click **Load Sample** to load a default hybrid pipeline with a sample image — or build your own by clicking blocks from the left palette.
3. Upload an image or paste a URL, then click **▶ Execute Pipeline**.

### CLI Demo (no web UI)

```bash
source venv/bin/activate
cd src
python run_pipeline.py --image path/to/image.jpg
```

---

## API Reference

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/blocks` | List all available blocks with parameter schemas |
| `GET` | `/api/blocks/{block_id}` | Get schema for a specific block |
| `POST` | `/api/pipeline/run` | Execute a pipeline (multipart: `blocks` JSON + `image` file) |
| `GET` | `/api/pipeline/fetch-image?url=` | Proxy-fetch an external image (CORS bypass) |

---

## License

See repository for license details.
