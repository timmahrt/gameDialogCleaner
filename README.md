
# Game script web scrapper

-----

This is a set of scripts that I have used to scrape websites for game scripts. The end result is currently available [https://www.timmahrt.com/game_scripts/](https://www.timmahrt.com/game_scripts/)

## Usage

1. Run `web_crawler.py` over a url containing many links to scripts (I crawl only 1 level deep)

2. Clean up the script with `cleanup.py`. The cleanup code is specific to each game script. Generally the end result should be a file where each line is either blank or looks like `speaker:speech event`

3. Generate the html for the script using `extract_dialogs.py`. Most output generated in step 2 should be processable here with perhaps some slight customization. (To get styling correct, don't forget to include `resources/game_scripts.css` with your html).

4. There is also `text_analyzer.py` which is a work-in-progress.

