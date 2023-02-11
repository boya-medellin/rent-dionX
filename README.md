### What it does:
	This project is a web scraping script to scrape data from real estate ads
	in the city of Heraklion.

### How it does what it does:
	- scraper.py : The main python script for scraping and storing data.
		* It first iterates through the website and stores all working
		url links to ads in urls.txt
		* It then iterates through those links and scrapes all the corresponding data.
		* The data is then saved to data/data.csv, along with a safety copy
		* The next time the script runs, it only scrapes the new data that were uploaded 
		since the last run.
		* Logs all batch scraping actions in log.txt

	- postprocessing.py : Executes some prostprocessing actions for Dataframe optimization.

How to use:
	The recomended use is to schedule via cron in 1-2 days interval.
	i.e:
		* * */2 * * /usr/bin/python3 scraper.py
