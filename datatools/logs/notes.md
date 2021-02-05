* for token, compute "noise factor":
  if this token is used in patterns, there will be more patterns.
  This factor would be the ratio of count(patterns with this token used)/(count patterns with this token unused)
  for lines with this token present.
  Idea is, that it's better to pick tokens with smaller noise factor.
  
* apply TF/IDF, seems similar to noise factor

* use FP-tree?

* when scattering, route by SeqSimHash (weighted how?), not by extracted pattern
* for centroid, compute SeqSimHash of extracted pattern?
