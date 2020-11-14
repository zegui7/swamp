for i in $(seq 1 $(($(python3 mapping_the_swamp.py list | wc -l)-1)))
do 
    function retry { python3 getting_video_lists.py $i && echo "success" || (echo "fail" && retry) }; retry
done
