"""Simple AMPL Solver flask wrapper
"""

__author__ = "John Eslick"

import logging
import uuid
import time
import subprocess
import json
import os
import sys

from flask import Flask, request, send_from_directory, Response

app_data = {
    "allowed_solvers":["ipopt", "petsc"],
    "max_proc":4,
    "procs":{}}

def new_session(f):
    uid = str(uuid.uuid4())
    root_path = os.path.join("data", uid)
    os.mkdir(path=root_path)
    f.save(os.path.join(root_path, "problem.nl"))
    return uid

def do_solve(uid, solver, args):
    root_path = os.path.join("data", uid)
    args2 = [solver, "-s", "problem"] + args
    if solver not in app_data["allowed_solvers"]:
        return None
    p = subprocess.Popen(
        args2,
        cwd=root_path,
        stderr=subprocess.PIPE,
        stdout=subprocess.PIPE)
    if p is None:
        return None
    fno = os.path.join(root_path, "stdout.log")
    fne = os.path.join(root_path, "stderr.log")
    with open(fno, "w") as fsout, open(fne, "w") as fserr:
        c1 = " "
        c2 = " "
        while c1 != "" or c2 !="":
            c1 = p.stdout.readline().decode()
            sys.stdout.write(c1)
            fsout.write(c1)
            c2 = p.stderr.readline().decode()
            sys.stderr.write(c2)
            fsout.write(c2)
    return p

def create_app():
    app = Flask(__name__)
    try:
        os.mkdir(path="data")
    except FileExistsError:
        pass

    @app.route('/new', methods=['POST'])
    def new():
        if request.method == 'POST':
            f = request.files['file']
            uid = new_session(f)
            return uid

    @app.route("/view/<uid>/<filename>", methods=["GET", "POST"])
    def download(uid, filename):
        root_path = os.path.join("data", uid)
        with open(os.path.join(root_path, filename)) as f:
            return Response(f.read(50000000), mimetype="text/plain")

    @app.route("/download/<uid>/<filename>", methods=["GET", "POST"])
    def view(uid, filename):
        root_path = os.path.join("data", uid)
        return send_from_directory(directory=root_path, filename=filename)

    @app.route("/solve", methods=["POST"])
    def solve():
        if request.method == "POST":
            uid = request.json["id"]
            slvr = request.json["solver"]
            args = request.json["args"]
        if slvr not in app_data["allowed_solvers"]:
            return "Solver not available"
        p = do_solve(uid, slvr, args)
        return str(p.poll())

    return app

if __name__ == "__main__":
    app = create_app()
    app.run()
