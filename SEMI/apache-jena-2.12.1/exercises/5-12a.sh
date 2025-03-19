#!/bin/bash
mkdir new_database
bin/tdbloader2 --loc=new_database royal92/royal92.nt
bin/tdbquery --loc=new_database --query=exercises/5-10a.rq