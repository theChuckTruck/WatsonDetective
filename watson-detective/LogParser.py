"""
The LogParser class stores message logs and cumulatively generates IBM Watson reports.
"""

import json
from os.path import join, dirname
import os
from collections import defaultdict
from watson_developer_cloud import TradeoffAnalyticsV1
from watson_developer_cloud import PersonalityInsightsV2
from datetime import datetime, timedelta
import configparser
from watson_developer_cloud import ToneAnalyzerV3


def main():
    # print(os.listdir('.'))
    lp = LogParser('config.ini')

    lp.add_log('Dude, what the hell?'*100)
    lp.watson_report_cumulative()
    print(lp.axes)

    # lp.single_reaction()
    #
    # print(lp.reaction)

    # lp.decision(resource="foo")

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
        with open('./' + path, 'r') as f:
            initparser = configparser.ConfigParser()
            initparser.read_file(f)
            initparser.keys()

        self.personality_client = PersonalityInsightsV2(
            username=initparser['p']['username'],
            password=initparser['p']['password'])
        self.tone_client = ToneAnalyzerV3(
            username=initparser['tone']['username'],
            password=initparser['tone']['password'],
            version="2016-02-11")
        self.decision_client = TradeoffAnalyticsV1(
            username=initparser['decision']['username'],
            password=initparser['decision']['password'])

        self.logs = []
        self.lenlog = [len(self.logs)]
        self.axes = defaultdict(lambda: [0])
        self.axes['x'] = self.lenlog

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
        for personality, percentage in self.personality_report('\n'.join(self.logs)):
            self.axes[personality].append(percentage)

        for tone_id, score in self.tone_report('\n'.join(self.logs)):
            self.axes[tone_id].append(score)

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
                    for name, percentage in self.tone_report(None, twig):
                        print("recursive call")
                        yield name, percentage
            else:
                print("not list")

    def decision(self, resource=None, filename=None):
        """
        Makes a decision with a standard JSON Tradeoff-Analytics input.
        
        If filename exists, searches that file path first for a .json file.
        :param resource: the JSON itself, if not using filename
        :param filename: the filename for json to open.
        :return: 
        """

        # Assert that the user is giving us *something*.
        assert resource or filename

        # Testing only

        with open(os.path.join(os.path.dirname(__file__),
                               '../problem.json')) as problem_json:
            dilemma = self.decision_client.dilemmas(json.load(problem_json),
                                                  generate_visualization=True,
                                                  find_preferable_options=True)
            print(json.dumps(dilemma, indent=2))

    def single_reaction(self):
        """
        Returns a report relative to the log that just happened.
        :return: 
        """

        reaction = []

        for tone_id, score in self.tone_report(self.logs[-1]):
            reaction.append((tone_id, score))

        # Return highest magnitude of either tone or personality implied through the statement
        self.reaction = sorted(reaction, key=lambda t: t[1], reverse=True)


if __name__ == '__main__':
    main()
