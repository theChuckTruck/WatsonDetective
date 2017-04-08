"""
The LogParser class stores message logs and cumulatively generates IBM Watson reports.
"""

import json
from os.path import join, dirname
from watson_developer_cloud import PersonalityInsightsV2
from datetime import datetime, timedelta
import configparser

def main():
    cparser = configparser.ConfigParser()
    cparser.read('config.ini')

    username = cparser['watson']['username']
    password = cparser['watson']['password']

    lp = LogParser(username, password)
    with open('MobyDick.txt', 'r') as infile:
        lp.add_log(infile.read())

    lp.watson_report()
    print(lp.personality_data)


# personality_insights = PersonalityInsightsV2(
#     username='4992907f-7c59-4405-953f-0fec302964f9',
#     password='1b6mpATU3AEh')
#
# with open(join(dirname(__file__), './MobyDick.txt')) as \
#         personality_text:
#     print(json.dumps(personality_insights.profile(
#         text=personality_text.read()), indent=2))


class LogParser:
    def __init__(self, username, password):
        """
        Instantiates an instance of the LogParser
        :param str username: Service Credential username
        :param str password: Service Credential password
        """

        self.personality_client = PersonalityInsightsV2(
            username=username,
            password=password)
        self.logs = []
        self.personality_data = {}
        self.tone_data = {}
        self.lenlog = [0]

    def add_log(self, log):
        """
        Adds a log or series of logs to self.logs
        :return: None
        """
        if isinstance(log, list):
            self.logs += log
        elif isinstance(log, str):
            self.logs.append(log)
        else:
            raise TypeError("add_log only accepts types (str, list str)")


    def watson_report(self):
        """
        Runs a cumulative report on the logs gathered to-date
        :return: 
        """
        self.lenlog.append(len(self.logs))
        personality_reports = {self.lenlog[-1]: {}}
        for personality, percentage in self.personality_report({}):
            print(personality)
            print(percentage)
            personality_reports[self.lenlog[-1]].update({personality: percentage})
        # print(list(self.personality_report()))
        # personality_reports[self.lenlog[-1]].update()

        self.personality_data.update(personality_reports)

        # tone_reports = {self.lenlog[-1]: {}}
        # for tone, percentage in

    def personality_report(self, tree=None):
        """
        Recursive Generator that yields tuples of personality insights for the current self.logs
        personality scores
        :return: a list of tuples with each personality type in the zeroth index and each percentage in the first index
        :rtype: list of tuple
        """
        # Collect data on first iteration
        if not tree and tree != []:
            print('acquiring')
            resp = self.personality_client.profile(text='\n'.join(self.logs))

            # Check for warnings and print them if they exist.
            if resp['warnings']:
                print(resp['warnings'])

            tree = resp['tree']

        if 'name' in tree and 'percentage' in tree:
            yield tree['name'], tree['percentage']
        for branch in tree:
            if isinstance(tree[branch], list):
                for twig in tree[branch]:
                    for name, percentage in self.personality_report(twig):
                        yield name, percentage

    def tone_report(self, tree=None):
        pass

if __name__ == '__main__':
    main()