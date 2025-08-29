# Pagination URL Construction Examples

This document provides concrete examples of how pagination URLs are constructed in the Dice.py scraper.

## Base URL Construction

### Input Parameters
```python
job_keyword = "data engineer"
location_city = "New York, NY"
```

### Formatting Process
```python
# Step 1: Format parameters (replace spaces with +)
formatted_keyword = format_search_parameter(job_keyword)    # "data+engineer"
formatted_location = format_search_parameter(location_city) # "New+York,+NY"

# Step 2: Construct base URL
base_url = f"https://www.dice.com/platform/jobs?location={formatted_location}&q={formatted_keyword}"
```

### Result
```
Base URL: https://www.dice.com/platform/jobs?location=New+York,+NY&q=data+engineer
```

## Page URL Generation

The scraper uses different logic for page 1 versus subsequent pages:

```python
# From lines 126-129 in Dice.py
if page == 1:
    url = base_url
else:
    url = f"{base_url}&page={page}"
```

## Complete URL Examples

### Example 1: "Data Engineer" in "New York, NY"

| Page | URL |
|------|-----|
| 1 | `https://www.dice.com/platform/jobs?location=New+York,+NY&q=data+engineer` |
| 2 | `https://www.dice.com/platform/jobs?location=New+York,+NY&q=data+engineer&page=2` |
| 3 | `https://www.dice.com/platform/jobs?location=New+York,+NY&q=data+engineer&page=3` |

### Example 2: "Software Developer" in "San Francisco"

| Page | URL |
|------|-----|
| 1 | `https://www.dice.com/platform/jobs?location=San+Francisco&q=software+developer` |
| 2 | `https://www.dice.com/platform/jobs?location=San+Francisco&q=software+developer&page=2` |
| 3 | `https://www.dice.com/platform/jobs?location=San+Francisco&q=software+developer&page=3` |

### Example 3: "Machine Learning Engineer" in "Austin, TX"

| Page | URL |
|------|-----|
| 1 | `https://www.dice.com/platform/jobs?location=Austin,+TX&q=machine+learning+engineer` |
| 2 | `https://www.dice.com/platform/jobs?location=Austin,+TX&q=machine+learning+engineer&page=2` |
| 3 | `https://www.dice.com/platform/jobs?location=Austin,+TX&q=machine+learning+engineer&page=3` |

## URL Parameter Analysis

### Query Parameters Used
1. **location**: The formatted job location
2. **q**: The formatted job keyword/query
3. **page**: The page number (only for pages 2+)

### Parameter Formatting Rules
- Spaces are replaced with `+` signs
- Commas and other special characters are preserved
- No URL encoding is applied beyond space replacement

## Current Implementation Flow

```python
def pagination_flow_example():
    # Detected pages from website
    pages = 5  # Example: website shows 5 pages available
    
    # Current limitation: only process 2 pages maximum
    for page in range(1, min(pages, 2)):  # Results in range(1, 2) = [1]
        print(f"Processing page {page}")
        
        if page == 1:
            url = "https://www.dice.com/platform/jobs?location=New+York&q=data+engineer"
        else:
            url = f"https://www.dice.com/platform/jobs?location=New+York&q=data+engineer&page={page}"
        
        print(f"URL: {url}")
        # Load page and process jobs...

# Output:
# Processing page 1
# URL: https://www.dice.com/platform/jobs?location=New+York&q=data+engineer
```

## Improved Implementation Example

```python
def improved_pagination_flow():
    # Remove artificial page limit
    for page in range(1, pages + 1):  # Process all available pages
        print(f"Processing page {page} of {pages}")
        
        if page == 1:
            url = base_url
        else:
            url = f"{base_url}&page={page}"
        
        print(f"URL: {url}")
        # Process all jobs on page (remove job limit)

# Example output for 5 pages:
# Processing page 1 of 5
# URL: https://www.dice.com/platform/jobs?location=New+York&q=data+engineer
# Processing page 2 of 5  
# URL: https://www.dice.com/platform/jobs?location=New+York&q=data+engineer&page=2
# ... continues for all 5 pages
```

## Error Scenarios

### Page Detection Failure
```python
# If page detection fails
pages = 1  # Fallback value

# Results in only processing page 1
for page in range(1, min(1, 2)):  # range(1, 1) = []
    # No pages processed!
```

### Invalid Page Access
```python
# If scraper tries to access non-existent page
url = "https://www.dice.com/platform/jobs?location=New+York&q=data+engineer&page=999"
# Would likely return empty results or error page
```

## Summary

The pagination system constructs URLs by:
1. Building a base URL with search parameters
2. Using the base URL directly for page 1
3. Appending `&page={number}` for subsequent pages
4. Currently limiting to maximum 2 pages for testing

The URL pattern is consistent and follows standard web pagination conventions, making it relatively reliable for accessing different pages of search results.