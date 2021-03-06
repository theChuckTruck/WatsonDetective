import json
from os.path import join, dirname
from watson_developer_cloud import PersonalityInsightsV2


personality_insights = PersonalityInsightsV2(
    username='4992907f-7c59-4405-953f-0fec302964f9',
    password='1b6mpATU3AEh')

with open(join(dirname(__file__), './MobyDick.txt')) as \
        personality_text:
    print(json.dumps(personality_insights.profile(
        text=personality_text.read()), indent=2))
#
# with open(join(dirname(__file__), './FDRSpeech')) as \
#         personality_text:
#     personality_insights_json = {"contentItems": [
#         {"id": "245160944223793152", "userid": "bob", "sourceid": "twitter",
#          "created": 1427720427, "updated": 1427720427,
#          "contenttype": "text/plain", "charset": "UTF-8",
#          "language": "en-us", "content": personality_text.read(),
#          "parentid": "", "reply": "false", "forward": "false"}]}
# print(json.dumps(personality_insights.profile(
#     text=personality_insights_json), indent=2))
#
# with open(join(dirname(__file__), '../resources/personality.es.txt')) as \
#         personality_text:
#     print(json.dumps(personality_insights.profile(
#         text=personality_text.read(), language='es'), indent=2))