"""
After downloading each set of game scripts, I had to clean
them up game-by-game since the formatting was different.

After the cleanup process, the scripts are (mostly) consistent.

A blank line represents a break in scene or time.
Each line where someone is speaking is of the format:
Speaker:「Text being spoken」
Lines without ':' given contextual information or are sometimes
used for inner monologues, etc.
"""

import pathlib
from os.path import join

import utils
from cleanup import chrono_trigger
from cleanup import final_fantasy_6
from cleanup import final_fantasy_7
from cleanup import final_fantasy_8
from cleanup import final_fantasy_9
from cleanup import shining_force
from cleanup import super_mario_rpg


def cleanChronoTrigger(root):
    chronoTriggerRoot = join(root, "data", "chrono_trigger")
    chronoTriggerSrc = join(
        chronoTriggerRoot, "src", "chrono_trigger_japanese_script.txt"
    )
    chronoTriggerCleaned = join(chronoTriggerRoot, "cleaned")

    chrono_trigger.clean(chronoTriggerSrc, chronoTriggerCleaned)


def cleanFinalFantasy6(root):
    ff6Root = join(root, "data", "ff6")
    finalFantasy6Src = join(ff6Root, "src")
    finalFantasy6RenamedDir = join(ff6Root, "src_renamed")
    finalFantasy6Cleaned = join(ff6Root, "cleaned")

    utils.renameFilesWithLeadingNumbers(finalFantasy6Src, finalFantasy6RenamedDir)
    final_fantasy_6.clean(finalFantasy6RenamedDir, finalFantasy6Cleaned)


def cleanFinalFantasy7(root):
    ff7Root = join(root, "data", "ff7")
    finalFantasy7Src = join(ff7Root, "src")
    finalFantasy7RenamedDir = join(ff7Root, "src_renamed")
    finalFantasy7Cleaned = join(ff7Root, "cleaned")

    utils.renameFilesWithLeadingNumbers(finalFantasy7Src, finalFantasy7RenamedDir)
    final_fantasy_7.clean(finalFantasy7RenamedDir, finalFantasy7Cleaned)


def cleanFinalFantasy8(root):
    ff8Root = join(root, "data", "ff8")
    finalFantasy8Src = join(ff8Root, "src")
    finalFantasy8RenamedDir = join(ff8Root, "src_renamed")
    finalFantasy8Cleaned = join(ff8Root, "cleaned")

    utils.renameFilesWithLeadingNumbers(finalFantasy8Src, finalFantasy8RenamedDir)
    final_fantasy_8.clean(finalFantasy8RenamedDir, finalFantasy8Cleaned)


def cleanFinalFantasy9(root):
    ff9Root = join(root, "data", "ff9")
    finalFantasy9Src = join(ff9Root, "src")
    finalFantasy9RenamedDir = join(ff9Root, "src_renamed")
    finalFantasy9Cleaned = join(ff9Root, "cleaned")

    utils.renameFilesWithLeadingNumbers(finalFantasy9Src, finalFantasy9RenamedDir)
    final_fantasy_9.clean(finalFantasy9RenamedDir, finalFantasy9Cleaned)


def cleanSuperMarioRpg(root):
    superMarioRpgRoot = join(root, "data", "super_mario_rpg")
    superMarioRpgSrc = join(superMarioRpgRoot, "src", "super_mario_rpg_transcript.txt")
    superMarioRpgFilteredSrc = join(
        superMarioRpgRoot, "src", "super_mario_rpg_transcript_ja_new.txt"
    )
    superMarioRpgSegmented = join(superMarioRpgRoot, "segmented_tmp")
    # super_mario_rpg.removeAsciiFromText(superMarioRpgSrc, superMarioRpgFilteredSrc)
    # super_mario_rpg.splitFile(superMarioRpgFilteredSrc, superMarioRpgSegmented)

    # Manually inject location names into texts created in segmented_tmp
    # Then rename the folder 'segmented'
    # In hindsight, we could have injected the location names into the source in
    # the same way we split the file. Oh well.

    superMarioRpgSegmented = join(superMarioRpgRoot, "segmented")
    superMarioRpgCleaned = join(superMarioRpgRoot, "cleaned")
    super_mario_rpg.clean(superMarioRpgSegmented, superMarioRpgCleaned)


def cleanShiningForce3(root, scenario):
    shiningForceRoot = join(root, "data", scenario)
    shiningForceSrcDir = join(shiningForceRoot, "src")
    shiningForceRenamedDir = join(shiningForceRoot, "renamed_src")
    shiningForceCleaned = join(shiningForceRoot, "cleaned")

    utils.renameFilesWithLeadingNumbers(shiningForceSrcDir, shiningForceRenamedDir)
    shining_force.clean(shiningForceRenamedDir, shiningForceCleaned)


if __name__ == "__main__":
    _root = pathlib.Path(__file__).parent.absolute()
    # cleanChronoTrigger(_root)
    # cleanSuperMarioRpg(_root)

    # cleanFinalFantasy6(_root)
    # cleanFinalFantasy7(_root)
    # cleanFinalFantasy8(_root)
    cleanFinalFantasy9(_root)

    # cleanShiningForce3(_root, 'sf3s1')
    # cleanShiningForce3(_root, 'sf3s2')
    # cleanShiningForce3(_root, 'sf3s3')
