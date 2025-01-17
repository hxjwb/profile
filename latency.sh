python3 profile.py archive/webrtc_test > pace.log
python3 profile.py archive/ace_test > ace.log

python3 latency_serial.py ace.log pace.log --output_file serial.png
python3 latency_cdf.py ace.log pace.log --output_file cdf.png