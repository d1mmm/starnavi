import logging
import os
import sys
from alembic.config import CommandLine, Config

from starnavi.database.db import DATABASE_URL


def main():
    try:
        alembic = CommandLine()
        options = alembic.parser.parse_args()

        if not os.path.isabs(options.config):
            options.config = os.path.join(os.path.dirname(__file__), "..", options.config)

        config = Config(file_=options.config)

        config.set_main_option("sqlalchemy.url", DATABASE_URL)
        config.set_main_option("script_location", "alembinc")

        sys.exit(alembic.run_cmd(config, options))
    except Exception as e:
        logging.error(f"Alembic error {e}")


if __name__ == "__main__":
    main()
