#!/usr/bin/env python3
"""
Concise ArXiv paper fetching script
Search papers by keywords in titles and abstracts within a specified time range and save in Markdown format
Search scope is limited to Mathematics, Computer Science and Statistics fields

Usage example:
python arxiv_fetcher.py --keywords "machine learning,deep learning" --start-date "2024-01-01" --end-date "2024-12-31" --output "ml_papers_2024.md"
"""

import urllib.request
import urllib.parse
import feedparser
import argparse
import re
from datetime import datetime
import time

def parse_arxiv_url(url):
    """Extract paper ID from ArXiv URL"""
    ix = url.rfind('/')
    return url[ix+1:]

def format_authors(authors):
    """Format author list"""
    if isinstance(authors, list):
        return ", ".join([author.get('name', '') for author in authors])
    return authors

def clean_text(text):
    """Clean text, remove extra whitespace"""
    return re.sub(r'\s+', ' ', text.strip())

def date_in_range(paper_date, start_date, end_date):
    """Check if paper date is within specified range"""
    try:
        paper_dt = datetime.strptime(paper_date[:10], '%Y-%m-%d')
        start_dt = datetime.strptime(start_date, '%Y-%m-%d')
        end_dt = datetime.strptime(end_date, '%Y-%m-%d')
        return start_dt <= paper_dt <= end_dt
    except:
        return False

def contains_keywords(text, keywords):
    """Check if text contains keywords"""
    text_lower = text.lower()
    return any(keyword.lower() in text_lower for keyword in keywords)

def extract_categories(entry):
    """Extract paper categories"""
    categories = []
    
    # Extract category information from tags
    if 'tags' in entry:
        for tag in entry['tags']:
            if 'term' in tag:
                categories.append(tag['term'])
    
    # If no tags, try to extract from other fields
    if not categories and 'arxiv_primary_category' in entry:
        categories.append(entry['arxiv_primary_category']['term'])
    
    return categories

def format_categories(categories):
    """Format category information"""
    if not categories:
        return "Unknown"
    
    # Group categories by field
    math_cats = [cat for cat in categories if cat.startswith('math.')]
    cs_cats = [cat for cat in categories if cat.startswith('cs.')]
    stat_cats = [cat for cat in categories if cat.startswith('stat.')]
    
    formatted = []
    if math_cats:
        formatted.append(f"Mathematics: {', '.join(math_cats)}")
    if cs_cats:
        formatted.append(f"Computer Science: {', '.join(cs_cats)}")
    if stat_cats:
        formatted.append(f"Statistics: {', '.join(stat_cats)}")
    
    return "; ".join(formatted) if formatted else ", ".join(categories)

def fetch_papers_by_keywords(keywords, start_date, end_date, max_results=1000):
    """
    Fetch papers based on keywords and date range
    
    Args:
        keywords: List of keywords
        start_date: Start date (YYYY-MM-DD)
        end_date: End date (YYYY-MM-DD)
        max_results: Maximum number of results
    """
    base_url = 'http://export.arxiv.org/api/query?'
    papers = []
    
    # Define target fields - Mathematics, Computer Science, Statistics
    target_categories = [
        # Mathematics categories
        'math.AG', 'math.AT', 'math.AP', 'math.CT', 'math.CA', 'math.CO', 'math.AC', 'math.CV',
        'math.DG', 'math.DS', 'math.FA', 'math.GM', 'math.GN', 'math.GT', 'math.GR', 'math.HO',
        'math.IT', 'math.KT', 'math.LO', 'math.MP', 'math.MG', 'math.NT', 'math.NA', 'math.OA',
        'math.OC', 'math.PR', 'math.QA', 'math.RT', 'math.RA', 'math.SP', 'math.ST', 'math.SG',
        
        # Computer Science categories  
        'cs.AI', 'cs.AR', 'cs.CC', 'cs.CE', 'cs.CG', 'cs.CL', 'cs.CR', 'cs.CV', 'cs.DB', 'cs.DC',
        'cs.DL', 'cs.DM', 'cs.DS', 'cs.DC', 'cs.ET', 'cs.FL', 'cs.GL', 'cs.GR', 'cs.GT', 'cs.HC',
        'cs.IR', 'cs.IT', 'cs.LG', 'cs.LO', 'cs.MS', 'cs.MA', 'cs.MM', 'cs.NI', 'cs.NE', 'cs.NA',
        'cs.OS', 'cs.OH', 'cs.PF', 'cs.PL', 'cs.RO', 'cs.SI', 'cs.SE', 'cs.SD', 'cs.SC', 'cs.SY',
        
        # Statistics categories
        'stat.AP', 'stat.CO', 'stat.ML', 'stat.ME', 'stat.OT', 'stat.TH'
    ]

    # Build category query
    category_query = '+OR+'.join([f'cat:{cat}' for cat in target_categories])

    # Build keyword query - search in title and abstract
    keyword_query = '+OR+'.join([f'ti:{urllib.parse.quote(kw)}+OR+abs:{urllib.parse.quote(kw)}' for kw in keywords])
    
    # Build date range query for ArXiv API
    start_dt = start_date.replace('-', '')
    end_dt = end_date.replace('-', '')
    date_query = f'submittedDate:[{start_dt}0000+TO+{end_dt}2359]'

    # Build combined query: (keyword query) AND (category query) AND (date query)
    combined_query = f'({keyword_query})+AND+({category_query})+AND+{date_query}'
    
    print(f"Searching keywords: {', '.join(keywords)}")
    print(f"Search fields: Mathematics, Computer Science, Statistics")
    print(f"Date range: {start_date} to {end_date}")
    
    start_index = 0
    results_per_batch = 100
    
    while start_index < max_results:
        query = f'search_query={combined_query}&sortBy=submittedDate&sortOrder=descending&start={start_index}&max_results={results_per_batch}'
        
        try:
            print(f"Fetching batch {start_index//results_per_batch + 1}...")
            
            with urllib.request.urlopen(base_url + query) as response:
                data = response.read()
            
            parsed = feedparser.parse(data)
            
            if not parsed.entries:
                print("No more results found")
                break
            
            batch_count = 0
            for entry in parsed.entries:
                # Check if publication date is within range
                published_date = entry.get('published', '')
                if not date_in_range(published_date, start_date, end_date):
                    continue
                
                # Check if title and abstract contain keywords
                title = entry.get('title', '')
                summary = entry.get('summary', '')
                
                if contains_keywords(title, keywords) or contains_keywords(summary, keywords):
                    paper_id = parse_arxiv_url(entry.get('id', ''))
                    categories = extract_categories(entry)
                    
                    paper = {
                        'id': paper_id,
                        'title': clean_text(title),
                        'authors': format_authors(entry.get('authors', [])),
                        'published': published_date[:10],  # Keep only date part
                        'summary': clean_text(summary),
                        'categories': categories,
                        'formatted_categories': format_categories(categories),
                        'link': entry.get('link', ''),
                        'pdf_link': entry.get('link', '').replace('/abs/', '/pdf/') + '.pdf'
                    }
                    papers.append(paper)
                    batch_count += 1
            
            print(f"Found {batch_count} relevant papers in this batch")
            
            start_index += results_per_batch
            
            # Avoid too frequent requests
            time.sleep(1)
            
        except Exception as e:
            print(f"Request error: {e}")
            break
    
    return papers

def save_to_markdown(papers, output_file, keywords, start_date, end_date):
    """Save papers to Markdown format"""
    
    with open(output_file, 'w', encoding='utf-8') as f:
        # Write title and statistics
        f.write(f"# ArXiv Paper Search Results\n\n")
        f.write(f"**Search Keywords**: {', '.join(keywords)}\n\n")
        f.write(f"**Search Fields**: Mathematics, Computer Science, Statistics\n\n")
        f.write(f"**Date Range**: {start_date} to {end_date}\n\n")
        f.write(f"**Papers Found**: {len(papers)}\n\n")
        f.write(f"**Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        f.write("---\n\n")
        
        # Sort by publication date
        papers.sort(key=lambda x: x['published'], reverse=True)
        
        # Write paper list
        for i, paper in enumerate(papers, 1):
            f.write(f"## {i}. {paper['title']}\n\n")
            f.write(f"**Authors**: {paper['authors']}\n\n")
            f.write(f"**Published**: {paper['published']}\n\n")
            f.write(f"**Categories**: {paper['formatted_categories']}\n\n")
            f.write(f"**ArXiv ID**: {paper['id']}\n\n")
            f.write(f"**Links**: [View Paper]({paper['link']}) | [Download PDF]({paper['pdf_link']})\n\n")
            f.write(f"**Abstract**:\n{paper['summary']}\n\n")
            f.write("---\n\n")
    
    print(f"Results saved to: {output_file}")

def main():
    parser = argparse.ArgumentParser(description='Fetch ArXiv papers by keywords (limited to Mathematics, Computer Science, Statistics fields)')
    parser.add_argument('--keywords', type=str, required=True,
                       help='Search keywords, separated by commas, e.g., "machine learning,deep learning"')
    parser.add_argument('--start-date', type=str, required=True,
                       help='Start date (YYYY-MM-DD)')
    parser.add_argument('--end-date', type=str, required=True,
                       help='End date (YYYY-MM-DD)')
    parser.add_argument('--output', type=str, default='arxiv_papers.md',
                       help='Output filename (default: arxiv_papers.md)')
    parser.add_argument('--max-results', type=int, default=1000,
                       help='Maximum number of search results (default: 1000)')
    
    args = parser.parse_args()
    
    # Parse keywords
    keywords = [kw.strip() for kw in args.keywords.split(',')]
    
    # Validate date format
    try:
        datetime.strptime(args.start_date, '%Y-%m-%d')
        datetime.strptime(args.end_date, '%Y-%m-%d')
    except ValueError:
        print("Error: Date format should be YYYY-MM-DD")
        return
    
    # Fetch papers
    papers = fetch_papers_by_keywords(keywords, args.start_date, args.end_date, args.max_results)
    
    if papers:
        # Save to Markdown
        save_to_markdown(papers, args.output, keywords, args.start_date, args.end_date)
        print(f"Found {len(papers)} relevant papers in total")
    else:
        print("No papers found matching the criteria")

if __name__ == "__main__":
    main()
