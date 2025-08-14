# ArXiv Keyword Paper Fetcher

This is a concise Python script for searching ArXiv papers by keywords within a specified time range and saving results in Markdown format.

**Search Scope**: Limited to Mathematics, Computer Science, and Statistics fields only.

## Features

- 🔍 **Keyword Search**: Search for specified keywords in paper titles and abstracts
- 📚 **Field Restriction**: Search only Mathematics, Computer Science, and Statistics fields
- 📅 **Date Range Filter**: Support for specifying start and end dates
- 📝 **Markdown Output**: Generate well-formatted Markdown files
- 📊 **Detailed Information**: Include title, authors, publication date, categories, abstract, ArXiv links, etc.
- ⚡ **Rate Limiting**: Automatically control request frequency to avoid being limited by ArXiv servers

## Installation

Make sure you have the required Python packages installed:

```bash
pip install feedparser
```

## Usage

### Basic Syntax

```bash
python arxiv_fetcher.py --keywords "keyword1,keyword2" --start-date "start_date" --end-date "end_date" --output "output_filename"
```

### Parameters

- `--keywords`: Search keywords, separated by commas for multiple keywords
- `--start-date`: Start date, format YYYY-MM-DD
- `--end-date`: End date, format YYYY-MM-DD  
- `--output`: Output filename (optional, default: arxiv_papers.md)
- `--max-results`: Maximum number of search results (optional, default: 1000)

### Usage Examples

```bash
python arxiv_fetcher.py \
    --keywords "machine learning,deep learning,neural network" \
    --start-date "2024-01-01" \
    --end-date "2024-03-31" \
    --output "ml_papers_2024_q1.md" \
    --max-results 200
```

## Output Format

The generated Markdown file contains the following content:

1. **Document Header**
   - Search keywords
   - Search field restrictions
   - Date range
   - Number of papers found
   - Generation time

2. **Paper List**
   - Papers sorted by publication date
   - Detailed information for each paper: title, authors, publication date, categories, ArXiv ID, links, abstract

### Supported Academic Fields

**Mathematics (math.*)**:
- Algebraic Geometry (AG), Algebraic Topology (AT), Analysis (AP), Category Theory (CT), etc.

**Computer Science (cs.*)**:
- Artificial Intelligence (AI), Computational Linguistics (CL), Computer Vision (CV), Machine Learning (LG), etc.

**Statistics (stat.*)**:
- Applied Statistics (AP), Computational Statistics (CO), Machine Learning (ML), Statistical Theory (TH), etc.

## License

This tool is developed based on the original [arxiv-sanity-preserver](https://github.com/karpathy/arxiv-sanity-preserver) project and follows the same open source license.
