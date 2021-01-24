
import io
import json


from extract_dialogs_as_html import Builder, compileSections
import utils

class JsonBuilder(Builder):

    def cleanSpeech(self, speech):
        return speech.lstrip('＋＋').lstrip('○')

    def buildSection(self, textList, _sectionId):
        speechEvents = []
        speakerClass = None
        for _speechId, line in enumerate(textList):
            speaker, speech = self.splitSpeakerAndSpeech(line)
            if speaker == '' and len(speechEvents) > 0:
                speechEvents[-1]['speech'].append(self.cleanSpeech(speech))
            else:
                speakerClass = self.getSpeakerClass(speech, speaker, speakerClass)
                if speakerClass in [Builder.SPEAKER_A, Builder.SPEAKER_B]:
                    speakerClass = Builder.SPEAKER
                speechEvents.append({'speaker': speaker, 'speech': [self.cleanSpeech(speech)], 'type': speakerClass})

        return speechEvents

def extractDialogAsJson(rootDir, outputFn, builder, title, version):
    sectionNum = 0
    sectionsByFile = []
    for fn, fd in utils.loadFiles(rootDir):
        sections, sectionNum = compileSections(fd, builder, sectionNum)
        sectionsByFile.append({'source': fn, 'sections': sections})

    root = {'game_content': title, 'version': version, 'content': sectionsByFile}

    with io.open(outputFn, "w", encoding="utf-8") as fd:
        json.dump(root, fd, ensure_ascii=False)

if __name__ == "__main__":
    extractDialogAsJson('data/super_mario_rpg/cleaned', 'data/super_mario_rpg/super_mario_rpg.json', JsonBuilder(), 'Super Mario RPG', 1.0)

    extractDialogAsJson('data/chrono_trigger/cleaned', 'data/chrono_trigger/chrono_trigger.json', JsonBuilder(), 'Chrono Trigger', 1.0)

    extractDialogAsJson('data/ff6/cleaned', 'data/ff6/ff6.json', JsonBuilder(), 'Final Fantasy 6', 1.0)
    extractDialogAsJson('data/ff7/cleaned', 'data/ff7/ff7.json', JsonBuilder(), 'Final Fantasy 7', 1.0)
    extractDialogAsJson('data/ff8/cleaned', 'data/ff8/ff8.json', JsonBuilder(), 'Final Fantasy 8', 1.0)
    extractDialogAsJson('data/ff9/cleaned', 'data/ff9/ff9.json', JsonBuilder(), 'Final Fantasy 9', 1.0)

    extractDialogAsJson('data/sf3s1/cleaned', 'data/sf3s1/sf3s1.json', JsonBuilder(), 'Shining Force 3 (Scenario 1)', 1.0)
    extractDialogAsJson('data/sf3s2/cleaned', 'data/sf3s2/sf3s2.json', JsonBuilder(), 'Shining Force 3 (Scenario 2)', 1.0)
    extractDialogAsJson('data/sf3s3/cleaned', 'data/sf3s3/sf3s3.json', JsonBuilder(), 'Shining Force 3 (Scenario 3)', 1.0)
