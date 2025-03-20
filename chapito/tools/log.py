import logging


def setup_logging_verbosity(verbosity):
    # Configurer le niveau de log en fonction de la verbosité
    if verbosity == 1:
        level = logging.WARNING
    elif verbosity == 2:
        level = logging.INFO
    elif verbosity >= 3:
        level = logging.DEBUG
    else:
        level = logging.ERROR

    logging.basicConfig(
        level=level, datefmt="%Y-%m-%d %H:%M:%S", format="[%(asctime)s] %(levelname)s: %(message)s", force=True
    )
