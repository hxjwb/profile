yuvPath=/mnt/md3/xiangjie/youtubevideos/evaluation_video/bathsong_coded.yuv

# single test
python3 kill_all.py
python3 run.py --file $yuvPath
# python3 mahi_serial.py logs
testName='ace_test'
# create if not exist
mkdir -p archive/$testName
cp logs/* archive/$testName/
python3 mahi_serial.py archive/$testName/


