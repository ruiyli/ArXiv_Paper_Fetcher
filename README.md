# ArXiv Paper Fetcher

A Python toolkit for searching ArXiv papers by keywords and automatically publishing daily updates to a curated repository.

**Search Scope**: Mathematics, Computer Science, and Statistics.

## Project Structure

```
.
├── arxiv_fetcher.py                  # Core: keyword-based ArXiv paper fetcher
├── scripts/
│   └── daily_publisher.py            # Daily automation: fetch, format, and publish papers
├── .github/
│   └── workflows/
│       └── daily_update.yml          # GitHub Actions: scheduled daily pipeline
└── README.md
```

## Features

- **Keyword Search**: Search paper titles and abstracts via the ArXiv API
- **Server-Side Date Filtering**: Uses `submittedDate` in the API query for accurate date range results
- **Field Restriction**: Scoped to Mathematics (`math.*`), Computer Science (`cs.*`), and Statistics (`stat.*`)
- **Markdown Output**: Generates well-formatted Markdown with title, authors, date, categories, abstract, and links
- **Daily Automation**: GitHub Actions workflow fetches papers daily and pushes to a target repository ([Awesome-Flow-and-Diffusion-Daily](https://github.com/ruiyli/Awesome-Flow-and-Diffusion-Daily))
- **Archive Management**: Daily results are archived by month (`archives/YYYY-MM.md`)

## Installation

```bash
pip install feedparser
```

## Usage

### Manual Search

```bash
python arxiv_fetcher.py \
    --keywords "keyword1,keyword2" \
    --start-date "YYYY-MM-DD" \
    --end-date "YYYY-MM-DD" \
    --output "output.md" \
    --max-results 1000
```

#### Parameters

| Parameter | Required | Default | Description |
|-----------|----------|---------|-------------|
| `--keywords` | Yes | - | Comma-separated search keywords |
| `--start-date` | Yes | - | Start date (YYYY-MM-DD) |
| `--end-date` | Yes | - | End date (YYYY-MM-DD) |
| `--output` | No | `arxiv_papers.md` | Output filename |
| `--max-results` | No | `1000` | Maximum number of results |

#### Example

```bash
python arxiv_fetcher.py \
    --keywords "flow matching,diffusion" \
    --start-date "2026-01-01" \
    --end-date "2026-01-05" \
    --output "papers_20260101_20260105.md"
```

### Daily Automation (GitHub Actions)

The workflow (`.github/workflows/daily_update.yml`) runs at **1:00 AM UTC daily** and:

1. Checks out this repo and the target repo ([Awesome-Flow-and-Diffusion-Daily](https://github.com/ruiyli/Awesome-Flow-and-Diffusion-Daily))
2. Runs `scripts/daily_publisher.py` to fetch papers for the keywords: *Flow Matching*, *Diffusion Model*, *Score-based Generative Model*
3. Updates the target repo's `README.md` (latest section) and `archives/YYYY-MM.md`
4. Commits and pushes changes automatically

**Setup**: Add a `TARGET_REPO_TOKEN` secret in this repo's Settings > Secrets with a GitHub PAT that has write access to the target repo.

The workflow can also be triggered manually via `workflow_dispatch`.

## License

This tool is developed based on the original [arxiv-sanity-preserver](https://github.com/karpathy/arxiv-sanity-preserver) project and follows the same open source license.
