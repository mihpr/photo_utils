import logging
import click
from .checksums import compute_hashes, print_hashes, read_hashes, check_hashes, gen_report


def get_logger_level_from_str(level=None):
    """Set up logger.
    
    Args:
        level: logging level: ERROR, WARNING, etc.
    
    Returns:
        Integer representing the log level.
    """
    if level is None:
        return level
    elif isinstance(level, int):
        return level
    elif isinstance(level, str):
        level = level.upper()
        if level == "CRITICAL":
            level = logging.CRITICAL
        elif level == "ERROR":
            level = logging.ERROR
        elif level == "WARNING":
            level = logging.WARNING
        elif level == "INFO":
            level = logging.INFO
        elif level == "DEBUG":
            level = logging.DEBUG
        elif level == "NOTSET":
            level = logging.NOTSET
        else:
            msg = ("If argument 'level' is string, it should be one of: " +
                   "CRITICAL, ERROR, WARNING, INFO, DEBUG, NOTSET.")
            raise ValueError(msg)
        return level
    else:
        msg = ("Argument 'level' should be int, string or None, while "
               f"{repr(type(level)):s} provided.")
        raise TypeError(msg)


@click.group()
def cli():
    return


@click.command()
@click.argument("glob_patterns",
                metavar="PATTERN1,PATTERN2",
                type=click.STRING)
@click.option("--algorithm",
              metavar="NAME",
              default="sha512",
              type=str,
              help="Hashing algorithm to use.")
@click.option("-r",
              "--recursive",
              is_flag=True,
              help="Traverse PATH recursively.")
@click.option("--log-level",
              metavar="LEVEL",
              default="info",
              type=str,
              help="Log level: DEBUG, INFO, WARNING, etc.")
@click.option("--log-file",
              metavar="PATH",
              default=None,
              type=str,
              help="Path to log file.")
def compute(glob_patterns, algorithm, recursive, log_level, log_file):
    """Computes hashes for all files matching a pattern."""
    # Set up logger
    format_str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    logging.basicConfig(format=format_str)

    logger = logging.getLogger("ComputeFileHashes")

    if log_level:
        log_level = get_logger_level_from_str(log_level)
        logger.setLevel(log_level)

    if log_file:
        fh = logging.FileHandler(log_file)
        fh.setFormatter(logging.Formatter(format_str))
        logger.addHandler(fh)
        fh.setLevel(logging.DEBUG)

    # Split glob patterns
    glob_patterns_str = glob_patterns
    glob_patterns = list(set(glob_patterns.split(",")))
    if len(glob_patterns) > 1:
        logger.info(f"Interpreting {glob_patterns_str:s} as " +
                    f"{len(glob_patterns):d} different glob patterns.")

    # Compute hashes
    hashes = compute_hashes(glob_patterns, recursive, algorithm, logger)

    # Print hashes to standard output
    print_hashes(hashes, algorithm, glob_patterns_str, recursive, logger)


@click.command()
@click.argument("checksums", type=click.Path(exists=True))
@click.option("--algorithm",
              metavar="NAME",
              default="sha512",
              type=str,
              help="Hashing algorithm to use.")
@click.option("--log-level",
              metavar="LEVEL",
              default="info",
              type=str,
              help="Log level: DEBUG, INFO, WARNING, etc.")
@click.option("--log-file",
              metavar="PATH",
              default=None,
              type=str,
              help="Path to log file.")
def check(checksums, algorithm, log_level, log_file):
    """Checks if file hashes match hashes from the previously generated file.
    
    Example usage:\n
    $ hashes check --algorithm sha512 log-level INFO .checksums.sha512 > report.txt
    """
    # Set up logger
    format_str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    logging.basicConfig(format=format_str)

    logger = logging.getLogger("ComputeFileHashes")

    if log_level:
        log_level = get_logger_level_from_str(log_level)
        logger.setLevel(log_level)

    if log_file:
        fh = logging.FileHandler(log_file)
        fh.setFormatter(logging.Formatter(format_str))
        logger.addHandler(fh)
        fh.setLevel(logging.DEBUG)

    hashes = read_hashes(".checksums.sha512")
    check_results = check_hashes(hashes, "sha512")
    report = gen_report(check_results)
    print(report)


cli.add_command(compute)
cli.add_command(check)

if __name__ == "__main__":
    cli()
