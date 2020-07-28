"""Simple AMPL Solver flask wrapper client
"""

__author__ = "John Eslick"

import requests
import logging
import sys
import os

_log = logging.getLogger("solver_flask_client")

handler = logging.StreamHandler(sys.stdout)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
_log.addHandler(handler)
_log.setLevel(logging.DEBUG)

if __name__ == "__main__":
    surl = "http://127.0.0.1:5000"
    solver = sys.argv[1]
    fname = sys.argv[2]
    args = sys.argv[3:]

    for i, a in enumerate(args):
        if a.startswith("url="):
            surl = a[4:]
            args.pop(i)
            break

    # get the file name and stub
    if not fname.endswith(".nl"):
        fname+=".nl"
    stub = fname[:-3]
    path = os.path.dirname(fname)
    # post the nl-file.
    r = requests.post(
        url=f"{surl}/new",
        files={'file': open(fname, 'rb')}
    )
    # get the solve job UID
    uid = r.text
    # log the job location in case you want to get more informaion
    _log.info(f"New session {uid}, to view or download files:")
    _log.info(f"  {surl}/view/{uid}/<file>")
    _log.info(f"  {surl}/download/{uid}/<file>")
    _log.info(r"    file in {stdout.log|stderr.log|problem.sol|problem.nl}")
    _log.info("Solving please hold...")
    r = requests.post(
        url=f"{surl}/solve",
        json={
            "id":uid,
            "solver":solver,
            "args":args
        }
    )
    returncode = int(r.text)
    _log.info(f"All done, solver returned {returncode}")
    r = requests.get(f"{surl}/download/{uid}/problem.sol")
    with open(stub+".sol", "w") as f:
        f.write(r.text)
    sys.exit(returncode)
