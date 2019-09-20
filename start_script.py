import os
import signal
import subprocess

# Making sure to use virtual environment libraries
# activate_this = "/home/ubuntu/tensorflow/bin/activate_this.py"
# exec(open(activate_this).read(), dict(__file__=activate_this))

from scrapelog import ScrapeLog


logger = ScrapeLog()

# Change directory to where your Flask's app.py is present
os.chdir("/home/ubuntu/scraper/project_scrape")
# os.chdir("/Users/sasu/Desktop/ASIN5/BoroMe/Image Quality Prediction/web-service/flask_server")
tf_ic_server = ""
flask_server = ""

try:
    scrape = subprocess.Popen(["DB_USERNAME=scraper DB_PASSWORD=Q1w2e3r4t5y6 TELEGRAM_TOKEN=951443203:AAEeoc0Q6-4Q6Dq7S40ACRr1ceXcIA_Twv0 AWS_ACCESS_KEY_ID=AKIAWFNWBEHETSGTGDGY AWS_SECRET_ACCESS_KEY=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 BUCKET_NAME=spearlytics-tweets nohup python3 scrapeusers.py > scrape_output.log"],
                                    stdout=subprocess.DEVNULL,
                                    shell=True,
                                    preexec_fn=os.setsid)
    logger.info("Started Handle Scraper!")

    update = subprocess.Popen([
                                  "DB_USERNAME=scraper DB_PASSWORD=Q1w2e3r4t5y6 TELEGRAM_TOKEN=951443203:AAEeoc0Q6-4Q6Dq7S40ACRr1ceXcIA_Twv0 AWS_ACCESS_KEY_ID=AKIAWFNWBEHETSGTGDGY AWS_SECRET_ACCESS_KEY=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 BUCKET_NAME=spearlytics-tweets nohup python3 scraper.py > update_output.log"],
                              stdout=subprocess.DEVNULL,
                              shell=True,
                              preexec_fn=os.setsid)
    logger.info("Started User Updater!")

    while True:
        logger.warn("Type 'exit' and press 'enter' to quit: ")
        in_str = input().strip().lower()
        if in_str == 'q' or in_str == 'exit':
            logger.warn('Shutting down all servers...')
            os.killpg(os.getpgid(scrape.pid), signal.SIGTERM)
            os.killpg(os.getpgid(update.pid), signal.SIGTERM)
            logger.warn('Servers successfully shutdown!')
            break
        else:
            continue
except KeyboardInterrupt:
    logger.warn('Shutting down all scrapers...')
    os.killpg(os.getpgid(scrape.pid), signal.SIGTERM)
    os.killpg(os.getpgid(update.pid), signal.SIGTERM)
    logger.warn('Scrapers successfully shutdown!')
