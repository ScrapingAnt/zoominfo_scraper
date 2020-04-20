# Zoominfo parser using scrapingant.com

## Usage
You need docker to run this example.

- fill you Rapidapi key in config.py
- Run:
```shell script
docker build -t zoominfo_parser . && docker run -it zoominfo_parser
```
Example output:
```shell script
getting page https://www.zoominfo.com/pic/mental-health-america-inc/76809493
getting page https://www.zoominfo.com/pic/mental-health-america-inc/76809493?pageNum=2
getting page https://www.zoominfo.com/pic/mental-health-america-inc/76809493?pageNum=3
getting page https://www.zoominfo.com/pic/mental-health-america-inc/76809493?pageNum=4
getting page https://www.zoominfo.com/pic/mental-health-america-inc/76809493?pageNum=5
getting page https://www.zoominfo.com/pic/mental-health-america-inc/76809493?pageNum=5
Contact Name            Job Title                                                                     Location
----------------------  ----------------------------------------------------------------------------  -----------------------------------
Jewell Gooding          Executive Director                                                            United States, Virginia, Alexandria
Victoria Renard         Vice President, Development                                                   United States, Virginia, Alexandria
...
```
