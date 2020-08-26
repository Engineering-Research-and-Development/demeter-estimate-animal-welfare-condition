# TEMPORARY MODULE FOR TESTING
import json
from Logger import log

class RandomForest:
  def execRFPrediction(self,a):
    print("CARICO JSON");
    b = json.loads(a);
    print(b);
    for item in b:
      item['Result'] = item['Arg1'] * item['Arg2']
    c = json.dumps(b,indent=2)
    print(c)
    return c