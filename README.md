# WaterlooAppCrawler

Crawl graduate applications in the Odyssey system and save to a local CSV file. To customize the information to be crawled, change the `extract_details` function.

## Dependencies

* Firefox browser
* `pip install selenium`

## Usage

First, set your Waterloo email and Waterloo password in environment variables:

```
export WATERLOOEMAIL=your_username@uwaterloo.ca
export WATERLOOPASSWORD=your_password
```

Next, run

```
python main.py
```

Note that running this script will send a push request to Duo Mobile, and you will need to use Duo Mobile to **approve** the login request.

After running this script, the results will be saved in a CSV file named `applications_data.csv`.
