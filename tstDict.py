matData = {}
for it in range(0,len(timeList),tSkip):
  if timeList[it] < tMin:
    continue
  if timeList[it] > tMax:
    break
  imat = 0
  for myMaterial in myHitMaterial.srcData:
    myMaterial = myHitMaterial.srcData[imat]
    imat = imat + 1
    matData[it,imat] = int(it)*1000 + imat
print matData

