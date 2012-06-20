#!/bin/bash

export PYTHONPATH=../:$PYTHONPATH
export PY_ENV=test
nosetests test/*
