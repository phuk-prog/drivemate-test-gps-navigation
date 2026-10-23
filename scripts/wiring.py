"""Static integration guards. These supplement runtime tests; they do not render the UI."""
import argparse,json,re
from pathlib import Path

CHECKS = [
 ('uncertainty-state','controller/NavigationSession.kt',r'positionUncertain\s*=\s*positionUncertainty\.update\(now,\s*positionReliable\)'),
 ('uncertainty-notice','ui/MainScreen.kt',r'drivingNotice\(navigation\.rerouting,\s*vm\.positionUncertain,'),
 ('uncertainty-label','ui/MainScreen.kt',r'DrivingNotice\.GPS_ESTIMATE\s*->\s*"Position uncertain"'),
 ('cached-lanes-cleared','controller/NavigationSession.kt',r'if\s*\(!positionReliable\)\s*\{\s*guidanceFallback\.invalidate\(\)[\s\S]*?current\.copy\(lanes\s*=\s*emptyList\(\),\s*laneLabel\s*=\s*null,\s*junction\s*=\s*null\)'),
 ('spoken-lanes-gated','controller/NavigationSession.kt',r'if\s*\(!positionReliable\s*\|\|\s*!guidanceFallback\.lanesAllowed\)'),
 ('stale-fix-watchdog','controller/NavigationSession.kt',r'while\s*\(true\)\s*\{\s*updatePositionReliability\(\)\s*delay\(250\)'),
 ('automatic-recenter-gated','ui/MainScreen.kt',r'PositionCameraPolicy\.mayAutoRecenter\(navigation\.mode\s*==\s*Mode\.NAVIGATING,\s*following,\s*vm\.positionReliable\)'),
 ('recenter-rechecked-after-wait','ui/MainScreen.kt',r'delay\(10_000\)\s*if\s*\(!vm\.positionReliable\)\s*return@LaunchedEffect'),
 ('manual-pan-retains-view','ui/MainScreen.kt',r'map\.onTrackingDismissed\s*=\s*\{\s*following\s*=\s*false\s*centeredGeneration\s*=\s*vm\.mapOpenGeneration'),
 ('explicit-recenter-available','ui/MainScreen.kt',r'val\s+recenter\s*=\s*\{\s*following\s*=\s*true\s*map\.setFollow\(if\s*\(navigation\.mode\s*==\s*Mode\.NAVIGATING\)\s*Follow\.NAVIGATE\s*else\s*Follow\.BROWSE\)'),
 ('initial-view-retained','ui/MainScreen.kt',r'if\s*\(!com\.drivemate\.app\.nav\.PositionCameraPolicy\.mayInitiallyCenter\(centeredGeneration\s*>=\s*0,\s*vm\.positionReliable\)\)\s*return@LaunchedEffect'),
 ('gyro-event-connected','nav/MotionHeading.kt',r'Sensor\.TYPE_GYROSCOPE\s*->\s*estimator\.onGyro\(e\.timestamp,'),
 ('gravity-event-connected','nav/MotionHeading.kt',r'Sensor\.TYPE_GRAVITY\s*->\s*estimator\.onGravity\('),
 ('measured-heading-connected','controller/NavigationSession.kt',r'if\s*\(raw\.hasBearing\(\)\s*&&\s*raw\.accuracy\s*<=\s*25\)\s*motion\.onGps\(raw\.bearing,\s*raw\.speed\)'),
]

def uncomment(s):
    # Preserve quoted strings; comments cannot make a disconnected binding look present.
    token = r'"(?:\\.|[^"\\])*"|/\*[\s\S]*?\*/|//[^\n]*'
    return re.sub(token,lambda m: '' if m[0].startswith(('/',)) else m[0],s)

def inspect(app):
    root=Path(app)/'app/src/main/java/com/drivemate/app'
    results=[]
    for name,path,pattern in CHECKS:
        source=uncomment((root/path).read_text())
        matches=list(re.finditer(pattern,source))
        count=2 if name=='spoken-lanes-gated' else 1
        passed=len(matches)>=count
        # Delete the required bindings only in memory; the guard must detect their absence.
        broken=re.sub(pattern,'',source)
        mutation_detected=len(list(re.finditer(pattern,broken)))<count
        results.append({'id':name,'passed':passed,'disconnection_detected':mutation_detected})
    return {'scope':'static source integration guards, not UI rendering','checks':results,'passed':sum(x['passed'] for x in results),'total':len(results),'disconnections_detected':sum(x['disconnection_detected'] for x in results)}

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--app',required=True);p.add_argument('--out',required=True);a=p.parse_args()
    d=inspect(a.app);Path(a.out).parent.mkdir(parents=True,exist_ok=True);Path(a.out).write_text(json.dumps(d,indent=2)+'\n')
    print(json.dumps({k:v for k,v in d.items() if k!='checks'}))
    raise SystemExit(0 if d['passed']==d['total']==d['disconnections_detected'] else 1)
