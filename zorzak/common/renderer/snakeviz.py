from zorzak.common.files import AnalysisFile


def render_with_snakeviz(pstats_file: AnalysisFile):
    return f"""
    # {pstats_file.name}

    Description: abcd
    """.strip()
