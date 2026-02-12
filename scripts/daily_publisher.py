import os
import sys
import re
import datetime
import argparse

# --- 1. dynamically import arxiv_fetcher from parent directory ---
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)

try:
    from arxiv_fetcher import fetch_papers_by_keywords
except ImportError:
    print("Error: Could not import arxiv_fetcher. Make sure the script is in a subdirectory of the repo.")
    sys.exit(1)

# --- 2. helper functions ---

def extract_github_link(text):
    """Extract the first GitHub link from text"""
    # match https://github.com/username/repo format
    pattern = r'(https?://github\.com/[\w-]+/[\w.-]+)'
    match = re.search(pattern, text)
    if match:
        return match.group(1)
    return None

def generate_markdown_entry(paper):
    """Generate markdown entry for a single paper"""
    # try to extract code link from summary or title
    code_link = extract_github_link(paper['summary'])
    if not code_link:
        code_link = extract_github_link(paper['title'])
    if not code_link:
        code_link = "N/A"
    else:
        code_link = f"[GitHub]({code_link})"

    # Clean abstract
    abstract = paper['summary'].replace('\n', ' ').strip()
    
    md = f"### [{paper['title']}]({paper['link']})\n"
    md += f"- **Date**: {paper['published']}\n"
    md += f"- **Code**: {code_link}\n"
    md += f"- **Abstract**:\n"
    md += f"  > {abstract}\n"
    
    return md

def update_readme(target_dir, new_content, date_str):
    """Update README.md with new content"""
    readme_path = os.path.join(target_dir, 'README.md')
    
    # If file doesn't exist, initialize it
    if not os.path.exists(readme_path):
        with open(readme_path, 'w', encoding='utf-8') as f:
            f.write(f"# Awesome Flow Matching & Diffusion Models (Daily)\n\n")
            f.write(f"Updated daily via automated scripts.\n\n")
            f.write(f"## 📅 Latest Updates ({date_str})\n\n")
            f.write("\n")
            f.write("\n\n")
            f.write(f"## 🗄️ Archives\n\n")
            f.write(f"- [2026 Archives](./archives/)\n")

    with open(readme_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Replace the content between markers
    # Here we keep the header, insert new content after START marker, push old content down,
    # but keep README short by only showing "today's updates", with history in archives.
    # Below logic replaces the "today's updates" section.
    
    start_marker = "<!-- START LATEST -->"
    end_marker = "<!-- END LATEST -->"
    
    if start_marker not in content or end_marker not in content:
        # If markers not found, append new content
        new_readme = content + f"\n\n## {date_str}\n{new_content}"
    else:
        # Replace middle part
        pattern = re.compile(f"{re.escape(start_marker)}.*?{re.escape(end_marker)}", re.DOTALL)
        replacement = f"{start_marker}\n{new_content}\n{end_marker}"
        new_readme = pattern.sub(replacement, content)
        
        # Update title with new date
        new_readme = re.sub(r"Latest Updates \(.*?\)", f"Latest Updates ({date_str})", new_readme)

    with open(readme_path, 'w', encoding='utf-8') as f:
        f.write(new_readme)
    print(f"✅ Updated README.md")

def update_archive(target_dir, papers, date_str):
    """Update archive file (archives/YYYY-MM.md)"""
    year_month = datetime.datetime.now().strftime("%Y-%m")
    archive_dir = os.path.join(target_dir, 'archives')
    os.makedirs(archive_dir, exist_ok=True)
    
    archive_file = os.path.join(archive_dir, f"{year_month}.md")
    
    # Generate markdown content for new papers
    append_content = f"\n## {date_str} (Total: {len(papers)})\n\n"
    for paper in papers:
        append_content += generate_markdown_entry(paper) + "\n---\n"

    # Append to file
    with open(archive_file, 'a', encoding='utf-8') as f:
        f.write(append_content)
    
    print(f"✅ Updated Archive: {archive_file}")

# --- 3. main ---

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output_dir", required=True, help="Path to the target repo")
    args = parser.parse_args()

    # 1. confirm time interval
    # To prevent timezone issues from missing papers, we fetch data from the past 2 days and filter in memory
    # or trust the arxiv_fetcher's date logic directly
    today = datetime.datetime.now()
    yesterday = today - datetime.timedelta(days=1)
    
    start_date_str = yesterday.strftime("%Y-%m-%d")
    end_date_str = today.strftime("%Y-%m-%d")
    
    keywords = ["Flow Matching", "Diffusion Model", "Score-based Generative Model"]
    
    print(f"🚀 Fetching papers for {start_date_str} to {end_date_str}...")
    
    # fetch papers
    # Note: your fetcher prints many logs, visible in CI
    papers = fetch_papers_by_keywords(
        keywords=keywords,
        start_date=start_date_str,
        end_date=end_date_str,
        max_results=50  # daily usually won't exceed 50 relevant papers
    )
    
    if not papers:
        print("⚠️ No papers found. Exiting.")
        # even without papers, don't exit with error to prevent CI failure
        return

    print(f"📦 Found {len(papers)} papers. Processing...")

    # Generate markdown content for new papers
    md_content = ""
    for paper in papers:
        md_content += generate_markdown_entry(paper) + "\n---\n"

    # Update Target Repo's files
    update_readme(args.output_dir, md_content, end_date_str)
    update_archive(args.output_dir, papers, end_date_str)

if __name__ == "__main__":
    main()