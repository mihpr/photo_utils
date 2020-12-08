#!/usr/bin/env python
import os
import glob
import hashlib
import logging
import datetime
from tqdm import tqdm
from typing import Callable

BLOCK_SIZE = 8192


def get_algorithm_from_str(algorithm: str) -> Callable:
    """Returns function hashlib based on hash algorithm name.
    
    Args:
        algorithm: name of the algorithm, e.g., md5 or sha512.

    Returns:
        Function that computes hash.
    """
    if algorithm.lower() == "md5":
        return hashlib.md5
    elif algorithm.lower() == "sha1":
        return hashlib.sha1
    elif algorithm.lower() == "sha256":
        return hashlib.sha256
    elif algorithm.lower() == "sha512":
        return hashlib.sha512
    else:
        msg = f"{algorithm:s} not implemented."
        raise NotImplementedError(msg)


def compute_file_hash(filepath: str, algorithm: Callable) -> str:
    """Computes hash of a single file.
    
    Args:
        filepath: path of a file for which to compute hash.
        algorithm: function that computes hash.

    Returns:
        Hex value of hash.
    """
    if not os.path.exists(filepath):
        raise ValueError(f"{filepath:s} does not exist.")
    if os.path.isdir(filepath):
        raise ValueError(f"{filepath:s} is a directory.")

    assert os.path.isfile(filepath)

    hash = algorithm()
    with open(filepath, "rb") as f:
        while (block := f.read(BLOCK_SIZE)):
            hash.update(block)

    return hash.hexdigest()


def compute_hashes(glob_patterns: list[str],
                   recursive: bool = False,
                   algorithm: str = "sha512",
                   logger: logging.Logger = None) -> list[dict[str, str]]:
    """Computes hashes for all files matching pattern.
    
    Args:
        glob_pattern: compute hash for files matching this pattern.
        recursive: whether to match pattern recursively.
        algorithm: name of the algorithm, e.g., md5 or sha512.
        logger: logger instance.

    Returns:
        Hash values, of the form `[{"filepath": ..., "hash":, ...}, ...]`.
    """
    # Get filepaths of matching files and directories
    filepaths = []
    for glob_pattern in glob_patterns:
        filepath_matches = glob.glob(glob_pattern, recursive=recursive)

        if logger:
            n_files = len(filepath_matches)
            msg = (f"Added {n_files:d} files matching '{glob_pattern:s}'" +
                " recursively." if recursive else ".")
            logger.debug(msg)

        filepaths.extend(filepath_matches)
    filepaths = sorted(list(set(filepaths)))
    if logger:
        n_files = len(filepaths)
        logger.debug(f"Total number of files for computing hash: {n_files:d}.")
   

    # Infer algorithm
    algorithm = get_algorithm_from_str(algorithm)

    # Compute hashes for files, skipping directories
    hashes = []
    for filepath in tqdm(filepaths):
        if os.path.isfile(filepath):
            hash = compute_file_hash(filepath, algorithm)
            hashes.append({"filepath": filepath, "hash": hash})

            if logger:
                logger.debug(f"{filepath:s}: {hash:s}")
        else:
            if logger:
                logger.debug(f"{filepath:s} is not a file: skipping.")

    return hashes


def print_hashes(hashes: list[dict[str, str]], algorithm: str,
                 glob_pattern: str, recursive: bool,
                 logger: logging.Logger) -> None:
    """Writes hashes along with some metadata to file.
    
    Args:
    """
    local_time = str(datetime.datetime.now())
    utc_time = str(datetime.datetime.utcnow())
    print(f"# Generated on (local time): {local_time:s}")
    print(f"# Generated on (UTC):        {utc_time:s}")
    print(f"# Algorithm used:            {algorithm:s}")
    print(f"# Working directory:         {os.getcwd():s}")
    print(f"# Glob pattern:              {glob_pattern:s}")
    print(f"# Recursive:                 {str(recursive):s}")

    # Write to output file
    for file in hashes:
        path = os.path.normpath(file["filepath"])
        hash = file["hash"]
        print(f"{hash:s}  {path:s}")


def read_hashes(filepath: str) -> list[dict[str, str]]:
    """Reads hashes from files.
    
    Args:
        filepath: path to file with hashes.
    
    Returns:
        List of files with their hashes.
    """
    with open(filepath, "r") as f:
        lines = f.readlines()

    # Strip return characters
    lines = [line.strip() for line in lines]

    # Filter out commented lines
    lines = [line for line in lines if line[0] != "#"]

    # Split line into hash and filename
    hashes = [line.split(" ") for line in lines]
    hashes = [{"hash": hash[0], "filepath": hash[-1]} for hash in hashes]

    # Cover special cases:
    # https://www.gnu.org/software/coreutils/manual/coreutils.html#md5sum-invocation
    for hash in hashes:
        if hash["hash"][0] == "\\":
            raise NotImplementedError()
        if hash["filepath"] == "*":
            raise NotImplementedError()

    return hashes


def check_hashes(hashes: list[dict[str, str]],
                 algorithm: str = "sha512",
                 logger: logging.Logger = None) -> list[dict[str, str]]:
    """Checks whether hashsums from file match actual hashsums.
    
    Args:
        hashes: list of filepaths with corresponding hashes.
        algorithm: name of the algorithm, e.g., md5 or sha512.
        logger: logger instance.

    Returns:
        List of files and whether their hashes match.
    """
    # Infer algorithm
    algorithm = get_algorithm_from_str(algorithm)

    # Create report
    check_results = []
    for file in hashes:
        filepath = file["filepath"]
        old_hash = file["hash"]
        current_hash = compute_file_hash(filepath, algorithm)

        checksum_ok = old_hash == current_hash

        if logger:
            if checksum_ok:
                logger.info(f"{filepath:s}: checksum matches.")
            else:
                logger.warning(f"{filepath:s}: checksum does not match.")

        check_results.append({"filepath": filepath, "ok": checksum_ok})
    return check_results


def gen_report(check_results) -> str:
    ok_files = [file for file in check_results if file["ok"]]
    problem_files = [file for file in check_results if not file["ok"]]

    report = "Summary: "
    if len(problem_files) == 0:
        report += "no problems found."
    else:
        report += f"found {len(problem_files):d} file(s) with problems."
        report += "\n\n"
        report += "Files with NOT matching hashes:\n"
        report += "\n".join([file["filepath"] for file in problem_files])

    report += "\n\n"
    report += "Files with matching hashes:\n"
    report += "\n".join(sorted([file["filepath"] for file in ok_files]))

    return report
