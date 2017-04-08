"""
The LogParser class stores message logs and cumulatively generates IBM Watson reports.
"""

import json
from os.path import join, dirname
from watson_developer_cloud import PersonalityInsightsV2
from datetime import datetime, timedelta
import configparser
from watson_developer_cloud import ToneAnalyzerV3

def main():
    cparser = configparser.ConfigParser()
    cparser.read('config.ini')

    lp = LogParser('config.ini')

    lp.add_log('Dude, what the hell?')
    lp.single_reaction()

    print(lp.reaction)
    # print(lp.personality_data)


# personality_insights = PersonalityInsightsV2(
#     username='4992907f-7c59-4405-953f-0fec302964f9',
#     password='1b6mpATU3AEh')
#
# with open(join(dirname(__file__), './MobyDick.txt')) as \
#         personality_text:
#     print(json.dumps(personality_insights.profile(
#         text=personality_text.read()), indent=2))


class LogParser:
    def __init__(self, path):
        """
        Instantiates an instance of the LogParser
        :param str username: Service Credential username
        :param str password: Service Credential password
        """
        initparser = configparser.ConfigParser()
        initparser.read(path)

        self.personality_client = PersonalityInsightsV2(
            username=initparser['personality']['username'],
            password=initparser['personality']['password'])
        self.tone_client = ToneAnalyzerV3(
            username=initparser['tone']['username'],
            password=initparser['tone']['password'],
            version="2016-02-11")

        self.logs = []
        self.personality_data = {}
        self.tone_data = {}
        self.lenlog = [0]
        self.reaction = []

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

    def watson_report_cumulative(self):
        """
        Runs a cumulative report on the logs gathered to-date
        :return: 
        """
        self.lenlog.append(len(self.logs))
        personality_reports = {self.lenlog[-1]: {}}
        for personality, percentage in self.personality_report('\n'.join(self.logs)):
            personality_reports[self.lenlog[-1]].update({personality: percentage})

        self.personality_data.update(personality_reports)

        tone_reports = {self.lenlog[-1]: {}}
        for tone_id, score in self.tone_report('\n'.join(self.logs)):
            tone_reports[self.lenlog[-1]].update({tone_id: score})

        self.tone_data.update(tone_reports)

    def personality_report(self, text, tree=None):
        """
        Recursive Generator that yields tuples of personality insights for the current self.logs
        personality scores
        :return: a list of tuples with each personality type in the zeroth index and each percentage in the first index
        :rtype: list of tuple
        """
        # Collect data on first iteration
        if not tree and tree != []:
            print('acquiring')
            resp = self.personality_client.profile(text=text)

            # Check for warnings and print them if they exist.
            if resp['warnings']:
                print(resp['warnings'])

            tree = resp['tree']

        if 'name' in tree and 'percentage' in tree:
            yield tree['name'], tree['percentage']
        for branch in tree:
            if isinstance(tree[branch], list):
                for twig in tree[branch]:
                    for name, percentage in self.personality_report(None, twig):
                        yield name, percentage

    def tone_report(self, text, tree=None):
        if not tree and tree != []:
            print("acquiring tone")
            resp = self.tone_client.tone(text=text)

            tree = resp['document_tone']
            print(tree)

            # Check for warnings and print them if they exist.
            if 'warnings' in resp and resp['warnings']:
                print(resp['warnings'])

        if 'tone_id' in tree and 'score' in tree:
            print("yielding")
            yield tree['tone_id'], tree['score']
        for branch in tree:
            if isinstance(tree[branch], list):
                for twig in tree[branch]:
                    for name, percentage in self.personality_report(None, twig):
                        print("recursive call")
                        yield name, percentage

    def single_reaction(self):
        """
        Returns a report relative to the log that just happened.
        :return: 
        """

        reaction = []

        for tone_id, score in self.tone_report(self.logs[-1]):
            reaction.append((tone_id, score))

        # Return highest magnitude of either tone or personality implied through the statement
        self.reaction = sorted(reaction, key=lambda t: t[1])


if __name__ == '__main__':
    main()