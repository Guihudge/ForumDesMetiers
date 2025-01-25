from app.models import WhishList
from app import db
import sqlalchemy as sa
import random
from app.config import TIMES_SLOT
from app.km_matcher import KMMatcher
import numpy as np

#Config Section
NON_WHISH = 1000
ALREADY_ATTRIBUT = 1000000

def getJobsIdFromDictName(name:str) -> int:
    return int(name.split("-")[0])

def WhishObjectToList(w:WhishList|None, Jobs) -> list[int]:
    out = None
    if w is None:
        out = list(random.sample(Jobs, 5))
    else:
        out = (w.first, w.second, w.third, w.fourth, w.fifth)
    return out

def expandJobsList(jobs, studentPerJobs):
    jList = []
    for j in jobs:
        for i in range(studentPerJobs):
            jList.append(f"{j}-{i}")
    return jList


def generate_costMatrix(studentList, Jobs, jList, affectation):
    out = []
    
    for student in studentList:
        localOut = []
        w:list = WhishObjectToList(db.session.scalar(sa.select(WhishList).where(WhishList.id == student)),Jobs)
        for j in jList:
            try:
                i = w.index(getJobsIdFromDictName(j))
                if student in affectation and i in affectation[student]:
                    localOut.append(-ALREADY_ATTRIBUT)
                else:
                    localOut.append(-i)
            except ValueError:
                localOut.append(-NON_WHISH)
        
        out.append(localOut)
    return np.array(out)

def propagateResult(result, studentList, jList, affectation):
    for k in result.keys():
        student = studentList[k]
        job = getJobsIdFromDictName(jList[result[k]])
        if student in affectation:
            affectation[student].append(job)
        else:
            affectation[student] = [job]

def Repartition(jobsList, studentIDList, studentPerJobs):
    jList = expandJobsList(jobsList, studentPerJobs)
    affectation = {}
    for _ in TIMES_SLOT:
        d = generate_costMatrix(studentIDList, jobsList, jList, affectation)
        k = KMMatcher(d)
        s = k.solve()
        propagateResult(s, studentIDList, jList, affectation)
    return affectation