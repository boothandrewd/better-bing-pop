""" app/parser.py
"""
from urllib import request
from time import sleep
from datetime import datetime, timedelta
from pytz import timezone
from re import compile as re

from bs4 import BeautifulSoup

def get_bp_html_events_lists():
    # Constants
    BP_URL_TEMPLATE = 'https://www.bingpop.com/basic-page/bingpop?page={}'
    MAX_REQUEST_ATTEMPTS = 3

    # Need page counter for url query `page=<counter>`
    page_counter = 0
    while True:
        # Attempt page request 3 times until code 200
        for attempt in range(MAX_REQUEST_ATTEMPTS):
            # Give the servers some breathing time on the last attempt
            if attempt == MAX_REQUEST_ATTEMPTS - 1:
                sleep(1)
            response = request.urlopen(BP_URL_TEMPLATE.format(page_counter))
            if response.getcode() == 200:
                break

        # Parse and detect content
        bp_html_page = response.read()
        soup = BeautifulSoup(bp_html_page, 'html.parser')
        if soup.find('div', {'class': 'views-row'}) == None:
            break

        # Yield list of entries
        yield soup.find_all('div', {'class': 'views-row'})
        page_counter += 1

def build_events_list():
    bp_events_list = []
    # Each page has a list of events. Loop over those pages
    for bp_html_events_list in get_bp_html_events_lists():
        # Loop over events in lists. Each element is html markup
        for bp_html_event in bp_html_events_list:
            # Get link info
            links = bp_html_event.find_all('a')
            link = links[0 if len(links) < 2 else 1]
            link_href = 'https://bingpop.com' + link.get('href')
            link_text = link.get_text()

            # Get time info and parse it into something relevant
            time_tag = bp_html_event.find('span', {'class': 'date-display-interval'})
            time_until = time_tag.get_text()

            # Capture some time data fields and enter into dict
            time_re = re(r'(?i)(?:in )?(?P<v1>\d{1,2}) (?P<u1>[^\Ws]*)s? (?P<v2>\d{1,2}) (?P<u2>[^\Ws]*)')
            match = time_re.match(time_until)
            if match == None:
                continue

            # Merge the time units by using `dict.update()`
            match_dict = match.groupdict()
            time_direction = 1 if 'In' in time_until else -1
            event_time_dict = {
                match_dict['u1'] + 's': int(match_dict['v1']) * time_direction,
                match_dict['u2'] + 's': int(match_dict['v2']) * time_direction
            }
            times_dict = {'years': 0, 'months': 0, 'weeks': 0, 'days': 0,
                          'hours': 0, 'mins': 0, 'seconds': 0}
            times_dict.update(event_time_dict)
            times_dict['minutes'] = times_dict['mins']
            del times_dict['mins']

            # `timedelta` doesn't take month or year values so do this by hand
            # First, remove from the dict but save the values
            years = times_dict['years']
            del times_dict['years']
            months = times_dict['months']
            del times_dict['months']
            # Next generate a timedelta without month or year changes, and add
            #   it to the current time
            time_elapsed_wo_my = timedelta(**times_dict)
            target_time_wo_my = datetime.now(timezone(US/Eastern)) + time_elapsed_wo_my
            # Find the value of the month and year changes and adjust based on
            #   the limited range (1..12) of months
            target_year = target_time_wo_my.year + years
            target_month = target_time_wo_my.month + months
            if target_month > 12:
                target_year += 1
                target_month -= 12
            if target_month < 1:
                target_year -= 1
                target_month += 12
            # Update the time
            target_time = target_time_wo_my.replace(year=target_year,
                                                    month=target_month)

            # Get event location
            place_tag = bp_html_event.find('span', {'itemprop': 'name address'})
            place = place_tag.get_text()

            # Add data to list
            bp_events_list.append({
                'url': link_href,
                'what': link_text,
                'where': place,
                'when': target_time,
                'when_string': target_time,
                'until': time_until,
                'past': time_direction < 0,
            })
    # Sort list and return
    return sorted(bp_events_list, key=lambda item:item['when'])


# events_list = build_events_list()
# for event in events_list:
#     print(event['when'], event['title'])
