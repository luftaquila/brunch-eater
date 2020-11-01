# brunch-eater
Crawler and keyword parser of Brunch, Kakao's writing platform.

### Installation
##### Clone repository
```
git clone https://github.com/luftaquila/brunch-eater.git
```

##### Install python dependencies
```
pip install -r requirements.txt
```


##### Install ChromeDriver
1. Visit [HERE](https://chromedriver.chromium.org/downloads) to download the corresponding version of ChromeDriver that matches your installed Chrome version.
1. Place chromedriver executable in the same directory as `main.py`
    * brunch-eater will assume `chromedriver` is located in the same directory as `main.py`
    * if not, give `-d` option to specify `chromedriver` path
    
### Options
##### Keyword
`-k` `--keyword`
