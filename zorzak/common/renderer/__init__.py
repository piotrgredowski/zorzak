from .snakeviz import render_with_snakeviz


def get_renderers(*args, **kwargs):
    return (render_with_snakeviz,)
