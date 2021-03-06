# brunch-eater
Crawler and keyword parser of Brunch, Kakao's writing platform.

### Installation
##### Clone repository
```
git clone https://github.com/luftaquila/brunch-eater.git
cd brunch-eater/server/
```

##### Install python dependencies
```
pip install requests selenium colorama
```

##### Install ChromeDriver
1. Visit [HERE](https://chromedriver.chromium.org/downloads) to download the corresponding version of ChromeDriver that matches your installed Chrome version.
1. Place chromedriver executable in the same directory as `main.py`
    * brunch-eater will assume `chromedriver` is located in the same directory as `main.py`
    * If not, give `-d` option to specify `chromedriver` path
    
### Options
##### Keyword
`-k` or `--keyword` [keyword] to pass keywords to brunch-eater.  

* Single keyword can be passed like `python3 main.py -k IT`  
* Multiple keywords should be passed with `-m` or `--multiple` option.  
Keywords are seperated by comma(,) and wrapped by double-quote("), like `python3 main.py -m -k "IT,AI"`

##### Scan Counts
`-n` or `--number` [number] to set count limit of scanning.  

* If not specified, brunch-eater will scan whole articles of passed keyword.
* ex) `python3 main.py -k IT -n 100` to scan most recent 100 articles of 'IT' keyword.  
`python3 main.py -m -k "IT,AI" -n 100` will scan 100 most recent articles about each keywords.

##### Output file
`-o` or `--output` [output file] to specify output json file directory and name.

* If not specified, brunch-eater will make output file in the `outputs/` folder of `main.py`'s parent directory.  
* ex) `python3 main.py -k IT -o /home/user/result.json` will create `result.json` in `/home/user/` as output.

##### ChromeDriver
`-d` or `--driver` [chromedriver location] to specify ChromeDriver executable location.
* If not specified, brunch-eater will assume it is located in the same directory as `main.py`.  
See [Install ChromeDriver](https://github.com/luftaquila/brunch-eater#install-chromedriver) for details.

### Usage Examples
* `python3 main.py -k IT`  
Scan all articles about IT, until no articles remaining.
* `python3 main.py -k IT -n 100`  
Only scan most recent 100 articles about IT.
* `python3 main.py -m -k "IT, AI"`  
Scan all articles about IT and AI, until no articles remaining for both keywords.
* `python3 main.py -m -k "IT, AI" -n 100`  
Only scan most recent 100 articles each about IT and AI.
