from flask import Blueprint, render_template, abort, request, redirect, session, url_for, send_file
from flask_login import current_user, login_user, logout_user
from sqlalchemy import desc, or_, and_
from srht.objects import *
from srht.common import *
from srht.config import _cfg
from srht.email import send_invite, send_rejection

from datetime import datetime
import hashlib
import binascii
import os
import zipfile
import urllib
import re
import json
import locale
import shlex
import math
import base64

encoding = locale.getdefaultlocale()[1]
api = Blueprint('api', __name__, template_folder='../../templates')

@api.route("/api/approve/<id>", methods=["POST"])
@adminrequired
@with_session
@json_output
def approve(id):
    u = User.query.filter(User.id == id).first()
    u.approved = True
    u.approvalDate = datetime.now()
    db.commit()
    send_invite(u)
    return { "success": True }

@api.route("/api/reject/<id>", methods=["POST"])
@adminrequired
@with_session
@json_output
def reject(id):
    u = User.query.filter(User.id == id).first()
    u.rejected = True
    db.commit()
    send_rejection(u)
    return { "success": True }

@api.route("/api/resetkey", methods=["POST"])
@json_output
def reset_key():
    key = request.form.get('key')
    if not key:
        return { "error": "Maybe you should include the actual key, dumbass" }, 400
    user = User.query.filter(User.apiKey == key).first()
    if not user:
        return { "error": "API key not recognized" }, 403
    user.generate_api_key()
    db.commit()
    return { "key": user.apiKey }

@api.route("/api/uploads")
@json_output
def uploads():
    key = request.form.get('key') or request.headers.get('key')
    if not key:
        return { "error": "API key is required" }, 401
    user = User.query.filter(User.apiKey == key).first()
    if not user:
        return { "error": "API key not recognized" }, 403
    uploads = (Upload.query
            .filter(Upload.user_id == user.id, Upload.hidden == False)
            .order_by(Upload.created.desc()))
    return [u.json() for u in uploads]

@api.route("/api/upload", methods=["POST"])
@json_output
def upload():
    key = request.form.get('key')
    f = request.files.get('file')
    if not key:
        return { "error": "API key is required" }, 401
    if not f:
        return { "error": "File is required" }, 400
    user = User.query.filter(User.apiKey == key).first()
    if not user:
        return { "error": "API key not recognized" }, 403
    filename = ''.join(c for c in f.filename if c.isalnum() or c == '.')
    upload = Upload()
    upload.user = user
    upload.hash = get_hash(f)
    existing = Upload.query.filter(Upload.hash == upload.hash).first()
    if existing:
        return {
            "success": True,
            "hash": existing.hash,
            "shorthash": existing.shorthash,
            "url": file_link(existing.path)
        }
    len = 4
    shorthash = upload.hash[:len]
    while any(Upload.query.filter(Upload.shorthash == shorthash)):
        len += 1
        shorthash = upload.hash[:len]
    upload.shorthash = shorthash
    upload.path = os.path.join(upload.shorthash + "." + extension(filename))
    upload.original_name = f.filename

    f.seek(0)
    f.save(os.path.join(_cfg("storage"), upload.path))

    if not upload.shorthash:
        return {
            "success": False,
            "error": "Upload interrupted"
        }

    db.add(upload)
    db.commit()
    return {
        "success": True,
        "hash": upload.hash,
        "shorthash": upload.shorthash,
        "url": _cfg("protocol") + "://" + _cfg("domain") + "/" + upload.path
    }

@api.route("/api/disown", methods=["POST"])
@json_output
def disown():
    key = request.form.get('key')
    filename = request.form.get('filename')
    if not key:
        return { "error": "API key is required" }, 401
    if not filename:
        return { "error": "File is required" }, 400
    user = User.query.filter(User.apiKey == key).first()
    if not user:
        return { "error": "API key not recognized" }, 403
    Upload.query.filter_by(path=filename).first().hidden = True
    db.commit()
    return {
            "success": True,
            "filename": filename
    }

def get_hash(f):
    f.seek(0)
    return base64.urlsafe_b64encode(hashlib.md5(f.read()).digest()).decode("utf-8")

@api.route("/api/tox", methods=['POST'])
@json_output
def tox():
    key = request.form.get('key')
    tox_id = request.form.get('id')
    if not key:
        return { "error": "API key is required" }, 401
    if tox_id is None:
        return { "error": "Tox ID is required" }, 400
    user = User.query.filter(User.apiKey == key).first()
    if not user:
        return { "error": "API key not recognized" }, 403
    user.tox_id = tox_id
    db.commit()
    return {
        "success": True
    }

def extension(f):
    parts = f.rsplit('.', 2)
    # special case for .tar.* files
    if len(parts) > 2 and parts[-2].lower() == 'tar':
        return 'tar.' + parts[-1].lower()
    return parts[-1].lower()
