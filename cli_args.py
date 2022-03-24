import argparse

def get_args():
    parser = argparse.ArgumentParser(
        description="Realiza acciones con las mallas (XML)"
    )
    parser.add_argument(
        "-e", "--extract", help="Para extraer los jobs", required=False,
        action="store_true"
    )
    parser.add_argument(
        "-a", "--accommodate", help="Para acomodar el xml", required=False,
        action="store_true"
    )
    parser.add_argument(
        "-c", "--check_sentry", help="Verificar los jobs de Sentry", required=False,
        action="store_true"
    )

    return parser.parse_args()
