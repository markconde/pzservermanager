import re


def extract_mod_ids_from_metadata(description_or_metadata):
    """
    Extracts mod IDs from a string containing mod metadata or description.
    Returns a list of mod IDs (strings).
    Handles common patterns like:
    - Mod ID: SomeMod
    - ModIDs=SomeMod;AnotherMod
    - Mods=SomeMod;AnotherMod
    - Mods=ModA,ModB,ModC
    - [mod id="SomeMod"]
    - etc.
    """
    mod_ids = set()
    # Pattern 1: Mod ID: SomeMod
    for match in re.findall(
        r"Mod ID[:=]\s*([\w\-]+)",
        description_or_metadata,
        re.IGNORECASE,
    ):
        mod_ids.add(match)
    # Pattern 2: ModIDs=SomeMod;AnotherMod or Mods=SomeMod;AnotherMod or Mods=ModA,ModB
    for match in re.findall(
        r"ModIDs?=([\w;\-, ]+)",
        description_or_metadata,
        re.IGNORECASE,
    ):
        for mod in re.split(r"[;,\s,]+", match):
            if mod:
                mod_ids.add(mod)
    # Pattern 2.1: Mods=ModA,ModB,ModC
    for match in re.findall(
        r"Mods?=([\w;,\-, ]+)",
        description_or_metadata,
        re.IGNORECASE,
    ):
        for mod in re.split(r"[;,\s,]+", match):
            if mod:
                mod_ids.add(mod)
    # Pattern 3: [mod id="SomeMod"]
    for match in re.findall(
        r"mod id=\"([\w\-]+)\"",
        description_or_metadata,
        re.IGNORECASE,
    ):
        mod_ids.add(match)
    # Pattern 4: Standalone mod names (optional, only if clearly labeled)
    # Add more patterns as needed for edge cases
    return list(mod_ids)
