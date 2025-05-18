import sys
import os
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__) + '/..'))

from extract_mod_ids import extract_mod_ids_from_metadata

def test_extract_single_mod_id():
    s = "Mod ID: MyCoolMod"
    assert extract_mod_ids_from_metadata(s) == ["MyCoolMod"]

def test_extract_multiple_mod_ids_semicolon():
    s = "ModIDs=ModA;ModB;ModC"
    result = extract_mod_ids_from_metadata(s)
    assert set(result) == {"ModA", "ModB", "ModC"}

def test_extract_multiple_mods_comma():
    s = "Mods=ModA,ModB,ModC"
    result = extract_mod_ids_from_metadata(s)
    assert set(result) == {"ModA", "ModB", "ModC"}

def test_extract_mod_id_bracket():
    s = '[mod id="SuperMod"]'
    assert extract_mod_ids_from_metadata(s) == ["SuperMod"]

def test_extract_mixed_patterns():
    s = '''Mod ID: X\nModIDs=Y;Z\n[mod id="W"]'''
    result = extract_mod_ids_from_metadata(s)
    assert set(result) == {"X", "Y", "Z", "W"}

def test_extract_ignores_noise():
    s = "This is a mod. Mod ID: Alpha. Not a mod: Beta. Mods=Gamma;Delta"
    result = extract_mod_ids_from_metadata(s)
    assert set(result) == {"Alpha", "Gamma", "Delta"}
