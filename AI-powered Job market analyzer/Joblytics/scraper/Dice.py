import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
import random
import time
from datetime import datetime, timedelta
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options


def extract_posted_date(full_date_string):
    """Extract the posted date part from the full date string."""
    posted_part = full_date_string.split("|")[0]  # Takes "Posted 15 days agoda"
    return posted_part.strip()


def parse_relative_date(relative_date):
    """Convert relative date strings to actual dates."""
    # Clean the input string
    relative_date = relative_date.lower().strip()

    # Handle special cases first
    if any(x in relative_date for x in ["moments", "just now", "today", "now"]):
        return datetime.now().date()

    # Extract numeric value (handle "60+" case)
    parts = relative_date.split()
    try:
        num_part = parts[1].replace("+", "")  # Remove '+' if present
        num = int(num_part)
    except (IndexError, ValueError):
        return datetime.now().date()  # Fallback for unexpected formats

    # Get time unit (day/week/hour/etc)
    unit = parts[2] if len(parts) > 2 else ""

    today = datetime.now().date()

    # Calculate date based on unit
    if any(x in unit for x in ["day", "d"]):
        return today - timedelta(days=num)
    elif any(x in unit for x in ["week", "w"]):
        return today - timedelta(weeks=num)
    elif any(x in unit for x in ["month", "m"]):
        return today - timedelta(days=num * 30)  # Approximation
    elif any(x in unit for x in ["year", "y"]):
        return today - timedelta(days=num * 365)  # Approximation
    elif any(x in unit for x in ["hour", "h"]):
        return today
    else:
        return today  # Fallback for unknown units


def format_search_parameter(param):
    """Format search parameters to replace spaces with + for URL."""
    return param.replace(" ", "+")


def scrape_dice_jobs(job_keyword, location_city, skills_tab_dict,headless=True):
    """
    Scrape job listings from Dice.com based on keyword and location.

    Args:
        job_keyword (str): Job keyword to search for
        location_city (str): City to search jobs in
        headless (bool): Whether to run browser in headless mode

    Returns:
        pandas.DataFrame: DataFrame containing job information matching the schema
    """
    # Format search parameters for URL
    formatted_keyword = format_search_parameter(job_keyword)
    formatted_location = format_search_parameter(location_city)

    # Set up webdriver options
    options = Options()
    if headless:
        options.add_argument("--headless")
        options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1920,1080")
    options.add_argument("--no-sandbox")
    options.add_argument(
        "--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.212 Safari/537.36")

    # Initialize data lists with all required columns from schema
    job_data = {
        "job_id": [],
        "title": [],
        "company": [],
        "location": [],
        "employment_type": [],
        "salary_range": [],
        "description": [],
        "requirements": [],
        "posted_date": [],
        "job_link": [],
        "source": [],
        "work_setting": []
    }
    try:
        driver = webdriver.Chrome(options=options)

        # Construct base URL with formatted parameters
        base_url = f"https://www.dice.com/platform/jobs?location={formatted_location}&q={formatted_keyword}"
        print(f"Searching for {job_keyword} jobs in {location_city}")
        print(f"URL: {base_url}")

        # Load the initial page
        driver.get(base_url)
        time.sleep(3)  # Wait for page to load

        try:
            # Get total number of pages
            pages_element = driver.find_element(By.CSS_SELECTOR, 'span[class="text-base font-bold leading-normal"]')
            pages = int(pages_element.text)
            print(f"Found {pages} pages of results")
        except Exception as e:
            print(f"Could not determine number of pages: {e}")
            pages = 1

        for page in range(1, min(pages, 2)):  # Limit to 2 pages for testing
            print(f"Scraping page {page} of {pages}...")

            # Construct URL for current page
            if page == 1:
                url = base_url
            else:
                url = f"{base_url}&page={page}"

            driver.get(url)
            time.sleep(random.uniform(2, 4))  # Random delay between page loads

            # Find all job cards on the page
            try:
                element = driver.find_element(By.CLASS_NAME, 'w-full')
                job_page = element.find_element(By.CSS_SELECTOR, '[class="m-px mx-auto max-w-[1400px] sm:px-6"]')
                jobs = job_page.find_elements(By.CSS_SELECTOR,
                                              '[class= "my-4 mx-auto flex h-full w-full items-center"]')

                # Extract job titles and links from the page
                job_links = []
                for job in jobs:
                    try:
                        job_title = job.find_element(By.CLASS_NAME, "self-stretch")
                        job_link = job_title.find_element(By.CSS_SELECTOR, "a").get_attribute("href")
                        job_links.append(job_link)
                    except Exception as e:
                        print(f"Error extracting job card: {e}")
                        continue

                # Visit each job page to extract detailed information
                for i, link in enumerate(job_links):
                    if(i==1):
                        break
                    try:
                        print(f"Scraping job {i + 1} of {len(job_links)} on page {page}...")
                        driver.get(link)
                        time.sleep(random.uniform(2, 4))  # Random delay between job page loads

                        # Initialize a temporary dictionary to store this job's data
                        current_job = {
                            "job_id": None,
                            "title": None,
                            "company": None,
                            "location": None,
                            "employment_type": None,
                            "salary_range": None,
                            "description": None,
                            "requirements": None,
                            "posted_date": None,
                            "job_link": link,
                            "source": "Dice",
                            "work_setting": None
                        }

                        # Extract job ID from URL
                        current_job["job_id"] = link.split('/')[-1]

                        # Get job details container
                        try:
                            job_details = driver.find_element(By.ID, "jobdetails")

                            # Company name
                            try:
                                current_job["company"] = job_details.find_element(
                                    By.CSS_SELECTOR,
                                    'li[class="job-header_jobDetailFirst__xI_5S job-header_companyName__Mx3ZU text-center font-sans text-base non-italic font-normal md:mr-4 md:text-left md:flex-nowrap"]'
                                ).text
                            except:
                                pass

                            # Location
                            try:
                                current_job["location"] = job_details.find_element(
                                    By.CSS_SELECTOR, 'li[data-cy="location"]'
                                ).text
                            except:
                                pass

                            # Posted date
                            try:
                                date_text = job_details.find_element(
                                    By.CSS_SELECTOR, 'li[data-cy="postedDate"]'
                                ).text
                                date_part = extract_posted_date(date_text)
                                parsed_date = parse_relative_date(date_part)
                                current_job["posted_date"] = datetime.combine(parsed_date, datetime.min.time())
                            except:
                                pass

                            # Job overview section
                            overview = driver.find_element(By.CSS_SELECTOR, 'div[class="lg:col-span-8"]')

                            # Work setting (Remote, Hybrid, etc.)
                            try:
                                loc_scrap = overview.find_element(By.CSS_SELECTOR, 'div[data-cy="locationDetails"]')
                                location_modes = loc_scrap.find_elements(By.CSS_SELECTOR,
                                                                         'div[class="chip_chip__cYJs6"]')
                                current_job["work_setting"] = ', '.join([mode.text for mode in location_modes])
                            except:
                                pass

                            # Salary range
                            try:
                                pay_scrap = overview.find_element(By.CSS_SELECTOR, 'div[data-cy="payDetails"]')
                                pay_modes = pay_scrap.find_elements(By.CSS_SELECTOR, 'div[class="chip_chip__cYJs6"]')
                                salary = ', '.join([mode.text for mode in pay_modes])
                                if ("Depends" not in salary)|("on" not in salary)|("experience" not in salary):
                                    current_job["salary_range"] = salary
                            except:
                                pass

                            # Employment type
                            try:
                                emp_scrap = overview.find_element(By.CSS_SELECTOR, 'div[data-cy="employmentDetails"]')
                                emp_type_modes = emp_scrap.find_elements(By.CSS_SELECTOR,
                                                                         'div[class="chip_chip__cYJs6"]')
                                current_job["employment_type"] = ', '.join([mode.text for mode in emp_type_modes])
                            except:
                                pass

                            # Try to expand skills section
                            try:
                                show_more = WebDriverWait(driver, 5).until(
                                    EC.element_to_be_clickable((By.ID, "skillsToggle"))
                                )
                                driver.execute_script("arguments[0].scrollIntoView();", show_more)
                                show_more.click()
                                time.sleep(1)
                            except:
                                pass

                            # Scrape skills (goes into requirements)
                            try:
                                skill_elements = driver.find_elements(By.CSS_SELECTOR, 'div[data-cy="skillsList"]')
                                skills_for_skill_table = [skill_elem.text.strip() for skill_elem in skill_elements]
                                current_job["requirements"] = ', '.join(skills_for_skill_table)
                            except:
                                current_job["requirements"] = ''

                            # Try to expand description
                            try:
                                show_more = WebDriverWait(driver, 5).until(
                                    EC.element_to_be_clickable((By.ID, "descriptionToggle"))
                                )
                                driver.execute_script("arguments[0].scrollIntoView();", show_more)
                                show_more.click()
                                time.sleep(1)
                            except:
                                pass

                            # Get job description
                            try:
                                desc_html = driver.find_element(By.ID, "jobDescription")
                                current_job["description"] = desc_html.find_element(
                                    By.CSS_SELECTOR, 'div[data-testid="jobDescriptionHtml"]'
                                ).text
                            except:
                                pass

                            # Get job title from details page if not already set
                            if current_job["title"] is None:
                                try:
                                    current_job["title"] = driver.find_element(
                                        By.CSS_SELECTOR, 'h1[data-cy="jobTitle"]'
                                    ).text
                                except:
                                    pass

                        except Exception as e:
                            print(f"Error processing job details container: {e}")

                        # Append all data for this job to our lists
                        for key in job_data.keys():
                            job_data[key].append(current_job.get(key, None))

                    except Exception as e:
                        print(f"Error processing job page: {e}")
                        continue

            except Exception as e:
                print(f"Error processing page {page}: {e}")
                continue

    except Exception as e:
        print(f"Error initializing scraper: {e}")
        return pd.DataFrame()  # Return empty DataFrame on critical error

    finally:
        # Close the driver
        if 'driver' in locals():
            driver.quit()

    # Create DataFrame from collected data
    df = pd.DataFrame(job_data)

    # Ensure all columns are present (even if empty)
    required_columns = [
        "job_id", "title", "company", "location", "employment_type",
        "salary_range", "description", "requirements", "posted_date",
        "job_link", "source", "work_setting"
    ]

    for col in required_columns:
        if col not in df.columns:
            df[col] = None

    # Add created_at timestamp column
    df['created_at'] = datetime.now()

    return df


def save_to_csv(df, filename="dice_jobs.csv"):
    """Save DataFrame to CSV file."""
    if not df.empty:
        df.to_csv(filename, index=False)
        print(f"Data saved to {filename}")
    else:
        print("No data to save - DataFrame is empty")


def main():
    """Main function to run the scraper."""
    # Example usage
    job_keyword = "data engineer"
    location_city = "New York, NY"

    # Scrape jobs and get DataFrame
    jobs_df = scrape_dice_jobs(job_keyword, location_city)

    # Create filename based on search parameters
    filename = f"dice_{job_keyword.replace(' ', '_')}_{location_city.replace(' ', '_').replace(',', '')}.csv"

    # Save data to CSV
    save_to_csv(jobs_df, filename)

    # Print summary
    print(f"\nScraping complete!")
    print(f"Total jobs found: {len(jobs_df)}")
    print(f"Data saved to {filename}")


if __name__ == "__main__":
    main()
