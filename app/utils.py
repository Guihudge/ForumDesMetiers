def convertjobsListToDict(jobsList):
    out = {}
    for j in jobsList:
        out[j.id] = j.Name
    
    return out
