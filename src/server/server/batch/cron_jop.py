import logging


def cron_job():
    with open("home/hayoung/ttest.txt", 'w') as f:
        for i in range(1, 11):
            data = "%d번째 줄입니다.\n" % i
            f.write(data)